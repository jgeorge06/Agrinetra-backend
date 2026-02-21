from flask import Blueprint, request, jsonify
from db_utils import get_db

fetch_plots_bp = Blueprint('fetch_plots', __name__)

@fetch_plots_bp.route('/api/fetch_plots', methods=['GET'])
def fetch_plots():
    user_id = request.args.get('userid')
    
    if not user_id:
        return jsonify({"error": "Missing userid parameter"}), 400

    db = get_db()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        # Query Firestore: SELECT * FROM plots WHERE uid = user_id
        plots_ref = db.collection('plots')
        query = plots_ref.where('uid', '==', user_id).stream()
        
        plots = []
        for doc in query:
            plot_data = doc.to_dict()
            # The client expects keys: pid, uid, plotname, boundaries
            # In Firestore, it's already stored in that structure!
            plots.append(plot_data)
        
        return jsonify({"plots": plots}), 200

    except Exception as err:
        print(f"Database Error: {err}")
        return jsonify({"error": str(err)}), 500
