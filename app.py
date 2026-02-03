import ee

# -----------------------------------------
# Earth Engine Initialization
# -----------------------------------------
try:
    ee.Initialize(project="agrinetra-2b4be")
except Exception:
    ee.Authenticate()
    ee.Initialize(project="agrinetra-2b4be")


# -----------------------------------------
# Cloud Masking using SCL
# -----------------------------------------
def mask_s2_clouds(image):
    scl = image.select("SCL")
    mask = (
        scl.neq(3)   # cloud shadow
        .And(scl.neq(8))   # medium cloud
        .And(scl.neq(9))   # high cloud
        .And(scl.neq(10))  # cirrus
    )
    return image.updateMask(mask)


# -----------------------------------------
# NDVI + NDMI TIME SERIES FOR POLYGON
# -----------------------------------------
def get_timeseries_indices(polygon_coords, start_date, end_date):
    try:
        # Ensure polygon is closed
        if polygon_coords[0] != polygon_coords[-1]:
            polygon_coords.append(polygon_coords[0])

        geometry = ee.Geometry.Polygon([polygon_coords])

        collection = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(geometry)
            .filterDate(start_date, end_date)
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 60))
            .map(mask_s2_clouds)
            .sort("system:time_start")
        )

        if collection.size().getInfo() == 0:
            return {
                "status": "no_data",
                "message": "No Sentinel-2 images found"
            }

        # ---- Per-image computation ----
        def per_image(image):
            ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
            ndmi = image.normalizedDifference(["B8", "B11"]).rename("NDMI")

            stats = ee.Image.cat([ndvi, ndmi]).reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geometry,
                scale=10,
                maxPixels=1e9
            )

            return ee.Feature(None, {
                "date": ee.Date(image.get("system:time_start")).format("YYYY-MM-dd"),
                "NDVI": stats.get("NDVI"),
                "NDMI": stats.get("NDMI")
            })

        feature_collection = ee.FeatureCollection(collection.map(per_image))
        features = feature_collection.getInfo()["features"]

        # ---- Convert to Python-friendly format ----
        timeseries = []
        for f in features:
            props = f["properties"]
            if props["NDVI"] is not None:
                timeseries.append({
                    "date": props["date"],
                    "NDVI": round(props["NDVI"], 4),
                    "NDMI": round(props["NDMI"], 4)
                })

        # ---- Area calculation ----
        area_ha = geometry.area().getInfo() / 10000

        return {
            "status": "success",
            "area_hectares": round(area_ha, 3),
            "data_points": len(timeseries),
            "timeseries": timeseries
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
def detect_growth_stage(timeseries):
    if len(timeseries) < 3:
        return "Insufficient data"

    latest = timeseries[-1]["NDVI"]
    prev = timeseries[-2]["NDVI"]

    if latest < 0.2:
        return "Sowing / Bare soil"
    elif latest < 0.4:
        return "Early vegetative stage"
    elif latest < 0.6:
        if latest - prev < 0.01:
            return "Vegetative stage"
        else:
            return "Active growth stage"
    elif latest >= 0.6:
        return "Flowering / Peak growth"
    else:
        return "Maturity / Harvest stage"
    
    
def irrigation_by_stage(stage, stress_level):
    if stage == "Sowing / Bare soil":
        return "Light irrigation to ensure germination"
    if stage == "Early vegetative stage":
        return "Moderate irrigation every 2–3 days"
    if stage == "Vegetative stage":
        return "Regular irrigation every 2 days"
    if stage == "Active growth stage":
        return "High water demand – frequent irrigation"
    if stage == "Flowering / Peak growth":
        return "Critical irrigation stage – avoid moisture stress"
    if stage == "Maturity / Harvest stage":
        return "Reduce irrigation gradually"
    return "Monitor field conditions"
