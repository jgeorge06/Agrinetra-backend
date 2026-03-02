import math
import datetime
from .crop_db import CROP_DB, get_crop_requirements

class Analyzer:
    def __init__(self):
        pass
        
    def calculate_polygon_area_ha(self, coords):
        """Calculates precise Hectares using spherical excess area formula on lng/lat."""
        if not coords or len(coords) < 3:
            return 0.0
            
        EARTH_RADIUS = 6378137.0 # meters
        
        # Ensure closed polygon
        polygon = list(coords)
        if polygon[0] != polygon[-1]:
            polygon.append(polygon[0])
            
        area = 0.0
        # Calculate the average latitude to scale the longitudinal distances
        # (Since longitude lines converge at the poles)
        avg_lat = sum(p[1] for p in polygon) / len(polygon)
        lat_scale = math.cos(math.radians(avg_lat))
        
        # Shoelace formula on an equirectangular projection centered on the polygon
        for i in range(len(polygon) - 1):
            lon1, lat1 = polygon[i]
            lon2, lat2 = polygon[i+1]
            
            # Convert decimal degrees to meters
            # 1 degree of latitude is ~111,320 meters everywhere
            # 1 degree of longitude is ~111,320 * cos(lat) meters
            x1 = lon1 * 111320.0 * lat_scale
            y1 = lat1 * 111320.0
            x2 = lon2 * 111320.0 * lat_scale
            y2 = lat2 * 111320.0
            
            # Standard Shoelace
            area += (x1 * y2 - x2 * y1)
            
        area = abs(area) / 2.0
        return round(area / 10000.0, 4) # Convert sq meters to Hectares
        
    def classify_soil(self, sand, clay, soc, ph):
        """Simplistic soil classification based on SoilGrids composition (sand/clay), SOC, and pH."""
        if sand is None or clay is None: return "Loamy"
        
        # Laterite soil (Highly weathered, rich in iron/aluminum, acidic, heavily leached)
        # Typically found in tropical regions with heavy rainfall (Kerala, etc.)
        if ph is not None and ph < 5.8 and clay > 25:
            return "Laterite"
            
        # Black soil (Regur) - High clay, high moisture retention, rich in minerals
        if clay > 40 and soc > 1.5: 
            return "Black"
            
        # Sandy soil - High sand content, drains instantly
        if sand > 65: 
            return "Sandy"
            
        # Clayey soil - Heavy, poor drainage if not Black soil
        if clay > 45: 
            return "Clayey"
            
        # Red soil - Typically sandy-loam to clay-loam, slightly acidic to neutral, lower fertility
        if 40 <= sand <= 65 and ph is not None and ph < 6.8:
            return "Red"
            
        # Alluvial/Loamy - Highly fertile, balanced mixture, neutral pH
        if 30 <= sand <= 50 and 20 <= clay <= 30: 
            return "Alluvial"
            
        return "Loamy"

    def get_crop_suitability(self, env_data, temp_override=None, threshold=50):
        """Scores all crops dynamically based on Engine constraints."""
        soil = env_data.get("soil", {})
        climate = env_data.get("climate", {})
        forecast = env_data.get("forecast", {})
        
        avg_temp = temp_override if temp_override is not None else climate.get("avg_temp_c", 25.0)
        sand = soil.get("sand", 40)
        clay = soil.get("clay", 30)
        soc = soil.get("soc", 20)
        ph = soil.get("ph", 6.5)
        
        dominant_soil = self.classify_soil(sand, clay, soc, ph)
        
        results = []
        
        # Determine average weekly rainfall from forecast for flood risk
        precip_list = forecast.get('precip_sum_mm', []) if 'forecast' in env_data else []
        weekly_precip_current = sum(precip_list[:7]) if len(precip_list) >= 7 else sum(precip_list)
        
        # Determine total historical seasonal rainfall (ERA5 12-month curve)
        outlook = climate.get("twelve_month_outlook", [])
        
        # Elevation
        elevation = forecast.get("elevation", 0) if forecast else 0
        
        from datetime import datetime
        current_month = datetime.now().month

        for crop_name, req in CROP_DB.items():
            best_score = -1.0
            best_month = current_month
            
            # Start simulation from the current month to find the *soonest* optimal month in case of ties
            months_to_simulate = [(current_month + i - 1) % 12 + 1 for i in range(12)] if len(outlook) == 12 else [current_month]
            
            for m in months_to_simulate:
                score = 100.0
                
                if len(outlook) == 12:
                    # Average temp and sum precip over the growing season
                    months_needed = max(1, req.days_to_maturity // 30)
                    temp_sum = 0
                    precip_sum = 0
                    for i in range(months_needed):
                        target_m = ((m - 1 + i) % 12) + 1
                        m_data = next((om for om in outlook if om["month"] == target_m), {})
                        temp_sum += m_data.get("avg_temp_c", 25.0)
                        precip_sum += m_data.get("avg_precip_mm", 100.0)
                    
                    avg_temp = temp_sum / months_needed
                    season_precip = precip_sum
                    
                    # Estimate weekly precip for aridity/flood checks
                    if m == current_month:
                        weekly_precip = weekly_precip_current
                    else:
                        planting_m_data = next((om for om in outlook if om["month"] == m), {})
                        planting_month_precip = planting_m_data.get("avg_precip_mm", 100.0)
                        weekly_precip = planting_month_precip / 4.0
                else:
                    avg_temp = temp_override if temp_override is not None else climate.get("avg_temp_c", 25.0)
                    season_precip = sum([om.get("avg_precip_mm", 0) for om in climate.get("twelve_month_outlook", [])])
                    weekly_precip = weekly_precip_current
            
                # 1. Temperature Match (Weight 40%)
                if req.optimal_temp_min <= avg_temp <= req.optimal_temp_max:
                    pass # perfect
                elif req.absolute_temp_min <= avg_temp <= req.absolute_temp_max:
                    score -= 15 # acceptable but sub-optimal
                else:
                    score = 0 # KNOCKOUT: Crop cannot survive these extremes
                    continue
                    
                # 2. Soil Texture Match (Weight 30%)
                if dominant_soil in req.preferred_soil_types:
                    pass
                else:
                    score -= 30
                    
                # 3. pH Tolerance (Weight 15%)
                if req.ph_min <= ph <= req.ph_max:
                    pass
                else:
                    diff = min(abs(ph - req.ph_min), abs(ph - req.ph_max))
                    score -= min(15, diff * 10)
                    
                # 4. Water Availability/Drought & Flood Tolerance (Weight 15%)
                moisture = soil.get("soil_moisture", 30)
                
                # KNOCKOUT: Extreme Aridity (Desert conditions)
                if moisture < 10 and weekly_precip < 5:
                    if not getattr(req, 'tolerant_to_drought', False):
                        score = 0
                        continue
                # PENALTY: High Aridity (Semi-Arid/Dry conditions)
                elif moisture < 15 and weekly_precip < 10:
                    if not getattr(req, 'tolerant_to_drought', False):
                        score -= 80
                
                # If forecasting extremely heavy rain (>100mm/week) and crop isn't flood tolerant
                if weekly_precip > 100 and not getattr(req, 'tolerant_to_waterlogging', False):
                    score -= 20
                elif getattr(req, 'tolerant_to_waterlogging', False) and weekly_precip > 100:
                    score += 5 # Bonus for thriving in wet conditions (e.g., Rice)
                    
                # PENALTY: Seasonal Rainfall Exceedance (e.g., planning Cotton right before Indian Monsoons)
                # Exempt trees, as they survive for decades and naturally weather annual monsoons.
                if season_precip > (req.water_reqs_mm_season * 1.3) and not getattr(req, 'tolerant_to_waterlogging', False) and not getattr(req, 'is_tree_crop', False):
                    score -= 30
                # PENALTY: Seasonal Rainfall Deficit
                # If natural rainfall provides less than 70% of base requirement, strongly penalize unless drought tolerant
                elif req.water_reqs_mm_season > 0 and season_precip < (req.water_reqs_mm_season * 0.70):
                    if not getattr(req, 'tolerant_to_drought', False) and not getattr(req, 'is_tree_crop', False):
                        deficit_ratio = season_precip / req.water_reqs_mm_season
                        score -= (0.70 - deficit_ratio) * 100
                    
                # 5. Altitude Match (Weight: Modifying Penalty or Knockout)
                if hasattr(req, 'optimal_altitude_min') and hasattr(req, 'optimal_altitude_max'):
                    if req.optimal_altitude_min <= elevation <= req.optimal_altitude_max:
                        pass
                    elif elevation < req.optimal_altitude_min - 500 or elevation > req.optimal_altitude_max + 500:
                        score = 0 # KNOCKOUT: Fundamentally incompatible altitude (e.g., Apples at sea level)
                        continue
                    else:
                        score -= 15 # Sub-optimal altitude penalty
                    
                if score > best_score:
                    best_score = score
                    best_month = m
                    
            if best_score >= threshold:
                results.append({
                    "crop": crop_name,
                    "score": round(best_score, 1),
                    "optimal_planting_month": best_month
                })
            
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Determine paired intercrop immediately for each crop
        for res in results:
            name = res["crop"]
            req = CROP_DB.get(name)
            
            intercrops = []
            if req and req.compatible_intercrops:
                # Find the scores of those intercrops to see if they are viable here too
                for partner in req.compatible_intercrops:
                    partner_res = next((r for r in results if r["crop"] == partner), None)
                    if partner_res and partner_res["score"] >= 70:
                        intercrops.append({"crop": partner, "score": partner_res["score"]})
                        
            res["viable_intercrops"] = intercrops
            
        return results

    def calculate_fertilizer(self, crop_name, soil, area_ha=None):
        """Calculates specific fertilizer deficit based on soil organic carbon and crop demand."""
        req = get_crop_requirements(crop_name)
        if not req: return []
        
        sand = soil.get("sand", 40)
        clay = soil.get("clay", 30)
        soc = soil.get("soc", 20) # organic carbon dg/kg
        
        # Approximate baseline soil nutrients (kg/ha)
        # Deeply simplistic agronomical correlation for demonstration
        soil_n = 40 + (soc / 2) 
        soil_p = 20 + (clay / 2)
        soil_k = 30 + (soc / 3)
        
        deficit_n = max(0, req.n_req_kg_per_ha - soil_n)
        deficit_p = max(0, req.p_req_kg_per_ha - soil_p)
        deficit_k = max(0, req.k_req_kg_per_ha - soil_k)
        
        recommendations = []
        
        def format_rec(nutrient_name, deficit_ha, example):
            base_str = f"{round(deficit_ha)} kg/ha {nutrient_name} ({example})"
            if area_ha and area_ha > 0:
                total_kg = round(deficit_ha * area_ha)
                base_str += f" Plot Total: {total_kg} kg"
            return "Apply " + base_str

        if deficit_n > 20: recommendations.append(format_rec("Nitrogen", deficit_n, "e.g., Urea"))
        if deficit_p > 10: recommendations.append(format_rec("Phosphorous", deficit_p, "e.g., DAP/SSP"))
        if deficit_k > 10: recommendations.append(format_rec("Potassium", deficit_k, "e.g., MOP"))
        
        if not recommendations:
            recommendations.append("Soil is incredibly healthy for this crop! No major fertilizers required.")
            
        return recommendations

    def calculate_irrigation(self, crop_name, env_data, area_ha=None, days_since_planting=None):
        """Calculates 7-day irrigation schedule using Open-Meteo precipitation vs evapotranspiration, considering live NDVI and crop stages."""
        req = get_crop_requirements(crop_name)
        if not req: return {}
        
        # Fast exit for robust/wild crops that are exclusively rainfed
        # A crop might be rainfed immediately (e.g. Millets, 0 days) or after 3 years (e.g. Rubber, 1095 days)
        rainfed_after_days = getattr(req, 'rainfed_after_days', -1)
        
        # If the user didn't provide a date, assume it's a sapling/seedling (0 days) so we don't accidentally starve it.
        dsp = days_since_planting if days_since_planting is not None else 0
        
        if rainfed_after_days != -1 and dsp >= rainfed_after_days:
            if rainfed_after_days > 0:
                advice = f"{crop_name} has reached its mature established stage (> {rainfed_after_days} days old) and is primarily maintained as a rainfed crop. Manual irrigation is no longer considered necessary."
            else:
                advice = f"{crop_name} is a hardy dryland crop cultivated under rainfed conditions. Manual irrigation is not typically required."
                
            return {
                "status": "Rainfed System",
                "advice": advice,
                "deficit_mm": 0,
                "etc_mm": 0,
                "precip_mm": 0
            }
        
        forecast = env_data.get("forecast", {})
        soil = env_data.get("soil", {})
        if not forecast: return "Unable to calculate without forecast."
        
        
        precip_list = forecast.get('precip_sum_mm', [])
        et0_list = forecast.get('et0_mm', [])
        
        # Handle cases where arrays are shorter than 7 days
        days = min(7, len(precip_list), len(et0_list))
        if days == 0:
            return "Forecast data invalid."
            
        precip_7d = sum(precip_list[:days])
        et0_7d = sum(et0_list[:days])
        
        # 1. Determine Crop Coefficient (Kc) based on rough growth stage
        if days_since_planting is None:
            # Assuming we are mid-season for demonstration purposes if no date is provided.
            days_since_planting = req.days_to_maturity / 2 
            
        stage = "Unknown"
        kc = req.kc_mid
        
        # Check if crop is a mature perennial/tree
        is_mature_perennial = (getattr(req, 'is_tree_crop', False) or getattr(req, 'has_multiple_harvests', False)) and (days_since_planting >= req.days_to_maturity)
        
        if is_mature_perennial:
            # Mature perennials (like Rubber/Apples) operate on a cyclical calendar rather than linear age.
            current_month = datetime.datetime.now().month
            is_tropical = req.optimal_temp_max > 30 and not req.frost_tolerant
            
            # --- LIVE NDVI SATELLITE INTEGRATION ---
            ndvi_data = env_data.get("ndvi", {})
            ndvi_status = ndvi_data.get("status")
            
            if ndvi_status == "success" and ndvi_data.get("ndvi") is not None:
                live_ndvi = ndvi_data.get("ndvi")
                # NDVI < 0.35 indicates brown/bare branches (leaf shedding)
                if live_ndvi < 0.35:
                    kc = req.kc_initial
                    stage = f"Dormant / Leaf-Shedding (Live Satellite NDVI: {live_ndvi})"
                else:
                    kc = req.kc_mid
                    stage = f"Mature Canopy Active (Live Satellite NDVI: {live_ndvi})"
                    
            elif ndvi_status == "cloudy_proxy":
                # User Insight: If the satellite has been completely blocked by clouds for 45 days,
                # it is highly indicative of an active wet/monsoon season, meaning the tree has its leaves.
                # We bypass the calendar heuristic and assume active canopy.
                kc = req.kc_mid
                stage = "Mature Canopy Active (Assumed via Persistent Cloud Proxy)"
                
            else:
                # --- CALENDAR HEURISTIC FALLBACK ---
                # Only used if API fails or images are missing but not persistently cloudy
                if is_tropical and current_month in [2, 3]: # e.g., Rubber "Wintering" where it sheds leaves
                    kc = req.kc_initial # Very low demand without leaves
                    stage = "Dormant / Leaf-Shedding (Predicted Calendar Fallback)"
                elif not is_tropical and current_month in [11, 12, 1, 2]: # Winter dormancy for temperate trees
                    kc = req.kc_initial
                    stage = "Winter Dormancy (Predicted Calendar Fallback)"
                else:
                    kc = req.kc_mid # Full canopy demand
                    stage = "Mature Canopy Active (Predicted Calendar Fallback)"
                
        else:
            # Linear Growth Stage calculation for seasonal crops
            if days_since_planting < (req.days_to_maturity * 0.2):
                kc = req.kc_initial
                stage = "Initial"
            elif days_since_planting < (req.days_to_maturity * 0.8):
                kc = req.kc_mid
                stage = "Mid-Season"
            else:
                kc = req.kc_end
                stage = "Late-Season"
            
        # Crop Evapotranspiration (ETc) = ET0 * Kc
        etc_7d = et0_7d * kc
        
        # 2. Incorporate Starting Soil Moisture (percentage to roughly estimated mm available water)
        # Calculate dynamic Available Water Capacity (AWC) based on Soil Texture
        # AWC represents the water held between Field Capacity and Permanent Wilting Point
        sand = soil.get("sand", 40)
        clay = soil.get("clay", 30)
        
        # Simplified Pedotransfer function for AWC (mm of water per cm of soil)
        # Sand drains quickly (low AWC), Silt/Loam holds well (high AWC), Clay holds tight (medium AWC)
        if sand > 60:
            awc_mm_per_cm = 1.0  # Sandy soils hold less plant-available water
        elif clay > 40:
            awc_mm_per_cm = 1.3  # Heavy clay holds a lot, but holds it too tightly for roots
        else:
            awc_mm_per_cm = 1.7  # Loamy soils have the highest optimal *available* capacity
            
        # Calculate dynamic effective root zone depth based on exact crop traits and current growth stage
        min_depth = getattr(req, 'root_depth_min_mm', 200)
        max_depth = getattr(req, 'root_depth_max_mm', 600)
        
        # Root depth increases from min (at planting) to max (at mid-season, ~80% of maturity)
        max_growth_days = req.days_to_maturity * 0.8
        if max_growth_days > 0:
            growth_fraction = min(1.0, max(0.0, days_since_planting / max_growth_days))
        else:
            growth_fraction = 1.0
            
        effective_root_depth_mm = min_depth + (max_depth - min_depth) * growth_fraction
        max_capacity_mm = (effective_root_depth_mm / 10.0) * awc_mm_per_cm
        
        current_moisture_pct = soil.get("soil_moisture", 30)
        available_soil_water_mm = (current_moisture_pct / 100.0) * max_capacity_mm
        
        # Water Deficit = Water Lost (ETc) - Water Gained (Precipitation) - Existing Bank (Soil Water)
        water_deficit = etc_7d - precip_7d - available_soil_water_mm
        
        if water_deficit > 10:
            deficit_val = round(water_deficit, 1)
            advice_str = f"In {stage} stage, crop needs {round(etc_7d, 1)}mm water. With {round(current_moisture_pct, 1)}% soil moisture (equivalent {round(available_soil_water_mm, 1)}mm root banked) and {round(precip_7d,1)}mm rain expected, apply {deficit_val}mm irrigation."
            
            if area_ha and area_ha > 0:
                # 1 mm of water over 1 hectare = 10,000 Liters
                total_liters = round(deficit_val * area_ha * 10000)
                advice_str += f"\nPlot Total ({round(area_ha, 2)} hectares): {total_liters:,} Liters of water required immediately."
                
            return {
                "status": "Irrigation Required",
                "deficit_mm": deficit_val,
                "growth_stage": stage,
                "crop_coefficient": kc,
                "advice": advice_str
            }
        else:
            advice_str = f"Current soil moisture holds {round(current_moisture_pct, 1)}% (equivalent {round(available_soil_water_mm, 1)}mm banked) + expected rain ({round(precip_7d,1)}mm) sufficiently covers the {round(etc_7d, 1)}mm required for the {stage} growth stage."
            return {
                "status": "No Immediate Irrigation Needed",
                "deficit_mm": 0,
                "growth_stage": stage,
                "crop_coefficient": kc,
                "advice": advice_str
            }
            
    def calculate_timeline(self, crop_name, start_date=None, optimal_month=None, forecast_precip=None):
        """Estimates harvest date based on current planting date or optimal planting month."""
        req = get_crop_requirements(crop_name)
        if not req: return None
        
        now = datetime.datetime.now()
        
        if optimal_month:
            # Find the next occurrence of this optimal month
            y = now.year if optimal_month >= now.month else now.year + 1
            base_date = now if optimal_month == now.month else datetime.datetime(y, optimal_month, 1)
            
            # Live Weather Fine-Tuning: If planting this month, find a dry 3-day window
            # Live Weather Fine-Tuning: If planting this month, find precise 3-day window
            if optimal_month == now.month and forecast_precip and len(forecast_precip) >= 14:
                best_day_idx = 0
                if getattr(req, "is_tree_crop", False):
                    # Trees should be planted immediately without waiting for a weather window.
                    planting_start = now
                else:
                    # Normal seeds prefer dry starts to avoid rot and washing away.
                    lowest_rain = 9999
                    for i in range(12):
                        window_rain = sum(forecast_precip[i:i+3])
                        if window_rain < lowest_rain:
                            lowest_rain = window_rain
                            best_day_idx = i
                planting_start = now + datetime.timedelta(days=best_day_idx)
            else:
                planting_start = base_date
        else:
            planting_start = start_date if start_date else now
            
        planting_end = planting_start + datetime.timedelta(days=14)
        harvest_start = planting_start + datetime.timedelta(days=req.days_to_maturity)
        harvest_end = harvest_start + datetime.timedelta(days=14)
        
        timeline_data = {
            "estimated_planting": f"{planting_start.strftime('%b %d')} - {planting_end.strftime('%b %d, %Y')}",
            "estimated_harvest": f"{harvest_start.strftime('%b %d')} - {harvest_end.strftime('%b %d, %Y')}",
            "days_to_maturity": req.days_to_maturity,
            "harvest_type": "Multiple Harvests" if req.has_multiple_harvests else "Single Harvest"
        }
        
        if req.has_multiple_harvests and req.harvest_interval_days > 0:
            next_h_start = harvest_start + datetime.timedelta(days=req.harvest_interval_days)
            next_h_end = next_h_start + datetime.timedelta(days=14)
            timeline_data["estimated_next_harvest"] = f"{next_h_start.strftime('%b %d')} - {next_h_end.strftime('%b %d, %Y')}"
            timeline_data["harvest_interval_days"] = req.harvest_interval_days
            
        return timeline_data

    def calculate_intercropping(self, crop_name):
        """Generates dynamic intercropping suggestions (spatial & temporal)."""
        req = get_crop_requirements(crop_name)
        if not req: return []
        
        suggestions = []
        
        # 1. Direct companions (e.g., Legumes with Cereals)
        if req.compatible_intercrops:
            suggestions.append(f"Companion Planting: Highly compatible with {', '.join(req.compatible_intercrops)} to improve nutrient cycling and pest management.")
            
        # 2. Temporal Intercropping for Tree Saplings (e.g., Pineapple under Rubber)
        if req.is_tree_crop:
            shade_tolerants = [c for c, cr in CROP_DB.items() if cr.is_shade_tolerant and c != crop_name]
            if shade_tolerants:
                suggestions.append(f"Sapling Synergy: Since {crop_name} takes years to mature, generate interim revenue by planting shade-tolerant cash crops like {', '.join(shade_tolerants[:3])} in the understory between saplings.")
                
        return suggestions

    def analyze(self, env_data, primary_crop=None, planting_date=None, harvest_date=None):
        """Full execution suite."""
        soil = env_data.get("soil", {})
        
        # Calculate regional soil type utilizing the enhanced classification matrix
        sand = soil.get("sand", 40)
        clay = soil.get("clay", 30)
        soc = soil.get("soc", 20)
        ph = soil.get("ph", 6.5)
        soil["dominant_soil_type"] = self.classify_soil(sand, clay, soc, ph)
        env_data["soil"] = soil
        
        if soil.get("error"):
            env_data.pop("plot_geometry", None)
            return {
                "environmental_data": env_data,
                "active_crop_status": None,
                "crop_viability_analysis": [],
                "upcoming_seasons": [],
                "interim_crop_strategy": None,
                "system_message": soil["error"]
            }
            
        if not soil.get("is_arable", True):
            env_data.pop("plot_geometry", None)
            return {
                "environmental_data": env_data,
                "active_crop_status": None,
                "crop_viability_analysis": [],
                "upcoming_seasons": [],
                "interim_crop_strategy": None,
                "system_message": "Non-arable land detected (e.g., Ocean, Glacier, or Extreme Urban). No viable soil physical properties exist here."
            }
            
        # --- Harvest-Aware Temporal Logic ---
        now = datetime.datetime.now()
        occupied_until = None
        target_month_offset = 0
        active_crop_status = None
        sys_msg = "Arable land analyzed successfully."
        
        # Calculate True Area from Coordinates to generate Plot Totals globally
        area_ha = 0
        if "plot_geometry" in env_data:
            area_ha = self.calculate_polygon_area_ha(env_data["plot_geometry"])
            
        sys_msg = "Arable land analyzed successfully."
        
        if primary_crop:
            try:
                req = CROP_DB.get(primary_crop.title())
                
                # Prioritize dynamic calculation if planting_date and CROP_DB match exist
                dsp_actual = None
                if planting_date and req:
                    if 'T' in planting_date:
                        p_date = datetime.datetime.fromisoformat(planting_date.replace('Z', '+00:00')).replace(tzinfo=None)
                    else:
                        p_date = datetime.datetime.strptime(planting_date, '%Y-%m-%d').replace(tzinfo=None)
                        
                    dsp_actual = (now - p_date).days
                    if dsp_actual < 0: dsp_actual = 0
                    
                    if getattr(req, 'is_tree_crop', False) or getattr(req, 'has_multiple_harvests', False):
                        # Perennials stay indefinitely, push the occupation far into the future so they aren't 'harvested'
                        occupied_until = now + datetime.timedelta(days=3650)
                    else:
                        occupied_until = p_date + datetime.timedelta(days=req.days_to_maturity)
                elif harvest_date:
                    # Fallback to the explicit DB harvest date if user entered a custom crop not in DB
                    if 'T' in harvest_date:
                        occupied_until = datetime.datetime.fromisoformat(harvest_date.replace('Z', '+00:00')).replace(tzinfo=None)
                    else:
                        occupied_until = datetime.datetime.strptime(harvest_date, '%Y-%m-%d').replace(tzinfo=None)
                
                if occupied_until and occupied_until > now:
                    days_remaining = (occupied_until - now).days
                    
                    if getattr(req, 'is_tree_crop', False) or getattr(req, 'has_multiple_harvests', False):
                        target_month_offset = 0
                        sys_msg = f"Plot is currently occupied by perennial crop {primary_crop}. The following recommendations are tailored for ongoing growth."
                        occ_str = "Ongoing (Perennial/Tree Crop)"
                    else:
                        target_month_offset = (days_remaining // 30) + 1
                        sys_msg = f"Plot is currently occupied by {primary_crop}. Harvest is expected around {occupied_until.strftime('%b %d, %Y')}. The following crop recommendations have been optimized for the post-harvest climate."
                        occ_str = occupied_until.strftime('%b %d, %Y')
                    
                    active_crop_status = {
                        "crop": primary_crop,
                        "occupied_until": occ_str,
                        "fertilizer_recommendations": self.calculate_fertilizer(primary_crop, env_data.get("soil", {}), area_ha=area_ha),
                        "irrigation_schedule": self.calculate_irrigation(primary_crop, env_data, area_ha=area_ha, days_since_planting=dsp_actual)
                    }
            except Exception as e:
                print(f"[Analyzer] Failed to parse occupation dates: {e}")
                
        # Override baseline climate payload for suitability check into the future if necessary
        climate = env_data.get("climate", {})
        outlook = climate.get("six_month_outlook", [])
        
        if target_month_offset > 0 and len(outlook) == 6:
            shift_idx = min(target_month_offset, 5) # Cap at the 6-month maximum limit
            climate["avg_temp_c"] = outlook[shift_idx]["avg_temp_c"]
            climate["monthly_precip_mm"] = outlook[shift_idx]["avg_precip_mm"]
        suitability = self.get_crop_suitability(env_data)
        
        if not suitability and not primary_crop:
            env_data.pop("plot_geometry", None)
            return {
                "environmental_data": env_data,
                "active_crop_status": None,
                "crop_viability_analysis": [],
                "upcoming_seasons": [],
                "interim_crop_strategy": None,
                "system_message": "Extreme Environment (e.g., Mount Everest / Desert). No registered crops can physically survive here based on absolute temperature thresholds."
            }
        
        # We no longer isolate one "top_crop". Every viable crop gets full analysis.
        # --- Predictive Seasonal Logic ---
        climate = env_data.get("climate", {})
        outlook = climate.get("six_month_outlook", [])
        upcoming_seasons = []
        interim_crop_suggestion = None
        
        if len(outlook) == 6:
            # Predict 3 months out
            temp_3m = outlook[3]["avg_temp_c"]
            suit_3m = self.get_crop_suitability(env_data, temp_override=temp_3m)
            
            # Predict 6 months out
            temp_6m = outlook[5]["avg_temp_c"]
            suit_6m = self.get_crop_suitability(env_data, temp_override=temp_6m)
            
            if suit_3m:
                best_3m = suit_3m[0]
                upcoming_seasons.append({
                    "timeframe": "3 Months (Next Season)",
                    "month": outlook[3]["month"],
                    "projected_avg_temp_c": temp_3m,
                    "top_crops": suit_3m
                })
                # Suggest a fast-growing interim cover crop to plant now until the 3-month season hits
                fast_crops = [r for r in suitability if r["score"] > 60]
                for fc in fast_crops:
                    fc_req = CROP_DB.get(fc["crop"])
                    # If it matures in under 90 days, it's a great interim crop before the 3-month mark
                    if fc_req and fc_req.days_to_maturity < 90 and fc["crop"] != best_3m["crop"]:
                        interim_crop_suggestion = {
                            "interim_crop": fc["crop"],
                            "target_future_crop": best_3m["crop"],
                            "reasoning": f"Plant {fc['crop']} now. It matures in {fc_req.days_to_maturity} days and is highly suitable for current conditions. Once harvested, the season will be perfect for {best_3m['crop']}."
                        }
                        break
                        
            if suit_6m:
                upcoming_seasons.append({
                    "timeframe": "6 Months (Following Season)",
                    "month": outlook[5]["month"],
                    "projected_avg_temp_c": temp_6m,
                    "top_crops": suit_6m
                })
        
        # Inject deep analytical diagnostics into every viable crop
        full_analysis = []
        for s in suitability:
            c_name = s["crop"]
            
            # Execute dynamic harvest timeline based on optimal simulated planting month
            # Fallback to occupied_until if this is forced override analysis
            sd = occupied_until if isinstance(occupied_until, datetime.datetime) else None
            forecast_data = env_data.get("forecast", {}).get("precip_sum_mm", [])
            timeline = self.calculate_timeline(
                c_name, 
                start_date=sd, 
                optimal_month=s.get("optimal_planting_month"), 
                forecast_precip=forecast_data
            )
            if not timeline:
                timeline = {
                    "estimated_planting": "N/A",
                    "estimated_harvest": "N/A",
                    "days_to_maturity": 0,
                    "harvest_type": "Data Unavailable"
                }
                
            if target_month_offset > 0 and isinstance(occupied_until, datetime.datetime):
                irrig = {"status": "Future Planting", "advice": f"Detailed daily irrigation scheduling will become available closer to the projected planting window ({occupied_until.strftime('%b %Y')})."}
                fert = ["Detailed fertilization plans should be reassessed closer to the planting date using updated soil tests."]
            else:
                # Calculate True Area from Coordinates to generate Plot Totals
                area_ha = 0
                if "coordinates" in env_data:
                    # In our system coordinates are passed directly into the fetcher but we should pass them through
                    pass
                if "plot_geometry" in env_data:
                    area_ha = self.calculate_polygon_area_ha(env_data["plot_geometry"])
                    
                irrig = self.calculate_irrigation(c_name, env_data, area_ha=area_ha)
                if not irrig:
                    irrig = {"status": "Analyzed", "advice": "No specific irrigation data available."}
                fert = self.calculate_fertilizer(c_name, env_data.get("soil", {}), area_ha=area_ha)
                
            full_analysis.append({
                "crop": c_name,
                "score": s["score"],
                "reasoning": s.get("reasoning", ""),
                "intercropping_partners": s.get("intercropping_partners", []),
                "fertilizer_recommendations": fert,
                "irrigation_schedule": irrig,
                "growth_timeline": timeline
            })
        if "plot_geometry" in env_data:
            del env_data["plot_geometry"]
            
        return {
            "environmental_data": env_data,
            "active_crop_status": active_crop_status,
            "crop_viability_analysis": full_analysis, # Formerly top_crops/focused_analysis
            "upcoming_seasons": upcoming_seasons,
            "interim_crop_strategy": interim_crop_suggestion,
            "system_message": sys_msg
        }
