
import mysql.connector
from db_config import db_config

def init_db():
    """
    Initializes the database and tables if they do not exist.
    """
    try:
        # 1. Connect to MySQL Server (check if DB exists)
        # We need to connect without a specific database first to check/create it
        config_no_db = db_config.copy()
        if 'database' in config_no_db:
            del config_no_db['database']
        
        conn = mysql.connector.connect(**config_no_db)
        cursor = conn.cursor()

        target_db = db_config.get('database', 'Agrinetra')

        # 2. Create Database if not exists
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {target_db}")
        print(f"[DB Init] Database '{target_db}' checked/created.")

        # 3. Connect to the specific database
        conn.database = target_db

        # 4. Create Tables
        # Plots Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `plots` (
          `pid` varchar(36) NOT NULL,
          `uid` varchar(255) DEFAULT NULL,
          `boundaries` json DEFAULT NULL,
          `plotname` varchar(20) DEFAULT NULL,
          PRIMARY KEY (`pid`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
        """)
        print("[DB Init] Table 'plots' checked/created.")

        # Crops Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `crops` (
          `pid` varchar(36) DEFAULT NULL,
          `cropname` varchar(20) DEFAULT NULL,
          `plantingdate` date DEFAULT NULL,
          `harvestdate` date DEFAULT NULL,
          KEY `pid` (`pid`),
          CONSTRAINT `crops_ibfk_1` FOREIGN KEY (`pid`) REFERENCES `plots` (`pid`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
        """)
        print("[DB Init] Table 'crops' checked/created.")

        cursor.close()
        conn.close()
        print("[DB Init] Initialization complete.")

    except mysql.connector.Error as err:
        print(f"[DB Init] Error: {err}")
