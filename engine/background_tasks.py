import ee
from engine.data_fetcher import DataFetcher
from engine.recommender import Recommender
from db_utils import get_db
from datetime import datetime, timezone

def analyze_and_cache_plot(plot_id):
    """
    Background worker function that performs analysis on a given plot
    and caches the results directly into Firestore.
    """
    print(f"[Worker] Starting analysis for plot: {plot_id}")
    
    db = get_db()
    if not db:
        print("[Worker] Failed to get Firestore connection.")
        return

    try:
        plot_ref = db.collection('plots').document(plot_id)
        plot_doc = plot_ref.get()
        
        if not plot_doc.exists:
            print(f"[Worker] Plot {plot_id} not found.")
            return

        plot_data = plot_doc.to_dict()
        boundaries = plot_data.get('boundaries')

        if not boundaries:
            print(f"[Worker] Plot {plot_id} has no boundaries to analyze.")
            return

        # 1. Fetch EE data using full polygon coordinates
        # Need to format boundaries into EE expected format: list of [lng, lat]
        coords = []
        if isinstance(boundaries, list) and len(boundaries) > 0:
            if isinstance(boundaries[0], dict):
                # if boundaries are in {lat: ..., lng: ...} format from frontend
                coords = [[float(pt['lng']), float(pt['lat'])] for pt in boundaries]
            elif isinstance(boundaries[0], list) and len(boundaries[0]) == 2:
                # if boundaries are already [lat, lng]
                # EE needs [long, lat], switch them!
                coords = [[float(pt[1]), float(pt[0])] for pt in boundaries]

        if not coords:
            print(f"[Worker] Could not parse coordinates for plot {plot_id}")
            return

        # Close the loop to make it a valid polygon
        if coords[0] != coords[-1]:
            coords.append(coords[0])

        fetcher = DataFetcher()
        ee_data = fetcher.fetch_soil_data([coords])
        
        if not ee_data:
             print(f"[Worker] Failed to fetch EE telemetry for plot {plot_id}.")
             return

        # 2. Run through Recommender model
        recommender = Recommender()
        n = ee_data.get("N", 0)
        p = ee_data.get("P", 0)
        k = ee_data.get("K", 0)
        temp = ee_data.get("temperature", 25)
        humidity = ee_data.get("humidity", 65)
        soil_type = ee_data.get("soil_type", "Loamy")
        moisture = ee_data.get("soil_moisture", 35)

        # Get top 5 suggested crops for the bare soil
        suggested_crops = recommender.recommend_crops(n, p, k, temp, humidity, soil_type, moisture)

        # 3. Analyze any existing crops planted in this plot
        crops_ref = plot_ref.collection('crops').stream()
        crop_analysis = []
        for crop_doc in crops_ref:
            crop_data = crop_doc.to_dict()
            name = crop_data.get('name') or crop_data.get('cropName') or crop_data.get('crop_name')
            if name:
                fert_recs = recommender.get_fertilizer_recommendation(name, n, p, k)
                status = recommender.analyze_health_status(name, n, p, k)
                crop_analysis.append({
                    "id": crop_doc.id, # useful for frontend binding
                    "cropName": name,
                    "healthStatus": status,
                    "fertilizerRecommendations": fert_recs
                })
        
        # 4. Package the analysis payload
        analysis_payload = {
             "temperature": temp,
             "humidity": humidity,
             "soil_moisture": moisture,
             "N": n,
             "P": p,
             "K": k,
             "ph": ee_data.get("ph", 6.5),
             "soil_type": soil_type,
             "suggested_crops": suggested_crops,
             "crop_analysis": crop_analysis,
             "last_updated": datetime.now(timezone.utc).isoformat()
        }

        # 5. Cache it natively into the plot document
        plot_ref.update({
            "analysis": analysis_payload
        })
        
        print(f"[Worker] Successfully updated analysis cache for plot {plot_id}")

    except Exception as e:
        print(f"[Worker] Error analyzing plot {plot_id}: {e}")

def run_daily_refresh():
    """
    Scheduled job that forces a refresh on all existing plots.
    """
    print("[Cron] Starting daily Earth Engine refresh loop...")
    db = get_db()
    if not db:
        return
        
    plots = db.collection('plots').stream()
    for plot in plots:
        analyze_and_cache_plot(plot.id)
    
    print("[Cron] Finished daily Earth Engine refresh.")
