import ee

# ---------------- INIT ----------------
try:
    ee.Initialize()
except:
    ee.Authenticate()
    ee.Initialize()


# ---------------- SOIL CLASSIFIER ----------------
def classify_soil(sand, clay, oc):

    if sand is None or clay is None:
        return "Loamy"

    if sand > 60:
        return "Sandy"

    if clay > 40 and oc > 2:
        return "Black"

    if clay > 40:
        return "Clayey"

    if 30 <= sand <= 60 and 20 <= clay <= 40:
        return "Loamy"

    return "Red"


# ---------------- SAFE VALUE EXTRACT ----------------
def safe_get(value_dict):
    if not value_dict:
        return None
    return list(value_dict.values())[0]


# ---------------- MAIN FUNCTION ----------------
def fetch_all_values(coords, date):

    try:
        polygon = ee.Geometry.Polygon(coords)
        point = polygon.centroid()

        # ---------------- WEATHER ----------------
        weather = (
            ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR")
            .filterDate(date, ee.Date(date).advance(5, "day"))
            .first()
        )

        temp_val = safe_get(
            weather.select("temperature_2m")
            .reduceRegion(ee.Reducer.mean(), point, 1000)
            .getInfo()
        )

        # ---------------- SOIL MOISTURE ----------------
        smap = (
            ee.ImageCollection("NASA/SMAP/SPL4SMGP/007")
            .filterDate(date, ee.Date(date).advance(5, "day"))
            .first()
        )

        moisture_val = safe_get(
            smap.select("sm_surface")
            .reduceRegion(ee.Reducer.mean(), point, 1000)
            .getInfo()
        )

        # ---------------- SOIL TEXTURE ----------------
        sand_val = safe_get(
            ee.Image("projects/soilgrids-isric/sand_mean")
            .select("sand_0-5cm_mean")
            .reduceRegion(ee.Reducer.mean(), point, 250)
            .getInfo()
        )

        clay_val = safe_get(
            ee.Image("projects/soilgrids-isric/clay_mean")
            .select("clay_0-5cm_mean")
            .reduceRegion(ee.Reducer.mean(), point, 250)
            .getInfo()
        )

        oc_val = safe_get(
            ee.Image("projects/soilgrids-isric/soc_mean")
            .select("soc_0-5cm_mean")
            .reduceRegion(ee.Reducer.mean(), point, 250)
            .getInfo()
        )

        # ---------------- FALLBACK DEFAULTS ----------------
        if temp_val is None:
            temp_val = 300

        if moisture_val is None:
            moisture_val = 0.35

        if sand_val is None:
            sand_val = 40

        if clay_val is None:
            clay_val = 30

        if oc_val is None:
            oc_val = 20

        # ---------------- CLASSIFY SOIL ----------------
        soil_type = classify_soil(sand_val, clay_val, oc_val)

        # ---------------- FINAL OUTPUT ----------------
        return {
            "temperature": round(temp_val - 273, 2),
            "humidity": 65,
            "soil_moisture": round(moisture_val * 100, 2),
            "N": round(40 + sand_val / 5, 2),
            "P": round(20 + clay_val / 10, 2),
            "K": round(30 + oc_val / 10, 2),
            "soil_type": soil_type
        }

    except Exception as e:
        print("GEE ERROR:", e)
        return None
