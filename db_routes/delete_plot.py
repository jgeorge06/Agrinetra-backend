from flask import Blueprint, request, jsonify
from db_utils import get_db

delete_plot_bp = Blueprint('delete_plot', __name__)

@delete_plot_bp.route('/api/delete_plot', methods=['DELETE'])
def delete_plot():
    plot_id = request.args.get('plotid')
    user_id = request.args.get('userid')  # For validation
    
    if not plot_id:
        return jsonify({"error": "Missing Required Field: plotid"}), 400

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

        # In Firestore, deleting a document doesn't automatically delete its subcollections.
        # We must query and delete all crops inside the `crops` subcollection first.
        crops_ref = doc_ref.collection('crops')
        crop_docs = crops_ref.stream()
        
        batch = db.batch()
        count = 0
        for crop_doc in crop_docs:
            batch.delete(crop_doc.reference)
            count += 1
            # Commit batch every 500 ops (Firestore limit)
            if count == 500:
                batch.commit()
                batch = db.batch()
                count = 0
        
        # Commit any remaining crop deletions
        if count > 0:
            batch.commit()

        # Delete the plot document itself
        doc_ref.delete()
        
        print(f"Plot '{plot_id}' and all its nested crops deleted successfully from Firestore")
        return jsonify({"message": "Plot deleted successfully", "pid": plot_id}), 200

    except Exception as err:
        print(f"Database Error: {err}")
        return jsonify({"error": str(err)}), 500
