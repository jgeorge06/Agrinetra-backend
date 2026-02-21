from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from engine.background_tasks import run_daily_refresh
from engine.firestore_listeners import start_firestore_listeners
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
    return "Agrinetra MySQL Server (v2) is Running with Blueprints!"

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
