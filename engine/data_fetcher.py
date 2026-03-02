import ee
import requests
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
                print(f"[Fetcher] Earth Engine Initialization Failed: {e}")

    def _calculate_centroid(self, coords):
        """Calculates the geometric centroid of a list of [lng, lat] coordinates."""
        if not coords:
            return 0, 0
        
        # In case the polygon is closed (last point == first point), omit the last point for pure centroid
        pts = coords[:-1] if coords[0] == coords[-1] and len(coords) > 1 else coords
        if not pts:
            pts = coords

        lngs = [pt[0] for pt in pts]
        lats = [pt[1] for pt in pts]
        return sum(lngs) / len(lngs), sum(lats) / len(lats)

    def fetch_forecast(self, coords):
        """Fetches 14-day weather forecast from Open-Meteo using the plot centroid."""
        lng, lat = self._calculate_centroid(coords)
        print(f"[Fetcher] Fetching Open-Meteo forecast for centroid [{lng:.4f}, {lat:.4f}]")
        
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,et0_fao_evapotranspiration&timezone=auto&forecast_days=14"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            json_data = resp.json()
            elevation = json_data.get('elevation', 0)
            data = json_data.get('daily', {})
            return {
                "elevation": elevation,
                "dates": data.get("time", []),
                "temp_max": data.get("temperature_2m_max", []),
                "temp_min": data.get("temperature_2m_min", []),
                "precip_sum_mm": data.get("precipitation_sum", []),
                "et0_mm": data.get("et0_fao_evapotranspiration", [])
            }
        except Exception as e:
            print(f"[Fetcher] Open-Meteo Fetch Error: {e}")
            return None

    def fetch_soil_properties(self, coords):
        """Fetches SoilGrids data from GEE regarding soil texture and organic carbon using plot centroid."""
        try:
            lng, lat = self._calculate_centroid(coords)
            print(f"[Fetcher] Fetching SoilGrids for centroid [{lng:.4f}, {lat:.4f}]")
            point = ee.Geometry.Point([lng, lat])
            
            def safe_get(val_dict):
                return list(val_dict.values())[0] if val_dict else None

            # Fetch sand, clay, soc, and ph at 0-5cm depth
            sand = safe_get(ee.Image("projects/soilgrids-isric/sand_mean").select("sand_0-5cm_mean").reduceRegion(ee.Reducer.mean(), point, 250).getInfo())
            clay = safe_get(ee.Image("projects/soilgrids-isric/clay_mean").select("clay_0-5cm_mean").reduceRegion(ee.Reducer.mean(), point, 250).getInfo())
            soc = safe_get(ee.Image("projects/soilgrids-isric/soc_mean").select("soc_0-5cm_mean").reduceRegion(ee.Reducer.mean(), point, 250).getInfo())
            ph = safe_get(ee.Image("projects/soilgrids-isric/phh2o_mean").select("phh2o_0-5cm_mean").reduceRegion(ee.Reducer.mean(), point, 250).getInfo())

            # Convert pH from phx10 to standard
            ph_standard = ph / 10.0 if ph else 6.5
            
            # Fetch soil moisture
            moisture_raw = None
            try:
                end_date = ee.Date(datetime.now().strftime('%Y-%m-%d'))
                start_date = end_date.advance(-6, 'month')
                col = ee.ImageCollection("NASA/SMAP/SPL4SMGP/008").filterDate(start_date, end_date)
                latest_img = col.sort('system:time_start', False).first()
                moisture_raw = safe_get(latest_img.select("sm_surface").reduceRegion(ee.Reducer.mean(), point, 1000).getInfo())
            except Exception as e:
                print(f"[Fetcher] Moisture fetch failed: {e}")
            
            if sand is None or clay is None or ph is None:
                return {
                    "is_arable": False,
                    "error": "Location is non-arable (e.g., Ocean, Glacier) or SoilGrids data is entirely missing for these coordinates. Cannot analyze without real soil properties."
                }
                
            if moisture_raw is None:
                raise Exception("SMAP surface moisture data is currently unavailable. Real local moisture data is strictly required for analysis.")
            
            moisture_pct = round(moisture_raw * 100, 2)
            
            return {
                "sand": round(sand / 10.0, 1) if sand is not None else 40.0,
                "clay": round(clay / 10.0, 1) if clay is not None else 30.0,
                "soc": round(soc / 100.0, 2) if soc is not None else 0.5, 
                "ph": ph_standard,
                "soil_moisture": moisture_pct,
                "is_arable": True
            }
        except Exception as e:
            print(f"[Fetcher] SoilGrids Fetch Error: {e}")
            return {"error": "Failed to fetch soil data from Google Earth Engine. Real data is required for analysis.", "is_arable": False}

    def fetch_historical_climate(self, coords):
        """Fetches average monthly temperature and precipitation from ERA5 for the current month and the next 5 months across the full polygon."""
        try:
            print(f"[Fetcher] Fetching ERA5 historical climate for polygon...")
            polygon = ee.Geometry.Polygon(coords)
            now = datetime.now()
            
            # We want to pull average temps for the next 6 months (including current)
            # ERA5 MONTHLY is historical, so we average past years for these specific months
            # To keep it fast, we'll just run 6 quick filter calculations natively
            monthly_forecasts = []
            # Use actively supported ERA5-Land monthly aggregates
            era5 = ee.ImageCollection("ECMWF/ERA5_LAND/MONTHLY_AGGR")
            
            for i in range(12):
                target_month = ((now.month - 1 + i) % 12) + 1
                month_col = era5.filter(ee.Filter.calendarRange(target_month, target_month, 'month'))
                mean_img = month_col.mean()
                
                val_dict = mean_img.select(['temperature_2m', 'total_precipitation_sum']).reduceRegion(
                    reducer=ee.Reducer.mean(),
                    geometry=polygon.buffer(10000),
                    scale=10000
                ).getInfo()
                
                temp_k = val_dict.get('temperature_2m')
                precip_m = val_dict.get('total_precipitation_sum')
                
                temp_c = round(temp_k - 273.15, 2) if temp_k else 25.0
                precip_mm = round(precip_m * 1000, 2) if precip_m else 100.0
                
                monthly_forecasts.append({
                    "month": target_month,
                    "avg_temp_c": temp_c,
                    "avg_precip_mm": precip_mm
                })
            
            return {
                "avg_temp_c": monthly_forecasts[0]["avg_temp_c"], # keep original signature valid
                "monthly_precip_mm": monthly_forecasts[0]["avg_precip_mm"],
                "twelve_month_outlook": monthly_forecasts
            }
        except Exception as e:
            print(f"[Fetcher] ERA5 Historical Fetch Error: {e}")
            
            # Dynamic Mathematical Fallback if GEE is unreachable
            # Instead of a flat 25.0°C everywhere, we approximate a realistic seasonal curve
            # based on planetary latitude tracking (Colder in winter, peak in summer).
            import math
            now = datetime.now()
            lng, lat = self._calculate_centroid(coords)
            
            is_northern = lat >= 0
            base_temp = max(5.0, 30.0 - abs(lat) * 0.4)
            amplitude = abs(lat) * 0.3
            
            monthly_forecasts = []
            for i in range(12):
                m = ((now.month - 1 + i) % 12) + 1
                phase_shift = (m - 7.0) / 12.0 * 2.0 * math.pi
                if is_northern:
                    sim_temp = base_temp + amplitude * math.cos(phase_shift)
                else:
                    sim_temp = base_temp - amplitude * math.cos(phase_shift)
                    
                monthly_forecasts.append({
                    "month": m,
                    "avg_temp_c": round(sim_temp, 1),
                    "avg_precip_mm": 100.0
                })
            return {"avg_temp_c": monthly_forecasts[0]["avg_temp_c"], "monthly_precip_mm": 100.0, "twelve_month_outlook": monthly_forecasts}

    def fetch_live_ndvi(self, coords):
        """Fetches the latest clear NDVI from Sentinel-2 or assesses persistent cloud cover."""
        try:
            print(f"[Fetcher] Fetching Sentinel-2 NDVI for polygon...")
            polygon = ee.Geometry.Polygon(coords)
            now = datetime.now()
            start_date = now - timedelta(days=45)
            
            # Sentinel-2 Surface Reflectance
            s2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
                .filterBounds(polygon) \
                .filterDate(start_date.strftime('%Y-%m-%d'), now.strftime('%Y-%m-%d'))
            
            # Count total images and extremely cloudy images
            total_images = s2.size().getInfo()
            if total_images > 0:
                very_cloudy_images = s2.filter(ee.Filter.gt('CLOUDY_PIXEL_PERCENTAGE', 80))
                cloudy_count = very_cloudy_images.size().getInfo()
                # If >80% of all passes were heavily obscured by clouds, it's very likely monsoon/wet season
                if (cloudy_count / total_images) > 0.8:
                    return {
                        "status": "cloudy_proxy",
                        "reason": f"Persistent thick cloud cover detected ({cloudy_count}/{total_images} passes >80% clouds). Assumed wet/active season."
                    }
                    
            # Try to find a clear image (< 20% clouds)
            clear_s2 = s2.filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) \
                .sort('system:time_start', False)
                
            if clear_s2.size().getInfo() == 0:
                return {
                    "status": "no_clear_data",
                    "reason": "No clear images (<20% clouds) in the last 45 days, but not persistently overcast enough to assume wet season."
                }
                
            latest_img = clear_s2.first()
            
            # Compute NDVI: (NIR - RED) / (NIR + RED)
            # Sentinel-2 Bands: B8 is NIR (10m), B4 is RED (10m)
            ndvi_img = latest_img.normalizedDifference(['B8', 'B4'])
            
            # Reduce over the polygon area
            mean_ndvi_dict = ndvi_img.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=polygon,
                scale=10,
                maxPixels=1e9
            ).getInfo()
            
            mean_ndvi = mean_ndvi_dict.get('nd')
            
            if mean_ndvi is None:
                 return {
                    "status": "error",
                    "reason": "NDVI reduction failed over polygon geometry."
                }
            
            date_ms = latest_img.get('system:time_start').getInfo()
            img_date = datetime.fromtimestamp(date_ms / 1000.0).strftime('%Y-%m-%d')
            
            return {
                "status": "success",
                "ndvi": round(mean_ndvi, 3),
                "date": img_date
            }
            
        except Exception as e:
            print(f"[Fetcher] Sentinel-2 NDVI Fetch Error: {e}")
            return {"status": "error", "reason": str(e)}

    def fetch_all(self, coords):
        """Aggregate all environmental data into a single payload."""
        return {
            "plot_geometry": coords,
            "forecast": self.fetch_forecast(coords),
            "soil": self.fetch_soil_properties(coords),
            "climate": self.fetch_historical_climate(coords),
            "ndvi": self.fetch_live_ndvi(coords)
        }
