from flask import Blueprint, request, jsonify
import json
from db_utils import get_db

add_plot_bp = Blueprint('add_plot', __name__)

@add_plot_bp.route('/api/add_plot', methods=['POST'])
def add_plot():
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400

    plot_id = data.get('plotid')    # Document ID
    user_id = data.get('userid')    # Auth UID
    plot_name = data.get('plotname') 
    boundaries = data.get('boundaries') 

    if not all([plot_id, user_id, plot_name, boundaries]):
        return jsonify({"error": "Missing required fields: plotid, userid, plotname, boundaries"}), 400

    # Firestore can handle lists/dicts directly, no need to json.dumps
    if isinstance(boundaries, str):
        try:
            boundaries = json.loads(boundaries)
        except json.JSONDecodeError:
            pass # keep as string if not valid JSON

    db = get_db()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        # Save to Firestore: plots/{plot_id}
        doc_ref = db.collection('plots').document(plot_id)
        
        plot_data = {
            'pid': plot_id,
            'uid': user_id,
            'plotname': plot_name,
            'boundaries': boundaries
        }
        
        doc_ref.set(plot_data)
        
        print(f"Plot '{plot_name}' added successfully to Firestore for user '{user_id}'")
        return jsonify({"message": "Plot added successfully", "pid": plot_id}), 200

    except Exception as err:
        print(f"Database Error: {err}")
        return jsonify({"error": str(err)}), 500
