from flask import Blueprint, request, jsonify
import mysql.connector
import json
from db_config import db_config

fetch_plots_bp = Blueprint('fetch_plots', __name__)

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

@fetch_plots_bp.route('/api/fetch_plots', methods=['GET'])
def fetch_plots():
    user_id = request.args.get('userid')
    
    if not user_id:
        return jsonify({"error": "Missing userid parameter"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)
    
    try:
        sql = "SELECT pid, uid, plotname, boundaries FROM Plots WHERE uid = %s"
        cursor.execute(sql, (user_id,))
        plots = cursor.fetchall()
        
        # Parse boundaries JSON for client if needed, or send as string
        # Here we send as is (object if dictionary=True handles JSON types correctly usually, 
        # but mysql-connector might return string or json object depending on version. 
        # Let's ensure it's JSON combatible)
        
        for plot in plots:
            if isinstance(plot['boundaries'], str):
                try:
                    plot['boundaries'] = json.loads(plot['boundaries'])
                except:
                    pass # Keep as string if parsing fails
        
        return jsonify({"plots": plots}), 200

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return jsonify({"error": str(err)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
