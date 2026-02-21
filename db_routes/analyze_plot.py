
from flask import Blueprint, request, jsonify
from engine.data_fetcher import DataFetcher
from engine.recommender import Recommender

analyze_plot_bp = Blueprint('analyze_plot', __name__)

# Initialize Engine Components
fetcher = DataFetcher()
recommender = Recommender()

@analyze_plot_bp.route('/analyze_plot', methods=['POST'])
def analyze_plot():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Extract data
        coords = data.get('coordinates') # Expecting list of list of [lon, lat]
        crop_name = data.get('crop_name') # Optional
        date_str = data.get('date') # Optional YYYY-MM-DD

        if not coords:
             return jsonify({"error": "Coordinates are required"}), 400

        # 1. Fetch Soil Data via Earth Engine
        soil_data = fetcher.fetch_soil_data(coords, date_str)
        
        if not soil_data:
            return jsonify({"error": "Failed to fetch soil data. Check Earth Engine connectivity."}), 500

        # Extract soil parameters
        n = soil_data.get('N', 0)
        p = soil_data.get('P', 0)
        k = soil_data.get('K', 0)
        temp = soil_data.get('temperature', 25)
        humidity = soil_data.get('humidity', 65)
        soil_type = soil_data.get('soil_type', 'Loamy')
        moisture = soil_data.get('soil_moisture', 35)

        # 2. Generate Recommendations
        # A. Fertilizer advice (if a specific crop is mentioned)
        fertilizer_recs = []
        health_status = "N/A"
        if crop_name:
            fertilizer_recs = recommender.get_fertilizer_recommendation(crop_name, n, p, k)
            health_status = recommender.analyze_health_status(crop_name, n, p, k)

        # B. Crop Suggestions (General suitability)
        suggested_crops = recommender.recommend_crops(n, p, k, temp, humidity, soil_type, moisture)

        # 3. Construct Response
        response = {
            "soil_health": soil_data,
            "crop_analysis": {
                "current_crop": crop_name,
                "health_status": health_status,
                "fertilizer_recommendations": fertilizer_recs
            },
            "suggested_crops": suggested_crops
        }

        return jsonify(response), 200

    except Exception as e:
        print(f"Analysis Error: {e}")
        return jsonify({"error": str(e)}), 500
