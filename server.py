from fastapi import FastAPI, Body
from npk_pipeline import fetch_all_values

app = FastAPI()


@app.get("/")
def home():
    return {"message": "AgriNetra backend running successfully"}


@app.post("/analyze-plot")
def analyze_plot(data: dict = Body(...)):

    coords = data.get("coordinates")
    date = data.get("date")

    if not coords or not date:
        return {"error": "Missing input"}

    result = fetch_all_values(coords, date)

    if result is None:
        return {"error": "Failed to fetch data"}

    return {"status": "success", "data": result}
