from flask import Blueprint, request, jsonify
import mysql.connector
from db_config import db_config
from datetime import datetime

add_crop_bp = Blueprint('add_crop', __name__)

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

@add_crop_bp.route('/api/add_crop', methods=['POST'])
def add_crop():
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400

    plot_id = data.get('plotid') # Foreign Key
    crop_name = data.get('cropname')
    planting_date = data.get('plantingdate') # YYYY-MM-DD
    harvest_date = data.get('harvestdate')   # YYYY-MM-DD

    if not all([plot_id, crop_name, planting_date, harvest_date]):
        return jsonify({"error": "Missing required fields: plotid, cropname, plantingdate, harvestdate"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor()
    
    try:
        # Check if plot exists first (FK constraint)
        cursor.execute("SELECT pid FROM Plots WHERE pid = %s", (plot_id,))
        if not cursor.fetchone():
             return jsonify({"error": f"Plot {plot_id} does not exist"}), 404

        sql = "INSERT INTO Crops (pid, cropname, plantingdate, harvestdate) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (plot_id, crop_name, planting_date, harvest_date))
        
        conn.commit()
        return jsonify({"message": f"Crop '{crop_name}' added to plot '{plot_id}' successfully"}), 200

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return jsonify({"error": str(err)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
