from flask import Blueprint, request, jsonify
import mysql.connector
from db_config import db_config

delete_plot_bp = Blueprint('delete_plot', __name__)

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

@delete_plot_bp.route('/api/delete_plot', methods=['DELETE'])
def delete_plot():
    # Expecting JSON body {"plotid": "..."} or query param
    # Using JSON body is cleaner for DELETE with payload, but sometimes query params are used. 
    # Let's support JSON body first as consistent with add_plot
    
    data = request.json
    plot_id = data.get('plotid') if data else None
    
    # Fallback to query param if not in body
    if not plot_id:
        plot_id = request.args.get('plotid')

    if not plot_id:
        return jsonify({"error": "Missing plotid"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor()
    
    try:
        # Check if plot exists (optional, but good for feedback)
        check_sql = "SELECT pid FROM Plots WHERE pid = %s"
        cursor.execute(check_sql, (plot_id,))
        if not cursor.fetchone():
             return jsonify({"error": "Plot not found"}), 404

        sql = "DELETE FROM Plots WHERE pid = %s"
        cursor.execute(sql, (plot_id,))
        conn.commit()
        
        return jsonify({"message": f"Plot {plot_id} deleted successfully"}), 200

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return jsonify({"error": str(err)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
