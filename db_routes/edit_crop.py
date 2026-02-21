from flask import Blueprint, request, jsonify
from db_utils import get_db

edit_crop_bp = Blueprint('edit_crop', __name__)

@edit_crop_bp.route('/api/edit_crop', methods=['PUT'])
def edit_crop():
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400

    plot_id = data.get('plotid') # corresponds to the parent plot document ID
    old_crop_name = data.get('old_cropname') # Needed to identify which crop to edit
    
    new_crop_name = data.get('new_cropname')
    new_planting_date = data.get('plantingdate')
    new_harvest_date = data.get('harvestdate')

    if not plot_id or not old_crop_name:
        return jsonify({"error": "Missing identifiers: plotid and old_cropname are required"}), 400
        
    if not any([new_crop_name, new_planting_date, new_harvest_date]):
        return jsonify({"error": "Nothing to update"}), 400

    db = get_db()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        # Reference the parent plot
        plot_ref = db.collection('plots').document(plot_id)
        if not plot_ref.get().exists:
             return jsonify({"error": "Parent plot not found"}), 404

        # Query the crops subcollection for the crop with the old name
        crops_ref = plot_ref.collection('crops')
        query = crops_ref.where('cropname', '==', old_crop_name).stream()
        
        # Prepare updates
        update_data = {}
        if new_crop_name:
            update_data['cropname'] = new_crop_name
        if new_planting_date:
            update_data['plantingdate'] = new_planting_date
        if new_harvest_date:
            update_data['harvestdate'] = new_harvest_date

        updated_count = 0
        for doc in query:
            doc.reference.update(update_data)
            updated_count += 1
            
        if updated_count == 0:
            return jsonify({"message": "Crop not found or no changes needed"}), 200

        return jsonify({"message": f"Crop '{old_crop_name}' updated successfully"}), 200

    except Exception as err:
        print(f"Database Error: {err}")
        return jsonify({"error": str(err)}), 500
