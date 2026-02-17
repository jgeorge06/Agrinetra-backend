from flask import Blueprint, request, jsonify
import mysql.connector
from db_config import db_config

edit_crop_bp = Blueprint('edit_crop', __name__)

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

@edit_crop_bp.route('/api/edit_crop', methods=['PUT'])
def edit_crop():
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400

    plot_id = data.get('plotid')
    old_crop_name = data.get('old_cropname') # Needed to identify which crop to edit
    
    new_crop_name = data.get('new_cropname')
    new_planting_date = data.get('plantingdate')
    new_harvest_date = data.get('harvestdate')

    if not plot_id or not old_crop_name:
        return jsonify({"error": "Missing identifiers: plotid and old_cropname are required"}), 400
        
    if not any([new_crop_name, new_planting_date, new_harvest_date]):
        return jsonify({"error": "Nothing to update"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor()
    
    try:
        updates = []
        values = []

        if new_crop_name:
            updates.append("cropname = %s")
            values.append(new_crop_name)
        
        if new_planting_date:
            updates.append("plantingdate = %s")
            values.append(new_planting_date)
            
        if new_harvest_date:
            updates.append("harvestdate = %s")
            values.append(new_harvest_date)
            
        # WHERE clause values
        values.append(plot_id)
        values.append(old_crop_name)
        
        sql = f"UPDATE Crops SET {', '.join(updates)} WHERE pid = %s AND cropname = %s"
        
        cursor.execute(sql, tuple(values))
        conn.commit()
        
        # Even if rowcount is 0, it might just mean no changes were needed. 
        # We consider this a success for the purpose of the app flow.
        return jsonify({"message": "Crop updated successfully (or no changes needed)"}), 200

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return jsonify({"error": str(err)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
