import ee

# Initialize (authentication already done)
ee.Initialize(project='agrinetra-2b4be')

# Simple test geometry
point = ee.Geometry.Point([76.5, 9.5])

# Load Sentinel-2 harmonized collection
collection = (
    ee.ImageCollection("COPERNICUS/S2_HARMONIZED")
    .filterDate("2019-08-01", "2019-09-01")
    .filterBounds(point)
    .sort("CLOUDY_PIXEL_PERCENTAGE")   # Prefer less cloud
)

image = collection.first()

# Safety check
if image is None:
    print("❌ No Sentinel-2 image found for this date and location.")
else:
    info = image.getInfo()
    print("✅ Image Loaded Successfully!")
    print("ID:", info["id"])
