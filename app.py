from flask import Flask, request, jsonify
from npk_pipeline import fetch_all_values

app = Flask(__name__)

print("Starting Flask server...")

@app.route("/")
def home():
    return {"message": "AgriNetra backend running successfully"}

@app.route("/analyze-plot", methods=["POST"])
def analyze_plot():
    try:
        data = request.get_json()

        coords = data.get("coordinates")
        date = data.get("date")

        if not coords or not date:
            return jsonify({"error": "Missing coordinates or date"}), 400

        result = fetch_all_values(coords, date)

        return jsonify({
            "status": "success",
            "data": result
        })

    except Exception as e:
        print("SERVER ERROR:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
