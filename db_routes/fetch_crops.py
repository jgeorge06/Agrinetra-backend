from flask import Blueprint, request, jsonify
import mysql.connector
from db_config import db_config

fetch_crops_bp = Blueprint('fetch_crops', __name__)

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

@fetch_crops_bp.route('/api/fetch_crops', methods=['GET'])
def fetch_crops():
    plot_id = request.args.get('plotid')
    
    if not plot_id:
        return jsonify({"error": "Missing plotid parameter"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)
    
    try:
        sql = "SELECT pid, cropname, plantingdate, harvestdate FROM Crops WHERE pid = %s"
        cursor.execute(sql, (plot_id,))
        crops = cursor.fetchall()
        
        # Format dates to ISO 8601 string
        for crop in crops:
            if crop.get('plantingdate'):
                crop['plantingdate'] = str(crop['plantingdate'])
            if crop.get('harvestdate'):
                crop['harvestdate'] = str(crop['harvestdate'])

        return jsonify({"crops": crops}), 200

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return jsonify({"error": str(err)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
