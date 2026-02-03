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
# AOI Generator (Square around point)
# -----------------------------------------
def get_square_aoi(lat, lon, size_m):
    point = ee.Geometry.Point([lon, lat])
    return point.buffer(size_m / 2).bounds()


# -----------------------------------------
# Temperature from ERA5-Land (Celsius)
# -----------------------------------------
def get_temperature(aoi, date):
    start = ee.Date(date).advance(-15, "day")
    end = ee.Date(date).advance(15, "day")

    era5 = (
        ee.ImageCollection('ECMWF/ERA5_LAND/HOURLY')
        .filterBounds(aoi)
        .filterDate(start, end)
        .select('temperature_2m')
    )

    if era5.size().getInfo() == 0:
        return {"status": "no_data"}

    # Convert Kelvin to Celsius
    temp_c = era5.map(lambda img: img.subtract(273.15))

    # Take average over AOI and time period
    avg_temp = temp_c.mean().reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=aoi,
        scale=1000,
        maxPixels=1e9
    ).get('temperature_2m')

    return {"status": "success", "temperature_c": ee.Number(avg_temp).getInfo()}


# -----------------------------------------
# Soil Moisture
# -----------------------------------------
def get_soil_moisture(aoi, date):
    start = ee.Date(date).advance(-15, "day")
    end = ee.Date(date).advance(15, "day")

    smap = (
        ee.ImageCollection('NASA_USDA/HSL/SMAP10KM_soil_moisture')
        .filterBounds(aoi)
        .filterDate(start, end)
        .select('ssm')
    )

    if smap.size().getInfo() == 0:
        return {"status": "no_data"}

    avg_moisture = smap.mean().reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=aoi,
        scale=10000,
        maxPixels=1e9
    ).get('ssm')

    return {"status": "success", "soil_moisture": ee.Number(avg_moisture).getInfo()}


# -----------------------------------------
# Soil Type (Clay fraction)
# -----------------------------------------
def get_soil_type(aoi):
    try:
        soil = ee.Image('projects/soilgrids-isric/soilgrids/250m/texture')
        clay = soil.select('clay')
        avg_clay = clay.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=aoi,
            scale=250,
            maxPixels=1e9
        ).get('clay')
        return {"status": "success", "clay_fraction_percent": ee.Number(avg_clay).getInfo()}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# -----------------------------------------
# MAIN EXECUTION
# -----------------------------------------
if __name__ == "__main__":
    lat = 12.9716
    lon = 77.5946
    size_m = 500
    date = "2024-06-01"

    aoi = get_square_aoi(lat, lon, size_m)

    temperature = get_temperature(aoi, date)
    moisture = get_soil_moisture(aoi, date)
    soil_type = get_soil_type(aoi)

    output = {
        "input": {"latitude": lat, "longitude": lon, "area_size_m": size_m, "date": date},
        "temperature": temperature,
        "soil_moisture": moisture,
        "soil_type": soil_type
    }

    print("\nFINAL OUTPUT:")
    print(output)
