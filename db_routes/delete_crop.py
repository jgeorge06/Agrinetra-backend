from flask import Blueprint, request, jsonify
import mysql.connector
from db_config import db_config

delete_crop_bp = Blueprint('delete_crop', __name__)

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

@delete_crop_bp.route('/api/delete_crop', methods=['DELETE'])
def delete_crop():
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400

    plot_id = data.get('plotid')
    crop_name = data.get('cropname')

    if not plot_id or not crop_name:
        return jsonify({"error": "Missing required fields: plotid, cropname"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor()
    
    try:
        sql = "DELETE FROM Crops WHERE pid = %s AND cropname = %s"
        cursor.execute(sql, (plot_id, crop_name))
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Crop not found"}), 404
            
        return jsonify({"message": f"Crop '{crop_name}' deleted successfully from plot '{plot_id}'"}), 200

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return jsonify({"error": str(err)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
