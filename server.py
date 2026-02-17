from fastapi import FastAPI, Body
from npk_pipeline import fetch_all_values

app = FastAPI(
    title="AgriNetra Crop Prediction API",
    version="1.0"
)

@app.get("/")
def home():
    return {"message": "Backend running successfully"}


@app.post("/analyze-plot")
def analyze_plot(data: dict = Body(...)):

    coords = data.get("coordinates")
    date = data.get("date")

    if not coords or not date:
        return {"error": "coordinates and date required"}

    result = fetch_all_values(coords, date)

    if result is None:
        return {"error": "No data found for this area/date"}

    return {
        "status": "success",
        "data": result
    }
