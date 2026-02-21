import firebase_admin
from firebase_admin import credentials, firestore
import os

# Initialize Firestore DB (Singleton pattern)
_db = None

def init_db():
    """
    Initializes the Firebase Admin SDK using the generated service account key.
    """
    global _db
    
    if not firebase_admin._apps:
        try:
            # Look for the service account key in the same directory as this file
            base_dir = os.path.dirname(os.path.abspath(__file__))
            cred_path = os.path.join(base_dir, 'firebase-adminsdk.json')
            
            if not os.path.exists(cred_path):
                print(f"[DB Init] WARNING: firebase-adminsdk.json not found at {cred_path}")
                print("[DB Init] Firestore will fail to initialize. Please add the service account key.")
                return None
            
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("[DB Init] Firebase Admin SDK initialized successfully.")
            
        except Exception as e:
            print(f"[DB Init] Error initializing Firebase: {e}")
            return None
            
    if _db is None:
        _db = firestore.client()
        print("[DB Init] Firestore client created.")
        
    return _db

def get_db():
    """
    Returns the initialized Firestore client.
    """
    global _db
    if _db is not None:
        return _db
    return init_db()
