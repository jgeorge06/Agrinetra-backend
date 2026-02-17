from flask import Flask
from flask_cors import CORS
from db_routes.add_plot import add_plot_bp
from db_routes.fetch_plots import fetch_plots_bp
from db_routes.delete_plot import delete_plot_bp
from db_routes.edit_plot import edit_plot_bp
from db_routes.add_crop import add_crop_bp
from db_routes.fetch_crops import fetch_crops_bp
from db_routes.edit_crop import edit_crop_bp
from db_routes.delete_crop import delete_crop_bp
from db_routes.fetch_available_crops import fetch_available_crops_bp

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# Register Blueprints
app.register_blueprint(add_plot_bp)
app.register_blueprint(fetch_plots_bp)
app.register_blueprint(delete_plot_bp)
app.register_blueprint(edit_plot_bp)
app.register_blueprint(add_crop_bp)
app.register_blueprint(fetch_crops_bp)
app.register_blueprint(edit_crop_bp)
app.register_blueprint(delete_crop_bp)
app.register_blueprint(fetch_available_crops_bp)

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

    # Run on all interfaces to allow access from emulator/devices
    app.run(host='0.0.0.0', port=5000, debug=True)
