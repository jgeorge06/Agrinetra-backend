from flask import Blueprint, request, jsonify
from db_utils import get_db

fetch_crops_bp = Blueprint('fetch_crops', __name__)

@fetch_crops_bp.route('/api/fetch_crops', methods=['GET'])
def fetch_crops():
    plot_id = request.args.get('pid')
    
    if not plot_id:
        return jsonify({"error": "Missing pid parameter"}), 400

    db = get_db()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        # Get all crop documents nested under this plot
        crops_ref = db.collection('plots').document(plot_id).collection('crops')
        query = crops_ref.stream()
        
        crops = []
        for doc in query:
            crop_data = doc.to_dict()
            # Include the auto-generated Firestore document ID so the frontend can reference it for edits/deletes
            crop_data['id'] = doc.id 
            crops.append(crop_data)
            
        return jsonify({"crops": crops}), 200

    except Exception as err:
        print(f"Database Error: {err}")
        return jsonify({"error": str(err)}), 500
