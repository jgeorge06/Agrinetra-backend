from flask import Blueprint, request, jsonify
from db_utils import get_db

add_crop_bp = Blueprint('add_crop', __name__)

@add_crop_bp.route('/api/add_crop', methods=['POST'])
def add_crop():
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400

    plot_id = data.get('pid')          # Foreign Key to Plot Document
    crop_name = data.get('cropname')
    planting_date = data.get('plantingdate')
    harvest_date = data.get('harvestdate')

    if not all([plot_id, crop_name, planting_date, harvest_date]):
        return jsonify({"error": "Missing required fields"}), 400

    db = get_db()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        # Save nested within the corresponding Plot document's 'crops' subcollection
        # db.collection('plots').document(plot_id).collection('crops').add(...)
        
        # Verify the plot exists first to enforce referential integrity
        plot_ref = db.collection('plots').document(plot_id)
        if not plot_ref.get().exists:
            return jsonify({"error": f"Plot with pid {plot_id} does not exist"}), 404

        crop_data = {
            'cropname': crop_name,
            'plantingdate': planting_date,
            'harvestdate': harvest_date,
            'pid': plot_id # Keep the pid on the child for easier reverse querying if ever needed
        }
        
        # Auto-generate a document ID for the crop
        _, doc_ref = plot_ref.collection('crops').add(crop_data)
        
        print(f"Crop '{crop_name}' added successfully to plot '{plot_id}' in Firestore")
        
        return jsonify({
            "message": "Crop added successfully", 
            "pid": plot_id,
            "crop_id": doc_ref.id  
        }), 200

    except Exception as err:
        print(f"Database Error: {err}")
        return jsonify({"error": str(err)}), 500
