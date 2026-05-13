from .data_fetcher import DataFetcher
from .analyzer import Analyzer

class AdvancedEngine:
    """
    Main orchestration class for the Engine framework.
    Coordinates fetching weather, climate, and soil data from diverse sources,
    and feeding them into the advanced agronomic analyzer.
    """
    def __init__(self):
        self.fetcher = DataFetcher()
        self.analyzer = Analyzer()

    def generate_recommendations(self, coords, primary_crop=None, sensor_data=None, planting_date=None, harvest_date=None):
        """
        Executes the full pipeline for the given plot geometry.
        :param coords: A list of [lng, lat] coordinate pairs.
        :param primary_crop: An optional crop name to focus the analysis on an existing planting.
        :param sensor_data: An optional dict containing live hardware sensor readings (e.g. soil moisture, NPK).
        :param planting_date: ISO 8601 string representing when the primary crop was planted.
        :param harvest_date: ISO 8601 string representing explicit harvest date.
        :return: A deeply analyzed recommendation payload.
        """
        print("[Engine] Commencing Data Acquisition...")
        env_data = self.fetcher.fetch_all(coords)
        
        # Override Earth Engine / static defaults with Live Hardware Sensor Data if present
        if sensor_data:
            print("[Engine] Intercepting fetch with Live Sensor hardware data...")
            if "soil" not in env_data: env_data["soil"] = {}
            if "climate" not in env_data: env_data["climate"] = {}
            
            # Find the latest reading by looking at the highest reading_X index
            latest_reading_idx = -1
            latest_reading = None
            for key, val in sensor_data.items():
                if key.startswith("reading_") and isinstance(val, dict):
                    try:
                        idx = int(key.split("_")[1])
                        if idx > latest_reading_idx:
                            latest_reading_idx = idx
                            latest_reading = val
                    except ValueError:
                        continue
                        
            if latest_reading:
                print(f"[Engine] Using latest sensor reading: reading_{latest_reading_idx}")
                if "soil_moisture" in latest_reading:
                    env_data["soil"]["soil_moisture"] = latest_reading["soil_moisture"]
                if "temperature" in latest_reading:
                    env_data["climate"]["avg_temp_c"] = latest_reading["temperature"]
                if "humidity" in latest_reading:
                    env_data["climate"]["humidity"] = latest_reading["humidity"]
            else:
                # Legacy fallback if it's a flat structure
                for key, val in sensor_data.items():
                    env_data["soil"][key] = val
        
        print("[Engine] Commencing Agronomic Analysis...")
        analysis_report = self.analyzer.analyze(
            env_data, 
            primary_crop=primary_crop, 
            planting_date=planting_date, 
            harvest_date=harvest_date
        )
        
        return analysis_report
