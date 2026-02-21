from flask import Blueprint, request, jsonify
from db_utils import get_db

delete_crop_bp = Blueprint('delete_crop', __name__)

@delete_crop_bp.route('/api/delete_crop', methods=['DELETE'])
def delete_crop():
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400

    plot_id = data.get('plotid')     # corresponds to the parent plot document ID
    crop_name = data.get('cropname') # the name of the crop to delete

    if not plot_id or not crop_name:
        return jsonify({"error": "Missing required fields: plotid, cropname"}), 400

    db = get_db()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        # Reference the parent plot
        plot_ref = db.collection('plots').document(plot_id)
        if not plot_ref.get().exists:
            return jsonify({"error": "Parent plot not found"}), 404

        # Query the crops subcollection for the crop with this name
        crops_ref = plot_ref.collection('crops')
        query = crops_ref.where('cropname', '==', crop_name).stream()
        
        deleted_count = 0
        for doc in query:
            doc.reference.delete()
            deleted_count += 1
            
        if deleted_count == 0:
            return jsonify({"error": "Crop not found"}), 404
            
        return jsonify({"message": f"Crop '{crop_name}' deleted successfully from plot '{plot_id}'"}), 200

    except Exception as err:
        print(f"Database Error: {err}")
        return jsonify({"error": str(err)}), 500
