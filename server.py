from flask import Flask, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from background_tasks import run_daily_refresh
from firestore_listeners import start_firestore_listeners
import atexit


from flask_cors import CORS

app = Flask(__name__)
# CORS may no longer be required if there are no HTTP endpoints,
# but leaving it safe.
CORS(app)

# -------------------------------------------------
# Root Check
# -------------------------------------------------
@app.route('/')
def home():
    return "Agrinetra MySQL Server  is Running with Blueprints!"

# -------------------------------------------------
# Engine Endpoints
# -------------------------------------------------
from engine import AdvancedEngine

@app.route('/api/analyze_plot', methods=['POST'])
def analyze_plot():
    """
    Independent endpoint to trigger Advanced Engine.
    Expects json: {"boundaries": [[lng, lat], [lng, lat], ...]}
    """
    data = request.json
    coords = data.get('boundaries')
    if not coords:
        return jsonify({"error": "boundaries array of [lng, lat] coordinates is required"}), 400
        
    try:
        engine = AdvancedEngine()
        report = engine.generate_recommendations(coords)
        return jsonify({"status": "success", "data": report}), 200
    except Exception as e:
        print(f"[Engine Interface] Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Initialize Database
    from db_utils import init_db
    init_db()

    # Start Realtime Firestore Listeners
    listeners = start_firestore_listeners()

    # Start Background Scheduler for Daily Refresh
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=run_daily_refresh, trigger="interval", hours=24)
    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())

    # Run on all interfaces to allow access from emulator/devices
    # use_reloader=False prevents double-spawning threads during development
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
