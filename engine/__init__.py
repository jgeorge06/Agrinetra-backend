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
