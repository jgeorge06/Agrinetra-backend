from flask import Blueprint, request, jsonify
import mysql.connector
import json
from db_config import db_config

add_plot_bp = Blueprint('add_plot', __name__)

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

@add_plot_bp.route('/api/add_plot', methods=['POST'])
def add_plot():
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400

    plot_id = data.get('plotid')    # Maps to SQL 'pid'
    user_id = data.get('userid')    # Maps to SQL 'uid'
    plot_name = data.get('plotname') # Maps to SQL 'plotname'
    boundaries = data.get('boundaries') # Maps to SQL 'boundaries'

    if not all([plot_id, user_id, plot_name, boundaries]):
        return jsonify({"error": "Missing required fields: plotid, userid, plotname, boundaries"}), 400

    if isinstance(boundaries, (dict, list)):
        boundaries_json = json.dumps(boundaries)
    else:
        boundaries_json = boundaries

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor()
    
    try:
        sql = "INSERT INTO Plots (pid, uid, plotname, boundaries) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (plot_id, user_id, plot_name, boundaries_json))
        
        conn.commit()
        print(f"Plot '{plot_name}' added successfully for user '{user_id}'")
        return jsonify({"message": "Plot added successfully", "pid": plot_id}), 200

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return jsonify({"error": str(err)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
