from flask import Blueprint, request, jsonify
import mysql.connector
import json
from db_config import db_config

edit_plot_bp = Blueprint('edit_plot', __name__)

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

@edit_plot_bp.route('/api/edit_plot', methods=['PUT'])
def edit_plot():
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400

    plot_id = data.get('plotid')
    new_name = data.get('plotname')
    new_boundaries = data.get('boundaries')

    if not plot_id:
        return jsonify({"error": "Missing plotid"}), 400
        
    if not new_name and not new_boundaries:
        return jsonify({"error": "Nothing to update (provide plotname or boundaries)"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor()
    
    try:
        # Build dynamic SQL
        updates = []
        values = []

        if new_name:
            updates.append("plotname = %s")
            values.append(new_name)
        
        if new_boundaries:
            if isinstance(new_boundaries, (dict, list)):
                boundaries_json = json.dumps(new_boundaries)
            else:
                boundaries_json = new_boundaries
            updates.append("boundaries = %s")
            values.append(boundaries_json)
            
        values.append(plot_id)
        
        sql = f"UPDATE Plots SET {', '.join(updates)} WHERE pid = %s"
        
        cursor.execute(sql, tuple(values))
        conn.commit()
        
        # Even if rowcount is 0, it might just mean no changes were needed. 
        # We consider this a success for the purpose of the app flow.
        return jsonify({"message": f"Plot {plot_id} updated successfully (or no changes needed)"}), 200

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return jsonify({"error": str(err)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
