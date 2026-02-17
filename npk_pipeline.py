import ee

# -----------------------------------------
# INIT EARTH ENGINE
# -----------------------------------------
try:
    ee.Initialize(project="agrinetra-2b4be")
except:
    ee.Authenticate()
    ee.Initialize(project="agrinetra-2b4be")


# -----------------------------------------
# CREATE POLYGON
# -----------------------------------------
def get_geometry(coords):
    if coords[0] != coords[-1]:
        coords.append(coords[0])
    return ee.Geometry.Polygon([coords])


# -----------------------------------------
# FETCH DATA FROM ERA5-LAND
# -----------------------------------------
def fetch_all_values(coords, date):

    geom = get_geometry(coords)

    start = ee.Date(date).advance(-7, "day")
    end = ee.Date(date).advance(7, "day")

    dataset = (
        ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR")
        .filterBounds(geom)
        .filterDate(start, end)
    )

    if dataset.size().getInfo() == 0:
        return None

    image = dataset.mean()

    # -----------------------------
    # Temperature (Kelvin → Celsius)
    # -----------------------------
    temp = image.select("temperature_2m").subtract(273.15)

    # -----------------------------
    # Soil Moisture (surface)
    # -----------------------------
    moisture = image.select("volumetric_soil_water_layer_1")

    values = ee.Image.cat([temp.rename("temp"), moisture.rename("moisture")]) \
        .reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geom,
            scale=9000,
            bestEffort=True
        ).getInfo()

    if values["moisture"] is None:
        return None

    # --------------------------------
    # CONVERT TO MODEL INPUT FORMAT
    # --------------------------------
    return {
        "temperature": round(values["temp"], 2),
        "humidity": 65,   # constant placeholder
        "soil_moisture": round(values["moisture"] * 100, 2),

        # Estimated NPK values
        "N": round(values["moisture"] * 120, 2),
        "P": round(values["moisture"] * 60, 2),
        "K": round(values["moisture"] * 90, 2)
    }
