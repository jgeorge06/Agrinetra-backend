
import ee
from datetime import datetime, timedelta

class DataFetcher:
    def __init__(self):
        self._initialize_ee()

    def _initialize_ee(self):
        try:
            ee.Initialize(project='agrinetra-2b4be')
        except:
            try:
                ee.Authenticate()
                ee.Initialize(project='agrinetra-2b4be')
            except Exception as e:
                print(f"Earth Engine Initialization Failed: {e}")

    def safe_get(self, value_dict):
        if not value_dict:
            return None
        return list(value_dict.values())[0]

    def _get_latest_image_val(self, collection_id, band, reducer, geometry, scale, end_date):
        # Look back up to 6 months to find the latest available image
        # This prevents empty collection errors when data lags real-time
        start_date = end_date.advance(-6, 'month')
        col = ee.ImageCollection(collection_id).filterDate(start_date, end_date)
        latest_img = col.sort('system:time_start', False).first()
        val_dict = latest_img.select(band).reduceRegion(reducer, geometry, scale).getInfo()
        return self.safe_get(val_dict)

    def classify_soil(self, sand, clay, oc):
        if sand is None or clay is None: return "Loamy" # Default
        
        if sand > 60: return "Sandy"
        if clay > 40 and oc > 2: return "Black"
        if clay > 40: return "Clayey"
        if 30 <= sand <= 60 and 20 <= clay <= 40: return "Loamy"
        
        return "Red"

    def fetch_soil_data(self, coords, date_str=None):
        try:
            if not date_str:
                date_str = datetime.now().strftime('%Y-%m-%d')
            
            # Create Geometry
            polygon = ee.Geometry.Polygon(coords)
            point = polygon.centroid()
            
            # Dates
            start_date = ee.Date(date_str)
            end_date = start_date.advance(5, "day")

            # 1. Weather (ERA5)
            temp_kelvin = None
            try:
                temp_kelvin = self._get_latest_image_val(
                    "ECMWF/ERA5_LAND/DAILY_AGGR",
                    "temperature_2m",
                    ee.Reducer.mean(),
                    point,
                    1000,
                    end_date
                )
            except Exception as e:
                print(f"Weather fetch failed for {date_str}: {e}")

            # 2. Soil Moisture (NASA SMAP uses 008 now)
            moisture_raw = None
            try:
                moisture_raw = self._get_latest_image_val(
                    "NASA/SMAP/SPL4SMGP/008",
                    "sm_surface",
                    ee.Reducer.mean(),
                    point,
                    1000,
                    end_date
                )
            except Exception as e:
                print(f"Moisture fetch failed for {date_str}: {e}")

            # 3. Soil Texture (SoilGrids)
            sand = None
            clay = None
            oc = None
            try:
                sand = self.safe_get(
                    ee.Image("projects/soilgrids-isric/sand_mean")
                    .select("sand_0-5cm_mean")
                    .reduceRegion(ee.Reducer.mean(), point, 250)
                    .getInfo()
                )
                clay = self.safe_get(
                    ee.Image("projects/soilgrids-isric/clay_mean")
                    .select("clay_0-5cm_mean")
                    .reduceRegion(ee.Reducer.mean(), point, 250)
                    .getInfo()
                )
                oc = self.safe_get(
                    ee.Image("projects/soilgrids-isric/soc_mean")
                    .select("soc_0-5cm_mean")
                    .reduceRegion(ee.Reducer.mean(), point, 250)
                    .getInfo()
                )
            except Exception as e:
                print(f"Soil texture fetch failed: {e}")

            # Fallbacks and Conversions
            temp_c = round(temp_kelvin - 273.15, 2) if temp_kelvin else 25.0
            moisture_pct = round(moisture_raw * 100, 2) if moisture_raw else 35.0
            sand_val = sand if sand else 40
            clay_val = clay if clay else 30
            oc_val = oc if oc else 20

            # Derived Values (approximations based on soil composition)
            # Nitrogen ~ Sand (aeration)
            # Phosphorous ~ Clay (retention)
            # Potassium ~ Organic Carbon
            N_val = round(40 + sand_val / 5, 2)
            P_val = round(20 + clay_val / 10, 2)
            K_val = round(30 + oc_val / 10, 2)

            soil_type = self.classify_soil(sand_val, clay_val, oc_val)

            return {
                "temperature": temp_c,
                "humidity": 65, # ERA5 humidity calculation is complex, keeping hardcoded for now or fetch Dewpoint
                "soil_moisture": moisture_pct,
                "N": N_val,
                "P": P_val,
                "K": K_val,
                "ph": 6.5, # Placeholder, SoilGrids has pH but kept simple for now
                "soil_type": soil_type
            }

        except Exception as e:
            print(f"Data Fetch Error: {e}")
            return None
