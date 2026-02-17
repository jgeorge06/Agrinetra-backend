from flask import Blueprint, jsonify

fetch_available_crops_bp = Blueprint('fetch_available_crops', __name__)

# This list can be dynamically loaded or expanded later
AVAILABLE_CROPS = [
    {"id": 1, "name": "Rice", "type": "Cereal"},
    {"id": 2, "name": "Wheat", "type": "Cereal"},
    {"id": 3, "name": "Sugarcane", "type": "Commercial"},
    {"id": 4, "name": "Cotton", "type": "Fiber"},
    {"id": 5, "name": "Maize", "type": "Cereal"},
    {"id": 6, "name": "Potato", "type": "Vegetable"},
    {"id": 7, "name": "Tomato", "type": "Vegetable"},
    {"id": 8, "name": "Onion", "type": "Vegetable"},
    {"id": 9, "name": "Soybean", "type": "Legume"},
    {"id": 10, "name": "Groundnut", "type": "Legume"}
]

@fetch_available_crops_bp.route('/api/available_crops', methods=['GET'])
def get_available_crops():
    return jsonify({"crops": AVAILABLE_CROPS}), 200
