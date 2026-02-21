from flask import Blueprint, request, jsonify
import json
from db_utils import get_db

edit_plot_bp = Blueprint('edit_plot', __name__)

@edit_plot_bp.route('/api/edit_plot', methods=['PUT'])
def edit_plot():
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400

    plot_id = data.get('plotid')     # required
    user_id = data.get('userid')     # optional, but good for validation
    plot_name = data.get('plotname') # optional update
    boundaries = data.get('boundaries') # optional update

    if not plot_id:
        return jsonify({"error": "Missing required field: plotid"}), 400

    db = get_db()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        doc_ref = db.collection('plots').document(plot_id)
        
        # Verify the plot exists and belongs to the user
        doc = doc_ref.get()
        if not doc.exists:
             return jsonify({"error": "Plot not found"}), 404
             
        if user_id and doc.to_dict().get("uid") != user_id:
             return jsonify({"error": "Unauthorized"}), 403

        # Prepare updates
        update_data = {}
        if plot_name is not None:
            update_data['plotname'] = plot_name
            
        if boundaries is not None:
            # Firestore can handle lists/dicts directly
            if isinstance(boundaries, str):
                try:
                    boundaries = json.loads(boundaries)
                except json.JSONDecodeError:
                    pass
            update_data['boundaries'] = boundaries

        if not update_data:
             return jsonify({"message": "No fields to update"}), 200

        doc_ref.update(update_data)
        
        print(f"Plot '{plot_id}' updated successfully in Firestore")
        return jsonify({"message": "Plot updated successfully", "pid": plot_id}), 200

    except Exception as err:
        print(f"Database Error: {err}")
        return jsonify({"error": str(err)}), 500
