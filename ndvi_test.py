import ee

# Initialize Earth Engine
ee.Initialize(project='agrinetra-2b4be')

# Test location & date
lat = 9.5
lon = 76.5
date = "2019-08-20"

point = ee.Geometry.Point([lon, lat])

start = ee.Date(date).advance(-3, "day")
end = ee.Date(date).advance(3, "day")

collection = (
    ee.ImageCollection("COPERNICUS/S2_HARMONIZED")
    .filterDate(start, end)
    .filterBounds(point)
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
)

print("Number of images:", collection.size().getInfo())

if collection.size().getInfo() > 0:
    image = collection.first()
    ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")

    ndvi_value = ndvi.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point,
        scale=10
    ).get("NDVI").getInfo()

    print("NDVI value:", ndvi_value)
else:
    print("No images found in date range")
