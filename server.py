import ee
from fastapi import FastAPI
from pydantic import BaseModel

# -----------------------------------------
# Earth Engine Init (ONCE)
# -----------------------------------------
try:
    ee.Initialize(project="agrinetra-2b4be")
except Exception:
    ee.Authenticate()
    ee.Initialize(project="agrinetra-2b4be")


# -----------------------------------------
# FASTAPI APP
# -----------------------------------------
app = FastAPI(title="AgriNetra Backend")


# -----------------------------------------
# INPUT MODEL
# -----------------------------------------
class InputData(BaseModel):
    lat: float
    lon: float
    size_m: int
    date: str


# -----------------------------------------
# AOI GENERATOR
# -----------------------------------------
def get_square_aoi(lat, lon, size_m):
    point = ee.Geometry.Point([lon, lat])
    return point.buffer(size_m / 2).bounds()


# -----------------------------------------
# CLOUD MASK
# -----------------------------------------
def mask_s2_clouds(image):
    scl = image.select("SCL")
    mask = (
        scl.neq(3)
        .And(scl.neq(8))
        .And(scl.neq(9))
        .And(scl.neq(10))
    )
    return image.updateMask(mask)


# -----------------------------------------
# NDVI
# -----------------------------------------
def get_ndvi_square(aoi, date):
    start = ee.Date(date).advance(-60, "day")
    end   = ee.Date(date).advance(60, "day")

    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(aoi)
        .filterDate(start, end)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 90))
        .map(mask_s2_clouds)
        .sort("CLOUDY_PIXEL_PERCENTAGE")
    )

    if collection.size().getInfo() == 0:
        return {"status": "no_data"}

    image = collection.first()
    ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")

    ndvi_val = ndvi.reduceRegion(
        ee.Reducer.mean(), aoi, 10, maxPixels=1e9
    ).get("NDVI")

    return {
        "status": "success",
        "ndvi": ee.Number(ndvi_val).getInfo()
    }


# -----------------------------------------
# SOIL NUTRIENTS
# -----------------------------------------
def get_soil_nutrients_square(aoi):
    nitrogen = ee.Image(
        "OpenLandMap/SOL/SOL_NITROGEN-USDA-6A1C_M/v02"
    ).select("b0")

    phosphorus = ee.Image(
        "OpenLandMap/SOL/SOL_P_USDA-4A1H_M/v02"
    ).select("b0")

    potassium = ee.Image(
        "OpenLandMap/SOL/SOL_K_USDA-4A1H_M/v02"
    ).select("b0")

    return {
        "nitrogen_g_per_kg": ee.Number(
            nitrogen.reduceRegion(
                ee.Reducer.mean(), aoi, 250, maxPixels=1e9
            ).get("b0")
        ).getInfo(),

        "phosphorus_mg_per_kg": ee.Number(
            phosphorus.reduceRegion(
                ee.Reducer.mean(), aoi, 250, maxPixels=1e9
            ).get("b0")
        ).getInfo(),

        "potassium_cmol_per_kg": ee.Number(
            potassium.reduceRegion(
                ee.Reducer.mean(), aoi, 250, maxPixels=1e9
            ).get("b0")
        ).getInfo()
    }


# -----------------------------------------
# 🔥 DIRECT OUTPUT ENDPOINT
# -----------------------------------------
@app.post("/analyze")
def analyze(data: InputData):

    aoi = get_square_aoi(data.lat, data.lon, data.size_m)

    return {
        "input": data.dict(),
        "ndvi": get_ndvi_square(aoi, data.date),
        "soil": get_soil_nutrients_square(aoi)
    }


# -----------------------------------------
# ROOT (OPTIONAL)
# -----------------------------------------
@app.get("/")
def root():
    return {"status": "AgriNetra API is running"}
