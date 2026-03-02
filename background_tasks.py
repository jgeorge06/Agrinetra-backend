import ee
from engine import AdvancedEngine
from db_utils import get_db
from datetime import datetime, timezone

def analyze_and_cache_plot(plot_id):
    """
    Background worker function that performs analysis on a given plot
    and caches the results directly into Firestore. Uses Engine primarily, 
    but still keeps legacy structure alive if needed.
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

        
        # --- NEW ENGINE INTEGRATION ---
        print(f"[Worker] Running Advanced Engine for plot {plot_id}...")
        engine = AdvancedEngine()
        
        # 2. Check for Hardware Sensor (Overrides GEE if present)
        sensor_data = None
        sensor_id = plot_data.get('sensor_id')
        if sensor_id:
            sensor_doc = db.collection('hardware_sensors').document(sensor_id).get()
            if sensor_doc.exists:
                sensor_data = sensor_doc.to_dict()
                print(f"[Worker] Plot {plot_id} uses Hardware Sensor {sensor_id}.")
        
        # Determine if there's a specific crop we should focus the analysis on
        # 1. Check if the Frontend attached the crop directly to the Plot document
        primary_crop = plot_data.get('cropName') or plot_data.get('crop_name') or plot_data.get('crop') or plot_data.get('name')
        if primary_crop: primary_crop = primary_crop.title()
        
        planting_date = plot_data.get('plantingdate') or plot_data.get('plantingDate') or plot_data.get('datePlanted') or plot_data.get('planted_date') or plot_data.get('plantingdate_start')
        harvest_date = plot_data.get('harvestdate') or plot_data.get('harvestDate') or plot_data.get('expectedHarvest') or plot_data.get('plantingdate_end') or plot_data.get('harvestdate_end')
        
        print(f"[Worker Debug] Top Level Extract - crop: {primary_crop}, start: {planting_date}, end: {harvest_date}")
        
        # 2. Check the subcollection if the main plot lacks explicit crop fields
        if not primary_crop:
            crops_ref = list(plot_ref.collection('crops').stream())
            print(f"[Worker Debug] Subcollection length: {len(crops_ref)}")
            if crops_ref:
                crop_data = crops_ref[0].to_dict()
                print(f"[Worker Debug] Subcollection Data: {crop_data}")
                primary_crop = crop_data.get('cropname') or crop_data.get('cropName') or crop_data.get('crop_name') or crop_data.get('name')
                if primary_crop: primary_crop = primary_crop.title()
                
                planting_date = crop_data.get('plantingdate_start') or crop_data.get('plantingdate') or crop_data.get('plantingDate') or crop_data.get('datePlanted') or crop_data.get('planted_date')
                harvest_date = crop_data.get('plantingdate_end') or crop_data.get('harvestdate_end') or crop_data.get('harvestdate') or crop_data.get('harvestDate') or crop_data.get('expectedHarvest')
                print(f"[Worker Debug] Subcollection Extract - crop: {primary_crop}, start: {planting_date}, end: {harvest_date}")

        # Generate the Engine Report
        engine_report = engine.generate_recommendations(
            coords, 
            primary_crop=primary_crop, 
            sensor_data=sensor_data, 
            planting_date=planting_date, 
            harvest_date=harvest_date
        )
        
        # 4. Package the analysis payload using the new structure
        analysis_payload = {
             "engine_report": engine_report, 
             "last_updated": datetime.now(timezone.utc).isoformat()
        }

        # 5. Cache it natively into the plot document
        plot_ref.update({
            "analysis": analysis_payload
        })
        
        print(f"[Worker] Successfully updated analysis cache for plot {plot_id} with Engine data.")

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
