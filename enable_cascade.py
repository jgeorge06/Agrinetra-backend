import mysql.connector
from db_config import db_config

def enable_cascade():
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        print("--- Finding Foreign Key Name ---")
        # Query `information_schema` to find the constraint name
        cursor.execute("""
            SELECT CONSTRAINT_NAME 
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
            WHERE TABLE_NAME = 'Crops' 
            AND COLUMN_NAME = 'pid' 
            AND TABLE_SCHEMA = DATABASE() 
            AND REFERENCED_TABLE_NAME IS NOT NULL
        """)
        
        row = cursor.fetchone()
        if not row:
            print("No Foreign Key found on Crops.pid. Creating new one...")
            # If no FK exists, just add it
            cursor.execute("""
                ALTER TABLE Crops
                ADD FOREIGN KEY (pid) REFERENCES Plots(pid) ON DELETE CASCADE
            """)
            print("Foreign Key added with CASCADE.")
        else:
            fk_name = row[0]
            print(f"Found Foreign Key: {fk_name}")
            
            # Drop the old FK
            print(f"Dropping FK {fk_name}...")
            cursor.execute(f"ALTER TABLE Crops DROP FOREIGN KEY {fk_name}")
            
            # Add new FK with CASCADE
            print("Adding new FK with ON DELETE CASCADE...")
            cursor.execute("""
                ALTER TABLE Crops
                ADD CONSTRAINT fk_crops_pid_cascade
                FOREIGN KEY (pid) REFERENCES Plots(pid) ON DELETE CASCADE
            """)
            print("Schema updated successfully.")

        conn.commit()

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    enable_cascade()
