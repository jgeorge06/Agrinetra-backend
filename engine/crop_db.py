from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class CropRequirement:
    name: str
    optimal_temp_min: float
    optimal_temp_max: float
    absolute_temp_min: float
    absolute_temp_max: float
    ph_min: float
    ph_max: float
    n_req_kg_per_ha: int  # Nitrogen requirement (kg/hectare)
    p_req_kg_per_ha: int  # Phosphorous requirement (kg/hectare)
    k_req_kg_per_ha: int  # Potassium requirement (kg/hectare)
    water_reqs_mm_season: int
    root_depth_min_mm: int  # Initial root stage depth (e.g. at planting)
    root_depth_max_mm: int  # Maximum root stage depth (e.g. at mid-season/maturity)
    days_to_maturity: int
    tolerant_to_drought: bool
    tolerant_to_waterlogging: bool # Flood tolerance
    kc_initial: float              # Crop Coefficient early stage
    kc_mid: float                  # Crop Coefficient mid stage
    kc_end: float                  # Crop Coefficient late stage
    preferred_soil_types: List[str]
    has_multiple_harvests: bool = False
    harvest_interval_days: int = 0
    is_tree_crop: bool = False           # Useful for sapling-stage intercropping calculations
    is_shade_tolerant: bool = False      # Useful for under-canopy planting
    rainfed_after_days: int = -1         # Days after planting when the crop becomes strictly rainfed (-1 = never)
    compatible_intercrops: List[str] = field(default_factory=list) # Synergistic pairs
    optimal_altitude_min: float = 0.0    # meters above sea level
    optimal_altitude_max: float = 3000.0 # defaults to widely tolerant

    def to_dict(self):
        return {
            "name": self.name,
            "optimal_temp_min": self.optimal_temp_min,
            "optimal_temp_max": self.optimal_temp_max,
            "absolute_temp_min": self.absolute_temp_min,
            "absolute_temp_max": self.absolute_temp_max,
            "ph_min": self.ph_min,
            "ph_max": self.ph_max,
            "n_req_kg_per_ha": self.n_req_kg_per_ha,
            "p_req_kg_per_ha": self.p_req_kg_per_ha,
            "k_req_kg_per_ha": self.k_req_kg_per_ha,
            "water_reqs_mm_season": self.water_reqs_mm_season,
            "root_depth_min_mm": self.root_depth_min_mm,
            "root_depth_max_mm": self.root_depth_max_mm,
            "days_to_maturity": self.days_to_maturity,
            "tolerant_to_drought": self.tolerant_to_drought,
            "tolerant_to_waterlogging": self.tolerant_to_waterlogging,
            "kc_initial": self.kc_initial,
            "kc_mid": self.kc_mid,
            "kc_end": self.kc_end,
            "preferred_soil_types": self.preferred_soil_types,
            "has_multiple_harvests": self.has_multiple_harvests,
            "harvest_interval_days": self.harvest_interval_days,
            "is_tree_crop": self.is_tree_crop,
            "is_shade_tolerant": self.is_shade_tolerant,
            "rainfed_after_days": self.rainfed_after_days,
            "compatible_intercrops": self.compatible_intercrops,
            "optimal_altitude_min": self.optimal_altitude_min,
            "optimal_altitude_max": self.optimal_altitude_max
        }

# Data derived from FAO Irrigation and Drainage Paper No. 56 (for Kc) and FAO EcoCrop general guidelines
# These requirements guide suitability scoring, fertilizer dosing, and irrigation scheduling.
CROP_DB: Dict[str, CropRequirement] = {
    "Rice": CropRequirement(
        name="Rice",
        optimal_temp_min=20.0, optimal_temp_max=35.0,
        absolute_temp_min=15.0, absolute_temp_max=40.0,
        ph_min=5.5, ph_max=6.5,
        n_req_kg_per_ha=100, p_req_kg_per_ha=50, k_req_kg_per_ha=50,
        water_reqs_mm_season=1500, root_depth_min_mm=300, root_depth_max_mm=1200, # High water demand
        days_to_maturity=120,
        tolerant_to_drought=False,
        tolerant_to_waterlogging=True,
        kc_initial=1.05, kc_mid=1.20, kc_end=0.90,
        preferred_soil_types=["Clayey", "Loamy"]
    ),
    "Wheat": CropRequirement(
        name="Wheat",
        optimal_temp_min=15.0, optimal_temp_max=25.0,
        absolute_temp_min=5.0, absolute_temp_max=35.0,
        ph_min=6.0, ph_max=7.5,
        n_req_kg_per_ha=120, p_req_kg_per_ha=60, k_req_kg_per_ha=40,
        water_reqs_mm_season=500, root_depth_min_mm=300, root_depth_max_mm=1200,
        days_to_maturity=150,
        tolerant_to_drought=True,
        tolerant_to_waterlogging=False,
        kc_initial=0.70, kc_mid=1.15, kc_end=0.25,
        preferred_soil_types=["Loamy", "Clayey"]
    ),
    "Maize": CropRequirement(
        name="Maize",
        optimal_temp_min=20.0, optimal_temp_max=30.0,
        absolute_temp_min=10.0, absolute_temp_max=40.0,
        ph_min=5.8, ph_max=7.0,
        n_req_kg_per_ha=150, p_req_kg_per_ha=60, k_req_kg_per_ha=60,
        water_reqs_mm_season=600, root_depth_min_mm=300, root_depth_max_mm=1200,
        days_to_maturity=100,
        tolerant_to_drought=False,
        tolerant_to_waterlogging=False,
        kc_initial=0.30, kc_mid=1.20, kc_end=0.35,
        preferred_soil_types=["Loamy", "Red"]
    ),
    "Cotton": CropRequirement(
        name="Cotton",
        optimal_temp_min=25.0, optimal_temp_max=35.0,
        absolute_temp_min=15.0, absolute_temp_max=40.0,
        ph_min=6.0, ph_max=8.0,
        n_req_kg_per_ha=120, p_req_kg_per_ha=60, k_req_kg_per_ha=60,
        water_reqs_mm_season=900, root_depth_min_mm=300, root_depth_max_mm=1200,
        days_to_maturity=160,
        tolerant_to_drought=True,
        tolerant_to_waterlogging=False,
        kc_initial=0.35, kc_mid=1.15, kc_end=0.70,
        preferred_soil_types=["Black", "Clayey", "Loamy"]
    ),
    "Sugarcane": CropRequirement(
        name="Sugarcane",
        optimal_temp_min=24.0, optimal_temp_max=30.0,
        absolute_temp_min=15.0, absolute_temp_max=38.0,
        ph_min=6.5, ph_max=7.5,
        n_req_kg_per_ha=250, p_req_kg_per_ha=100, k_req_kg_per_ha=100,
        water_reqs_mm_season=2000, root_depth_min_mm=300, root_depth_max_mm=1200,
        days_to_maturity=300,
        tolerant_to_drought=False,
        tolerant_to_waterlogging=True, # Tolerates some flooding
        kc_initial=0.40, kc_mid=1.25, kc_end=0.75,
        preferred_soil_types=["Loamy", "Clayey"]
    ),
    "Blackgram": CropRequirement(
        name="Blackgram",
        optimal_temp_min=25.0, optimal_temp_max=35.0,
        absolute_temp_min=20.0, absolute_temp_max=40.0,
        ph_min=6.5, ph_max=7.5,
        n_req_kg_per_ha=20, p_req_kg_per_ha=40, k_req_kg_per_ha=20, # Legumes fix N
        water_reqs_mm_season=400, root_depth_min_mm=300, root_depth_max_mm=1200,
        days_to_maturity=70,
        tolerant_to_drought=True,
        tolerant_to_waterlogging=False,
        kc_initial=0.40, kc_mid=1.15, kc_end=0.35,
        preferred_soil_types=["Loamy", "Sandy"]
    ),
    "Chickpea": CropRequirement(
        name="Chickpea",
        optimal_temp_min=15.0, optimal_temp_max=25.0,
        absolute_temp_min=5.0, absolute_temp_max=35.0,
        ph_min=6.0, ph_max=8.0,
        n_req_kg_per_ha=20, p_req_kg_per_ha=40, k_req_kg_per_ha=20, # Legumes fix N
        water_reqs_mm_season=300, root_depth_min_mm=300, root_depth_max_mm=1200,
        days_to_maturity=100,
        tolerant_to_drought=True,
        tolerant_to_waterlogging=False,
        kc_initial=0.40, kc_mid=1.00, kc_end=0.35,
        preferred_soil_types=["Loamy", "Black"]
    ),
    "Coconut": CropRequirement(
        name="Coconut",
        optimal_temp_min=27.0, optimal_temp_max=32.0,
        absolute_temp_min=20.0, absolute_temp_max=35.0,
        ph_min=5.2, ph_max=8.0,
        n_req_kg_per_ha=30, p_req_kg_per_ha=20, k_req_kg_per_ha=60, # Per tree estimation adapted to ha (placeholder)
        water_reqs_mm_season=2200, root_depth_min_mm=300, root_depth_max_mm=1200,
        days_to_maturity=1800, # Perennial
        tolerant_to_drought=False,
        tolerant_to_waterlogging=False,
        kc_initial=0.75, kc_mid=0.75, kc_end=0.75, # Relatively constant for trees
        preferred_soil_types=["Sandy", "Loamy"],
        has_multiple_harvests=True,
        harvest_interval_days=45, # Coconuts harvested frequently
        is_tree_crop=True, rainfed_after_days=1095
    ),
    "Tomato": CropRequirement(
        name="Tomato",
        optimal_temp_min=18.0, optimal_temp_max=27.0,
        absolute_temp_min=10.0, absolute_temp_max=35.0,
        ph_min=6.0, ph_max=7.0,
        n_req_kg_per_ha=100, p_req_kg_per_ha=50, k_req_kg_per_ha=150,
        water_reqs_mm_season=600, root_depth_min_mm=300, root_depth_max_mm=1200,
        days_to_maturity=110,
        tolerant_to_drought=False,
        tolerant_to_waterlogging=False,
        kc_initial=0.60, kc_mid=1.15, kc_end=0.80,
        preferred_soil_types=["Loamy", "Sandy"]
    ),
    "Potato": CropRequirement(
        name="Potato",
        optimal_temp_min=15.0, optimal_temp_max=20.0,
        absolute_temp_min=5.0, absolute_temp_max=30.0,
        ph_min=5.0, ph_max=6.5,
        n_req_kg_per_ha=120, p_req_kg_per_ha=80, k_req_kg_per_ha=160,
        water_reqs_mm_season=500, root_depth_min_mm=300, root_depth_max_mm=1200,
        days_to_maturity=120,
        tolerant_to_drought=False,
        tolerant_to_waterlogging=False,
        kc_initial=0.50, kc_mid=1.15, kc_end=0.75,
        preferred_soil_types=["Loamy", "Sandy"]
    ),
    "Soybean": CropRequirement(
        name="Soybean",
        optimal_temp_min=20.0, optimal_temp_max=30.0,
        absolute_temp_min=10.0, absolute_temp_max=40.0,
        ph_min=6.0, ph_max=7.0,
        n_req_kg_per_ha=20, p_req_kg_per_ha=50, k_req_kg_per_ha=40, # Legumes fix N
        water_reqs_mm_season=500, root_depth_min_mm=300, root_depth_max_mm=1200,
        days_to_maturity=100,
        tolerant_to_drought=True,
        tolerant_to_waterlogging=False,
        kc_initial=0.40, kc_mid=1.15, kc_end=0.50,
        preferred_soil_types=["Loamy"],
        compatible_intercrops=["Maize", "Sorghum"]
    ),
    "Sorghum": CropRequirement(
        name="Sorghum",
        optimal_temp_min=25.0, optimal_temp_max=32.0,
        absolute_temp_min=15.0, absolute_temp_max=40.0,
        ph_min=5.5, ph_max=8.5,
        n_req_kg_per_ha=80, p_req_kg_per_ha=40, k_req_kg_per_ha=40,
        water_reqs_mm_season=450, root_depth_min_mm=300, root_depth_max_mm=1200,
        days_to_maturity=110,
        tolerant_to_drought=True,
        tolerant_to_waterlogging=True,
        kc_initial=0.30, kc_mid=1.10, kc_end=0.55,
        preferred_soil_types=["Clayey", "Loamy", "Sandy"], rainfed_after_days=0
    ),
    "Pearl Millet": CropRequirement(
        name="Pearl Millet",
        optimal_temp_min=25.0, optimal_temp_max=35.0,
        absolute_temp_min=10.0, absolute_temp_max=45.0, # Highly heat tolerant
        ph_min=5.5, ph_max=8.0,
        n_req_kg_per_ha=60, p_req_kg_per_ha=30, k_req_kg_per_ha=30,
        water_reqs_mm_season=300, root_depth_min_mm=300, root_depth_max_mm=1200, # Very low water req
        days_to_maturity=80,
        tolerant_to_drought=True,
        tolerant_to_waterlogging=False,
        kc_initial=0.30, kc_mid=1.00, kc_end=0.30,
        preferred_soil_types=["Sandy", "Loamy"], rainfed_after_days=0
    ),
    "Groundnut": CropRequirement(
        name="Groundnut",
        optimal_temp_min=25.0, optimal_temp_max=30.0,
        absolute_temp_min=15.0, absolute_temp_max=35.0,
        ph_min=6.0, ph_max=6.5,
        n_req_kg_per_ha=25, p_req_kg_per_ha=50, k_req_kg_per_ha=75,
        water_reqs_mm_season=600, root_depth_min_mm=300, root_depth_max_mm=1200,
        days_to_maturity=120,
        tolerant_to_drought=True,
        tolerant_to_waterlogging=False,
        kc_initial=0.40, kc_mid=1.15, kc_end=0.60,
        preferred_soil_types=["Sandy", "Loamy"]
    ),
    "Sunflower": CropRequirement(
        name="Sunflower",
        optimal_temp_min=20.0, optimal_temp_max=25.0,
        absolute_temp_min=5.0, absolute_temp_max=40.0,
        ph_min=6.0, ph_max=7.5,
        n_req_kg_per_ha=80, p_req_kg_per_ha=60, k_req_kg_per_ha=40,
        water_reqs_mm_season=700, root_depth_min_mm=300, root_depth_max_mm=1200,
        days_to_maturity=130,
        tolerant_to_drought=True,
        tolerant_to_waterlogging=False,
        kc_initial=0.35, kc_mid=1.15, kc_end=0.35,
        preferred_soil_types=["Loamy", "Sandy"]
    ),
    "Onion": CropRequirement(
        name="Onion",
        optimal_temp_min=13.0, optimal_temp_max=24.0,
        absolute_temp_min=5.0, absolute_temp_max=35.0,
        ph_min=6.0, ph_max=7.0,
        n_req_kg_per_ha=100, p_req_kg_per_ha=50, k_req_kg_per_ha=100,
        water_reqs_mm_season=450, root_depth_min_mm=300, root_depth_max_mm=1200,
        days_to_maturity=150,
        tolerant_to_drought=False,
        tolerant_to_waterlogging=False,
        kc_initial=0.70, kc_mid=1.05, kc_end=0.75,
        preferred_soil_types=["Loamy", "Sandy"]
    ),
    "Garlic": CropRequirement(
        name="Garlic",
        optimal_temp_min=13.0, optimal_temp_max=24.0,
        absolute_temp_min=5.0, absolute_temp_max=35.0,
        ph_min=6.0, ph_max=7.0,
        n_req_kg_per_ha=100, p_req_kg_per_ha=50, k_req_kg_per_ha=100,
        water_reqs_mm_season=450, root_depth_min_mm=300, root_depth_max_mm=1200,
        days_to_maturity=150,
        tolerant_to_drought=False,
        tolerant_to_waterlogging=False,
        kc_initial=0.70, kc_mid=1.00, kc_end=0.70,
        preferred_soil_types=["Loamy", "Sandy"]
    ),
    "Carrot": CropRequirement(
        name="Carrot",
        optimal_temp_min=15.0, optimal_temp_max=20.0,
        absolute_temp_min=5.0, absolute_temp_max=30.0,
        ph_min=5.5, ph_max=7.0,
        n_req_kg_per_ha=80, p_req_kg_per_ha=50, k_req_kg_per_ha=100,
        water_reqs_mm_season=450, root_depth_min_mm=300, root_depth_max_mm=1200,
        days_to_maturity=90,
        tolerant_to_drought=False,
        tolerant_to_waterlogging=False,
        kc_initial=0.70, kc_mid=1.05, kc_end=0.95,
        preferred_soil_types=["Sandy", "Loamy"]
    ),
    "Cabbage": CropRequirement(
        name="Cabbage",
        optimal_temp_min=15.0, optimal_temp_max=20.0,
        absolute_temp_min=0.0, absolute_temp_max=30.0, # Frost tolerant
        ph_min=6.0, ph_max=6.8,
        n_req_kg_per_ha=150, p_req_kg_per_ha=50, k_req_kg_per_ha=150,
        water_reqs_mm_season=450, root_depth_min_mm=300, root_depth_max_mm=1200,
        days_to_maturity=100,
        tolerant_to_drought=False,
        tolerant_to_waterlogging=False,
        kc_initial=0.70, kc_mid=1.05, kc_end=0.95,
        preferred_soil_types=["Loamy", "Clayey"]
    ),
    "Banana": CropRequirement(
        name="Banana",
        optimal_temp_min=26.0, optimal_temp_max=30.0,
        absolute_temp_min=15.0, absolute_temp_max=35.0,
        ph_min=5.5, ph_max=7.0,
        n_req_kg_per_ha=200, p_req_kg_per_ha=50, k_req_kg_per_ha=300,
        water_reqs_mm_season=1500, root_depth_min_mm=300, root_depth_max_mm=1200, # Very high water req
        days_to_maturity=365,
        tolerant_to_drought=False,
        tolerant_to_waterlogging=True,
        kc_initial=0.50, kc_mid=1.10, kc_end=1.00,
        preferred_soil_types=["Loamy", "Clayey"]
    ),
    "Mango": CropRequirement(
        name="Mango",
        optimal_temp_min=24.0, optimal_temp_max=30.0,
        absolute_temp_min=10.0, absolute_temp_max=48.0,
        ph_min=5.5, ph_max=7.5,
        n_req_kg_per_ha=100, p_req_kg_per_ha=50, k_req_kg_per_ha=100,
        water_reqs_mm_season=1000, root_depth_min_mm=300, root_depth_max_mm=1200,
        days_to_maturity=1800, # Perennial
        tolerant_to_drought=True,
        tolerant_to_waterlogging=False,
        kc_initial=0.75, kc_mid=0.85, kc_end=0.85, # Tree constants
        preferred_soil_types=["Loamy", "Sandy", "Red"],
        has_multiple_harvests=True,
        harvest_interval_days=365, # Annual harvesting season
        is_tree_crop=True, rainfed_after_days=1460
    ),
    "Ginger": CropRequirement(
        name="Ginger",
        optimal_temp_min=20.0, optimal_temp_max=30.0,
        absolute_temp_min=13.0, absolute_temp_max=35.0,
        ph_min=5.5, ph_max=6.5,
        n_req_kg_per_ha=100, p_req_kg_per_ha=50, k_req_kg_per_ha=100,
        water_reqs_mm_season=1500, root_depth_min_mm=300, root_depth_max_mm=1200,
        days_to_maturity=240,
        tolerant_to_drought=False,
        tolerant_to_waterlogging=False,
        kc_initial=0.50, kc_mid=1.10, kc_end=0.90,
        preferred_soil_types=["Loamy"],
        is_shade_tolerant=True
    ),
    "Turmeric": CropRequirement(
        name="Turmeric",
        optimal_temp_min=20.0, optimal_temp_max=35.0,
        absolute_temp_min=15.0, absolute_temp_max=40.0,
        ph_min=5.5, ph_max=7.5,
        n_req_kg_per_ha=150, p_req_kg_per_ha=60, k_req_kg_per_ha=150,
        water_reqs_mm_season=1500, root_depth_min_mm=300, root_depth_max_mm=1200,
        days_to_maturity=270,
        tolerant_to_drought=False,
        tolerant_to_waterlogging=False,
        kc_initial=0.50, kc_mid=1.15, kc_end=0.95,
        preferred_soil_types=["Loamy", "Clayey"],
        is_shade_tolerant=True
    ),
    "Cumin": CropRequirement(
        name="Cumin",
        optimal_temp_min=25.0, optimal_temp_max=30.0,
        absolute_temp_min=10.0, absolute_temp_max=35.0,
        ph_min=6.8, ph_max=8.3,
        n_req_kg_per_ha=30, p_req_kg_per_ha=20, k_req_kg_per_ha=20,
        water_reqs_mm_season=400, root_depth_min_mm=300, root_depth_max_mm=1200,
        days_to_maturity=120,
        tolerant_to_drought=True,
        tolerant_to_waterlogging=False,
        kc_initial=0.40, kc_mid=1.00, kc_end=0.60,
        preferred_soil_types=["Loamy", "Sandy"]
    ),
    "Coriander": CropRequirement(
        name="Coriander",
        optimal_temp_min=15.0, optimal_temp_max=25.0,
        absolute_temp_min=5.0, absolute_temp_max=35.0,
        ph_min=6.0, ph_max=8.0,
        n_req_kg_per_ha=60, p_req_kg_per_ha=30, k_req_kg_per_ha=30,
        water_reqs_mm_season=400, root_depth_min_mm=300, root_depth_max_mm=1200,
        days_to_maturity=100,
        tolerant_to_drought=False,
        tolerant_to_waterlogging=False,
        kc_initial=0.40, kc_mid=1.00, kc_end=0.60,
        preferred_soil_types=["Loamy", "Clayey"]
    ),
    "Chilli": CropRequirement(
        name="Chilli",
        optimal_temp_min=20.0, optimal_temp_max=30.0,
        absolute_temp_min=10.0, absolute_temp_max=35.0,
        ph_min=6.0, ph_max=7.0,
        n_req_kg_per_ha=100, p_req_kg_per_ha=50, k_req_kg_per_ha=50,
        water_reqs_mm_season=600, root_depth_min_mm=300, root_depth_max_mm=1200,
        days_to_maturity=120,
        tolerant_to_drought=False,
        tolerant_to_waterlogging=False,
        kc_initial=0.60, kc_mid=1.05, kc_end=0.90,
        preferred_soil_types=["Loamy", "Sandy", "Red"],
        has_multiple_harvests=True,
        harvest_interval_days=15 # Multiple pickings
    ),
    "Papaya": CropRequirement(
        name="Papaya",
        optimal_temp_min=22.0, optimal_temp_max=30.0,
        absolute_temp_min=15.0, absolute_temp_max=40.0,
        ph_min=6.0, ph_max=7.0,
        n_req_kg_per_ha=200, p_req_kg_per_ha=100, k_req_kg_per_ha=250,
        water_reqs_mm_season=1200, root_depth_min_mm=300, root_depth_max_mm=1200,
        days_to_maturity=270,
        tolerant_to_drought=False,
        tolerant_to_waterlogging=False,
        kc_initial=0.70, kc_mid=0.90, kc_end=0.90,
        preferred_soil_types=["Loamy", "Sandy"],
        has_multiple_harvests=True,
        harvest_interval_days=15 # Weekly/bi-weekly picking once mature
    ),
    "Watermelon": CropRequirement(
        name="Watermelon",
        optimal_temp_min=25.0, optimal_temp_max=32.0,
        absolute_temp_min=15.0, absolute_temp_max=40.0,
        ph_min=6.0, ph_max=6.8,
        n_req_kg_per_ha=100, p_req_kg_per_ha=50, k_req_kg_per_ha=100,
        water_reqs_mm_season=500, root_depth_min_mm=300, root_depth_max_mm=1200,
        days_to_maturity=90,
        tolerant_to_drought=True,
        tolerant_to_waterlogging=False,
        kc_initial=0.40, kc_mid=1.00, kc_end=0.75,
        preferred_soil_types=["Sandy", "Loamy"]
    ),
    "Citrus": CropRequirement(
        name="Citrus",
        optimal_temp_min=15.0, optimal_temp_max=30.0,
        absolute_temp_min=5.0, absolute_temp_max=40.0,
        ph_min=6.0, ph_max=8.0,
        n_req_kg_per_ha=150, p_req_kg_per_ha=50, k_req_kg_per_ha=150,
        water_reqs_mm_season=1000, root_depth_min_mm=300, root_depth_max_mm=1200,
        days_to_maturity=1460, # Several years to mature
        tolerant_to_drought=False,
        tolerant_to_waterlogging=False,
        kc_initial=0.70, kc_mid=0.70, kc_end=0.70,
        preferred_soil_types=["Loamy", "Sandy", "Red"],
        has_multiple_harvests=True,
        harvest_interval_days=365,
        is_tree_crop=True
    ),
    "Cucumber": CropRequirement(
        name="Cucumber",
        optimal_temp_min=20.0, optimal_temp_max=30.0,
        absolute_temp_min=15.0, absolute_temp_max=35.0,
        ph_min=6.0, ph_max=7.5,
        n_req_kg_per_ha=80, p_req_kg_per_ha=40, k_req_kg_per_ha=80,
        water_reqs_mm_season=400, root_depth_min_mm=300, root_depth_max_mm=1200,
        days_to_maturity=60,
        tolerant_to_drought=False,
        tolerant_to_waterlogging=False,
        kc_initial=0.50, kc_mid=1.00, kc_end=0.75,
        preferred_soil_types=["Loamy", "Sandy"],
        has_multiple_harvests=True,
        harvest_interval_days=3
    ),
    "Eggplant": CropRequirement(
        name="Eggplant",
        optimal_temp_min=22.0, optimal_temp_max=30.0,
        absolute_temp_min=15.0, absolute_temp_max=35.0,
        ph_min=5.5, ph_max=6.8,
        n_req_kg_per_ha=100, p_req_kg_per_ha=50, k_req_kg_per_ha=100,
        water_reqs_mm_season=600, root_depth_min_mm=300, root_depth_max_mm=1200,
        days_to_maturity=100,
        tolerant_to_drought=False,
        tolerant_to_waterlogging=False,
        kc_initial=0.60, kc_mid=1.05, kc_end=0.90,
        preferred_soil_types=["Loamy", "Sandy"],
        has_multiple_harvests=True,
        harvest_interval_days=7
    ),
    "Spinach": CropRequirement(
        name="Spinach",
        optimal_temp_min=15.0, optimal_temp_max=20.0,
        absolute_temp_min=0.0, absolute_temp_max=30.0,
        ph_min=6.0, ph_max=7.0,
        n_req_kg_per_ha=80, p_req_kg_per_ha=30, k_req_kg_per_ha=60,
        water_reqs_mm_season=300, root_depth_min_mm=300, root_depth_max_mm=1200,
        days_to_maturity=45,
        tolerant_to_drought=False,
        tolerant_to_waterlogging=False,
        kc_initial=0.70, kc_mid=1.00, kc_end=0.95,
        preferred_soil_types=["Loamy"],
        has_multiple_harvests=True,
        harvest_interval_days=14 # Multiple cuttings
    ),
    "Okra": CropRequirement(
        name="Okra",
        optimal_temp_min=24.0, optimal_temp_max=30.0,
        absolute_temp_min=15.0, absolute_temp_max=40.0,
        ph_min=6.0, ph_max=6.8,
        n_req_kg_per_ha=100, p_req_kg_per_ha=30, k_req_kg_per_ha=50,
        water_reqs_mm_season=500, root_depth_min_mm=300, root_depth_max_mm=1200,
        days_to_maturity=60,
        tolerant_to_drought=True,
        tolerant_to_waterlogging=False,
        kc_initial=0.50, kc_mid=1.00, kc_end=0.90,
        preferred_soil_types=["Loamy", "Sandy"],
        has_multiple_harvests=True,
        harvest_interval_days=3
    ),
    "Tea": CropRequirement(
        name="Tea",
        optimal_temp_min=13.0, optimal_temp_max=30.0,
        absolute_temp_min=5.0, absolute_temp_max=35.0,
        ph_min=4.5, ph_max=5.5, # Highly acidic preference
        n_req_kg_per_ha=150, p_req_kg_per_ha=40, k_req_kg_per_ha=100,
        water_reqs_mm_season=1500, root_depth_min_mm=300, root_depth_max_mm=1200, # Perennial, high water
        days_to_maturity=1000,
        tolerant_to_drought=False,
        tolerant_to_waterlogging=False,
        kc_initial=0.90, kc_mid=1.00, kc_end=1.00,
        preferred_soil_types=["Loamy", "Red"],
        has_multiple_harvests=True,
        harvest_interval_days=15, # Plucking rounds
        optimal_altitude_min=1000.0,
        optimal_altitude_max=2500.0
    ),
    "Coffee": CropRequirement(
        name="Coffee",
        optimal_temp_min=18.0, optimal_temp_max=24.0,
        absolute_temp_min=10.0, absolute_temp_max=35.0,
        ph_min=5.5, ph_max=6.5,
        n_req_kg_per_ha=150, p_req_kg_per_ha=50, k_req_kg_per_ha=150,
        water_reqs_mm_season=1500, root_depth_min_mm=300, root_depth_max_mm=1200,
        days_to_maturity=1460,
        tolerant_to_drought=False,
        tolerant_to_waterlogging=False,
        kc_initial=0.90, kc_mid=0.95, kc_end=0.95,
        preferred_soil_types=["Loamy", "Red"],
        has_multiple_harvests=True,
        harvest_interval_days=365,
        optimal_altitude_min=600.0,
        optimal_altitude_max=2000.0
    ),
    "Rubber": CropRequirement(
        name="Rubber",
        optimal_temp_min=25.0, optimal_temp_max=32.0, absolute_temp_min=20.0, absolute_temp_max=35.0,
        ph_min=4.5, ph_max=6.0,
        n_req_kg_per_ha=30, p_req_kg_per_ha=40, k_req_kg_per_ha=30,
        water_reqs_mm_season=2000, days_to_maturity=2190,
        tolerant_to_drought=False, tolerant_to_waterlogging=False,
        kc_initial=0.95, kc_mid=1.0, kc_end=0.95,
        root_depth_min_mm=500, root_depth_max_mm=1000,
        preferred_soil_types=["Laterite", "Red", "Loamy"],
        is_tree_crop=True, has_multiple_harvests=True, harvest_interval_days=2, # Latex tapping
        compatible_intercrops=["Plantain/Banana", "Pineapple", "Coffee"], rainfed_after_days=1095
    ),
    "Pineapple": CropRequirement(
        name="Pineapple",
        optimal_temp_min=22.0, optimal_temp_max=32.0,
        absolute_temp_min=10.0, absolute_temp_max=40.0,
        ph_min=4.5, ph_max=6.5,
        n_req_kg_per_ha=200, p_req_kg_per_ha=50, k_req_kg_per_ha=250,
        water_reqs_mm_season=1000, root_depth_min_mm=300, root_depth_max_mm=1200,
        days_to_maturity=540, # 18 months
        tolerant_to_drought=True,
        tolerant_to_waterlogging=False,
        kc_initial=0.50, kc_mid=0.30, kc_end=0.30, # CAM photosynthesis limits water use
        preferred_soil_types=["Sandy", "Loamy"],
        is_shade_tolerant=True
    ),
    "Barley": CropRequirement(name="Barley", optimal_temp_min=15.0, optimal_temp_max=20.0, absolute_temp_min=0.0, absolute_temp_max=38.0, ph_min=6.0, ph_max=7.5, n_req_kg_per_ha=80, p_req_kg_per_ha=40, k_req_kg_per_ha=40, water_reqs_mm_season=450, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=120, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.30, kc_mid=1.15, kc_end=0.25, preferred_soil_types=["Loamy", "Clayey"], compatible_intercrops=["Peas", "Clover"], optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Oats": CropRequirement(name="Oats", optimal_temp_min=15.0, optimal_temp_max=24.0, absolute_temp_min=0.0, absolute_temp_max=35.0, ph_min=5.5, ph_max=7.0, n_req_kg_per_ha=70, p_req_kg_per_ha=35, k_req_kg_per_ha=35, water_reqs_mm_season=500, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=120, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.30, kc_mid=1.15, kc_end=0.25, preferred_soil_types=["Loamy", "Sandy"], compatible_intercrops=["Peas"], optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Rye": CropRequirement(name="Rye", optimal_temp_min=10.0, optimal_temp_max=20.0, absolute_temp_min=-5.0, absolute_temp_max=35.0, ph_min=5.0, ph_max=7.5, n_req_kg_per_ha=80, p_req_kg_per_ha=40, k_req_kg_per_ha=40, water_reqs_mm_season=400, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=150, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.30, kc_mid=1.15, kc_end=0.25, preferred_soil_types=["Sandy", "Loamy"], compatible_intercrops=["Clover"], optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Quinoa": CropRequirement(name="Quinoa", optimal_temp_min=15.0, optimal_temp_max=25.0, absolute_temp_min=-4.0, absolute_temp_max=38.0, ph_min=6.0, ph_max=8.5, n_req_kg_per_ha=60, p_req_kg_per_ha=30, k_req_kg_per_ha=30, water_reqs_mm_season=300, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=120, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.50, kc_mid=1.00, kc_end=0.50, preferred_soil_types=["Sandy", "Loamy"], optimal_altitude_min=2000.0, optimal_altitude_max=4000.0),
    "Buckwheat": CropRequirement(name="Buckwheat", optimal_temp_min=18.0, optimal_temp_max=23.0, absolute_temp_min=0.0, absolute_temp_max=35.0, ph_min=5.0, ph_max=7.5, n_req_kg_per_ha=50, p_req_kg_per_ha=30, k_req_kg_per_ha=30, water_reqs_mm_season=400, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=90, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.40, kc_mid=1.10, kc_end=0.50, preferred_soil_types=["Loamy", "Sandy"], optimal_altitude_min=1000.0, optimal_altitude_max=3500.0),
    "Amaranth": CropRequirement(name="Amaranth", optimal_temp_min=25.0, optimal_temp_max=30.0, absolute_temp_min=8.0, absolute_temp_max=40.0, ph_min=5.5, ph_max=7.5, n_req_kg_per_ha=70, p_req_kg_per_ha=35, k_req_kg_per_ha=35, water_reqs_mm_season=400, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=100, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.50, kc_mid=1.00, kc_end=0.50, preferred_soil_types=["Loamy", "Sandy"], optimal_altitude_min=1000.0, optimal_altitude_max=3500.0),
    "Cowpea": CropRequirement(name="Cowpea", optimal_temp_min=20.0, optimal_temp_max=35.0, absolute_temp_min=15.0, absolute_temp_max=40.0, ph_min=5.5, ph_max=8.0, n_req_kg_per_ha=20, p_req_kg_per_ha=40, k_req_kg_per_ha=30, water_reqs_mm_season=400, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=90, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.40, kc_mid=1.05, kc_end=0.60, preferred_soil_types=["Sandy", "Loamy"], compatible_intercrops=["Maize", "Sorghum"], optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Pigeonpea": CropRequirement(name="Pigeonpea", optimal_temp_min=25.0, optimal_temp_max=35.0, absolute_temp_min=10.0, absolute_temp_max=40.0, ph_min=5.0, ph_max=8.0, n_req_kg_per_ha=20, p_req_kg_per_ha=50, k_req_kg_per_ha=30, water_reqs_mm_season=500, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=150, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.40, kc_mid=1.00, kc_end=0.50, preferred_soil_types=["Loamy", "Sandy"], compatible_intercrops=["Maize"], optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Lentil": CropRequirement(name="Lentil", optimal_temp_min=15.0, optimal_temp_max=25.0, absolute_temp_min=-2.0, absolute_temp_max=35.0, ph_min=6.0, ph_max=8.0, n_req_kg_per_ha=20, p_req_kg_per_ha=40, k_req_kg_per_ha=30, water_reqs_mm_season=350, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=110, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.40, kc_mid=1.00, kc_end=0.30, preferred_soil_types=["Loamy", "Clayey"], compatible_intercrops=["Wheat"], optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Mungbean": CropRequirement(name="Mungbean", optimal_temp_min=27.0, optimal_temp_max=30.0, absolute_temp_min=20.0, absolute_temp_max=40.0, ph_min=6.0, ph_max=7.5, n_req_kg_per_ha=20, p_req_kg_per_ha=40, k_req_kg_per_ha=30, water_reqs_mm_season=400, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=75, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.40, kc_mid=1.00, kc_end=0.35, preferred_soil_types=["Loamy", "Sandy"], compatible_intercrops=["Rice", "Maize"], optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Peas": CropRequirement(name="Peas", optimal_temp_min=15.0, optimal_temp_max=20.0, absolute_temp_min=0.0, absolute_temp_max=30.0, ph_min=6.0, ph_max=7.5, n_req_kg_per_ha=20, p_req_kg_per_ha=40, k_req_kg_per_ha=30, water_reqs_mm_season=400, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=90, tolerant_to_drought=False, tolerant_to_waterlogging=False, kc_initial=0.50, kc_mid=1.15, kc_end=1.00, preferred_soil_types=["Loamy"], has_multiple_harvests=True, harvest_interval_days=7, optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Sweet Potato": CropRequirement(name="Sweet Potato", optimal_temp_min=21.0, optimal_temp_max=29.0, absolute_temp_min=10.0, absolute_temp_max=38.0, ph_min=5.5, ph_max=6.5, n_req_kg_per_ha=50, p_req_kg_per_ha=50, k_req_kg_per_ha=100, water_reqs_mm_season=500, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=120, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.50, kc_mid=1.15, kc_end=0.65, preferred_soil_types=["Sandy", "Loamy"], is_shade_tolerant=True, optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Cassava": CropRequirement(name="Cassava", optimal_temp_min=25.0, optimal_temp_max=29.0, absolute_temp_min=18.0, absolute_temp_max=38.0, ph_min=4.5, ph_max=7.5, n_req_kg_per_ha=50, p_req_kg_per_ha=30, k_req_kg_per_ha=100, water_reqs_mm_season=800, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=300, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.30, kc_mid=0.80, kc_end=0.30, preferred_soil_types=["Sandy", "Loamy", "Red"], is_shade_tolerant=True, optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Yam": CropRequirement(name="Yam", optimal_temp_min=25.0, optimal_temp_max=30.0, absolute_temp_min=20.0, absolute_temp_max=35.0, ph_min=5.5, ph_max=6.5, n_req_kg_per_ha=60, p_req_kg_per_ha=40, k_req_kg_per_ha=80, water_reqs_mm_season=1000, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=200, tolerant_to_drought=False, tolerant_to_waterlogging=False, kc_initial=0.50, kc_mid=1.10, kc_end=0.60, preferred_soil_types=["Loamy", "Red"], optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Taro": CropRequirement(name="Taro", optimal_temp_min=25.0, optimal_temp_max=30.0, absolute_temp_min=15.0, absolute_temp_max=35.0, ph_min=5.5, ph_max=7.0, n_req_kg_per_ha=80, p_req_kg_per_ha=40, k_req_kg_per_ha=100, water_reqs_mm_season=1500, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=250, tolerant_to_drought=False, tolerant_to_waterlogging=True, kc_initial=0.50, kc_mid=1.05, kc_end=0.60, preferred_soil_types=["Clayey", "Loamy"], is_shade_tolerant=True, optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Radish": CropRequirement(name="Radish", optimal_temp_min=10.0, optimal_temp_max=25.0, absolute_temp_min=0.0, absolute_temp_max=35.0, ph_min=6.0, ph_max=7.5, n_req_kg_per_ha=50, p_req_kg_per_ha=30, k_req_kg_per_ha=50, water_reqs_mm_season=300, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=45, tolerant_to_drought=False, tolerant_to_waterlogging=False, kc_initial=0.50, kc_mid=1.00, kc_end=0.80, preferred_soil_types=["Sandy", "Loamy"], is_shade_tolerant=True, optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Turnip": CropRequirement(name="Turnip", optimal_temp_min=10.0, optimal_temp_max=20.0, absolute_temp_min=-5.0, absolute_temp_max=30.0, ph_min=6.0, ph_max=7.5, n_req_kg_per_ha=50, p_req_kg_per_ha=30, k_req_kg_per_ha=50, water_reqs_mm_season=350, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=60, tolerant_to_drought=False, tolerant_to_waterlogging=False, kc_initial=0.50, kc_mid=1.00, kc_end=0.80, preferred_soil_types=["Loamy", "Sandy"], optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Beetroot": CropRequirement(name="Beetroot", optimal_temp_min=15.0, optimal_temp_max=20.0, absolute_temp_min=0.0, absolute_temp_max=35.0, ph_min=6.0, ph_max=7.5, n_req_kg_per_ha=80, p_req_kg_per_ha=40, k_req_kg_per_ha=80, water_reqs_mm_season=400, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=70, tolerant_to_drought=False, tolerant_to_waterlogging=False, kc_initial=0.50, kc_mid=1.05, kc_end=0.95, preferred_soil_types=["Loamy", "Sandy"], optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Cauliflower": CropRequirement(name="Cauliflower", optimal_temp_min=15.0, optimal_temp_max=20.0, absolute_temp_min=-2.0, absolute_temp_max=30.0, ph_min=6.0, ph_max=7.5, n_req_kg_per_ha=120, p_req_kg_per_ha=50, k_req_kg_per_ha=100, water_reqs_mm_season=500, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=80, tolerant_to_drought=False, tolerant_to_waterlogging=False, kc_initial=0.70, kc_mid=1.05, kc_end=0.95, preferred_soil_types=["Loamy", "Clayey"], optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Broccoli": CropRequirement(name="Broccoli", optimal_temp_min=15.0, optimal_temp_max=20.0, absolute_temp_min=-4.0, absolute_temp_max=30.0, ph_min=6.0, ph_max=7.0, n_req_kg_per_ha=120, p_req_kg_per_ha=50, k_req_kg_per_ha=100, water_reqs_mm_season=500, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=80, tolerant_to_drought=False, tolerant_to_waterlogging=False, kc_initial=0.70, kc_mid=1.05, kc_end=0.95, preferred_soil_types=["Loamy", "Clayey"], optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Kale": CropRequirement(name="Kale", optimal_temp_min=10.0, optimal_temp_max=20.0, absolute_temp_min=-5.0, absolute_temp_max=35.0, ph_min=6.0, ph_max=7.5, n_req_kg_per_ha=100, p_req_kg_per_ha=40, k_req_kg_per_ha=80, water_reqs_mm_season=450, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=60, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.70, kc_mid=1.00, kc_end=0.95, preferred_soil_types=["Loamy"], has_multiple_harvests=True, harvest_interval_days=14, optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Lettuce": CropRequirement(name="Lettuce", optimal_temp_min=15.0, optimal_temp_max=20.0, absolute_temp_min=0.0, absolute_temp_max=30.0, ph_min=6.0, ph_max=7.0, n_req_kg_per_ha=60, p_req_kg_per_ha=30, k_req_kg_per_ha=60, water_reqs_mm_season=300, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=45, tolerant_to_drought=False, tolerant_to_waterlogging=False, kc_initial=0.70, kc_mid=1.00, kc_end=0.95, preferred_soil_types=["Loamy", "Sandy"], has_multiple_harvests=True, harvest_interval_days=7, optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Celery": CropRequirement(name="Celery", optimal_temp_min=15.0, optimal_temp_max=20.0, absolute_temp_min=5.0, absolute_temp_max=30.0, ph_min=6.0, ph_max=7.0, n_req_kg_per_ha=100, p_req_kg_per_ha=50, k_req_kg_per_ha=100, water_reqs_mm_season=600, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=100, tolerant_to_drought=False, tolerant_to_waterlogging=False, kc_initial=0.70, kc_mid=1.05, kc_end=0.95, preferred_soil_types=["Loamy"], optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Asparagus": CropRequirement(name="Asparagus", optimal_temp_min=15.0, optimal_temp_max=25.0, absolute_temp_min=-10.0, absolute_temp_max=40.0, ph_min=6.5, ph_max=7.5, n_req_kg_per_ha=80, p_req_kg_per_ha=40, k_req_kg_per_ha=80, water_reqs_mm_season=600, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=730, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.70, kc_mid=0.95, kc_end=0.95, preferred_soil_types=["Sandy", "Loamy"], has_multiple_harvests=True, harvest_interval_days=3, optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Zucchini": CropRequirement(name="Zucchini", optimal_temp_min=20.0, optimal_temp_max=25.0, absolute_temp_min=15.0, absolute_temp_max=35.0, ph_min=6.0, ph_max=7.5, n_req_kg_per_ha=100, p_req_kg_per_ha=50, k_req_kg_per_ha=80, water_reqs_mm_season=500, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=50, tolerant_to_drought=False, tolerant_to_waterlogging=False, kc_initial=0.50, kc_mid=0.95, kc_end=0.75, preferred_soil_types=["Loamy", "Sandy"], has_multiple_harvests=True, harvest_interval_days=3, optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Pumpkin": CropRequirement(name="Pumpkin", optimal_temp_min=20.0, optimal_temp_max=30.0, absolute_temp_min=10.0, absolute_temp_max=38.0, ph_min=6.0, ph_max=7.5, n_req_kg_per_ha=100, p_req_kg_per_ha=50, k_req_kg_per_ha=100, water_reqs_mm_season=600, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=110, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.50, kc_mid=1.00, kc_end=0.80, preferred_soil_types=["Loamy", "Sandy"], optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Bitter Gourd": CropRequirement(name="Bitter Gourd", optimal_temp_min=24.0, optimal_temp_max=27.0, absolute_temp_min=15.0, absolute_temp_max=35.0, ph_min=6.0, ph_max=7.0, n_req_kg_per_ha=80, p_req_kg_per_ha=40, k_req_kg_per_ha=80, water_reqs_mm_season=500, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=70, tolerant_to_drought=False, tolerant_to_waterlogging=False, kc_initial=0.50, kc_mid=1.00, kc_end=0.80, preferred_soil_types=["Loamy", "Sandy"], has_multiple_harvests=True, harvest_interval_days=5, optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Bottle Gourd": CropRequirement(name="Bottle Gourd", optimal_temp_min=24.0, optimal_temp_max=27.0, absolute_temp_min=15.0, absolute_temp_max=35.0, ph_min=6.0, ph_max=7.0, n_req_kg_per_ha=80, p_req_kg_per_ha=40, k_req_kg_per_ha=80, water_reqs_mm_season=500, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=70, tolerant_to_drought=False, tolerant_to_waterlogging=False, kc_initial=0.50, kc_mid=1.00, kc_end=0.80, preferred_soil_types=["Loamy", "Sandy"], has_multiple_harvests=True, harvest_interval_days=5, optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Ridge Gourd": CropRequirement(name="Ridge Gourd", optimal_temp_min=25.0, optimal_temp_max=30.0, absolute_temp_min=15.0, absolute_temp_max=35.0, ph_min=6.5, ph_max=7.5, n_req_kg_per_ha=80, p_req_kg_per_ha=40, k_req_kg_per_ha=80, water_reqs_mm_season=500, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=60, tolerant_to_drought=False, tolerant_to_waterlogging=False, kc_initial=0.50, kc_mid=1.00, kc_end=0.80, preferred_soil_types=["Loamy", "Sandy"], has_multiple_harvests=True, harvest_interval_days=5, optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Ash Gourd": CropRequirement(name="Ash Gourd", optimal_temp_min=25.0, optimal_temp_max=30.0, absolute_temp_min=15.0, absolute_temp_max=38.0, ph_min=6.0, ph_max=7.5, n_req_kg_per_ha=80, p_req_kg_per_ha=40, k_req_kg_per_ha=80, water_reqs_mm_season=500, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=120, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.50, kc_mid=1.00, kc_end=0.80, preferred_soil_types=["Loamy", "Sandy"], optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Apple": CropRequirement(name="Apple", optimal_temp_min=15.0, optimal_temp_max=24.0, absolute_temp_min=-20.0, absolute_temp_max=40.0, ph_min=6.0, ph_max=7.0, n_req_kg_per_ha=100, p_req_kg_per_ha=40, k_req_kg_per_ha=120, water_reqs_mm_season=800, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=1800, tolerant_to_drought=False, tolerant_to_waterlogging=False, kc_initial=0.60, kc_mid=0.90, kc_end=0.70, preferred_soil_types=["Loamy", "Clayey"], has_multiple_harvests=True, harvest_interval_days=365, is_tree_crop=True, optimal_altitude_min=1500.0, optimal_altitude_max=3000.0),
    "Pear": CropRequirement(name="Pear", optimal_temp_min=15.0, optimal_temp_max=25.0, absolute_temp_min=-20.0, absolute_temp_max=40.0, ph_min=6.0, ph_max=7.5, n_req_kg_per_ha=100, p_req_kg_per_ha=40, k_req_kg_per_ha=120, water_reqs_mm_season=800, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=1800, tolerant_to_drought=False, tolerant_to_waterlogging=False, kc_initial=0.60, kc_mid=0.90, kc_end=0.70, preferred_soil_types=["Loamy", "Clayey"], has_multiple_harvests=True, harvest_interval_days=365, is_tree_crop=True, optimal_altitude_min=1000.0, optimal_altitude_max=2500.0),
    "Peach": CropRequirement(name="Peach", optimal_temp_min=15.0, optimal_temp_max=24.0, absolute_temp_min=-15.0, absolute_temp_max=40.0, ph_min=6.0, ph_max=7.5, n_req_kg_per_ha=80, p_req_kg_per_ha=40, k_req_kg_per_ha=100, water_reqs_mm_season=700, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=1460, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.60, kc_mid=0.90, kc_end=0.70, preferred_soil_types=["Loamy", "Sandy"], has_multiple_harvests=True, harvest_interval_days=365, is_tree_crop=True, optimal_altitude_min=1000.0, optimal_altitude_max=2500.0),
    "Plum": CropRequirement(name="Plum", optimal_temp_min=15.0, optimal_temp_max=25.0, absolute_temp_min=-15.0, absolute_temp_max=40.0, ph_min=6.0, ph_max=7.0, n_req_kg_per_ha=80, p_req_kg_per_ha=40, k_req_kg_per_ha=100, water_reqs_mm_season=700, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=1460, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.60, kc_mid=0.90, kc_end=0.70, preferred_soil_types=["Loamy", "Sandy"], has_multiple_harvests=True, harvest_interval_days=365, is_tree_crop=True, optimal_altitude_min=1000.0, optimal_altitude_max=2500.0),
    "Cherry": CropRequirement(name="Cherry", optimal_temp_min=15.0, optimal_temp_max=20.0, absolute_temp_min=-20.0, absolute_temp_max=35.0, ph_min=6.0, ph_max=7.5, n_req_kg_per_ha=60, p_req_kg_per_ha=30, k_req_kg_per_ha=80, water_reqs_mm_season=700, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=1460, tolerant_to_drought=False, tolerant_to_waterlogging=False, kc_initial=0.60, kc_mid=0.90, kc_end=0.70, preferred_soil_types=["Loamy", "Sandy"], has_multiple_harvests=True, harvest_interval_days=365, is_tree_crop=True, optimal_altitude_min=1000.0, optimal_altitude_max=2500.0),
    "Grape": CropRequirement(name="Grape", optimal_temp_min=15.0, optimal_temp_max=30.0, absolute_temp_min=-10.0, absolute_temp_max=40.0, ph_min=6.0, ph_max=7.5, n_req_kg_per_ha=80, p_req_kg_per_ha=40, k_req_kg_per_ha=100, water_reqs_mm_season=600, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=1095, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.30, kc_mid=0.85, kc_end=0.45, preferred_soil_types=["Loamy", "Sandy"], has_multiple_harvests=True, harvest_interval_days=365, is_tree_crop=True, optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Strawberry": CropRequirement(name="Strawberry", optimal_temp_min=15.0, optimal_temp_max=25.0, absolute_temp_min=-5.0, absolute_temp_max=35.0, ph_min=5.5, ph_max=6.5, n_req_kg_per_ha=60, p_req_kg_per_ha=30, k_req_kg_per_ha=80, water_reqs_mm_season=500, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=90, tolerant_to_drought=False, tolerant_to_waterlogging=False, kc_initial=0.40, kc_mid=0.85, kc_end=0.75, preferred_soil_types=["Loamy", "Sandy"], has_multiple_harvests=True, harvest_interval_days=3, optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Blueberry": CropRequirement(name="Blueberry", optimal_temp_min=15.0, optimal_temp_max=25.0, absolute_temp_min=-20.0, absolute_temp_max=35.0, ph_min=4.5, ph_max=5.5, n_req_kg_per_ha=50, p_req_kg_per_ha=30, k_req_kg_per_ha=50, water_reqs_mm_season=600, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=730, tolerant_to_drought=False, tolerant_to_waterlogging=False, kc_initial=0.40, kc_mid=0.80, kc_end=0.60, preferred_soil_types=["Loamy", "Sandy"], has_multiple_harvests=True, harvest_interval_days=365, optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Raspberry": CropRequirement(name="Raspberry", optimal_temp_min=15.0, optimal_temp_max=25.0, absolute_temp_min=-20.0, absolute_temp_max=35.0, ph_min=5.5, ph_max=6.5, n_req_kg_per_ha=60, p_req_kg_per_ha=30, k_req_kg_per_ha=60, water_reqs_mm_season=600, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=730, tolerant_to_drought=False, tolerant_to_waterlogging=False, kc_initial=0.40, kc_mid=0.80, kc_end=0.60, preferred_soil_types=["Loamy", "Sandy"], has_multiple_harvests=True, harvest_interval_days=365, optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Blackberry": CropRequirement(name="Blackberry", optimal_temp_min=15.0, optimal_temp_max=25.0, absolute_temp_min=-20.0, absolute_temp_max=35.0, ph_min=5.5, ph_max=6.5, n_req_kg_per_ha=60, p_req_kg_per_ha=30, k_req_kg_per_ha=60, water_reqs_mm_season=600, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=730, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.40, kc_mid=0.80, kc_end=0.60, preferred_soil_types=["Loamy", "Sandy"], has_multiple_harvests=True, harvest_interval_days=365, optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Pomegranate": CropRequirement(name="Pomegranate", optimal_temp_min=25.0, optimal_temp_max=35.0, absolute_temp_min=-5.0, absolute_temp_max=45.0, ph_min=5.5, ph_max=8.0, n_req_kg_per_ha=100, p_req_kg_per_ha=50, k_req_kg_per_ha=80, water_reqs_mm_season=600, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=1095, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.50, kc_mid=0.80, kc_end=0.50, preferred_soil_types=["Sandy", "Loamy"], has_multiple_harvests=True, harvest_interval_days=365, is_tree_crop=True, optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Guava": CropRequirement(name="Guava", optimal_temp_min=23.0, optimal_temp_max=28.0, absolute_temp_min=5.0, absolute_temp_max=45.0, ph_min=5.5, ph_max=7.5, n_req_kg_per_ha=150, p_req_kg_per_ha=50, k_req_kg_per_ha=100, water_reqs_mm_season=800, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=1095, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.50, kc_mid=0.80, kc_end=0.60, preferred_soil_types=["Loamy", "Sandy"], has_multiple_harvests=True, harvest_interval_days=365, is_tree_crop=True, optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Avocado": CropRequirement(name="Avocado", optimal_temp_min=20.0, optimal_temp_max=30.0, absolute_temp_min=-2.0, absolute_temp_max=40.0, ph_min=6.0, ph_max=7.0, n_req_kg_per_ha=150, p_req_kg_per_ha=50, k_req_kg_per_ha=150, water_reqs_mm_season=1200, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=1460, tolerant_to_drought=False, tolerant_to_waterlogging=False, kc_initial=0.60, kc_mid=0.85, kc_end=0.75, preferred_soil_types=["Loamy", "Sandy"], has_multiple_harvests=True, harvest_interval_days=365, is_tree_crop=True, is_shade_tolerant=True, optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Almond": CropRequirement(name="Almond", optimal_temp_min=15.0, optimal_temp_max=30.0, absolute_temp_min=-10.0, absolute_temp_max=45.0, ph_min=6.5, ph_max=8.0, n_req_kg_per_ha=150, p_req_kg_per_ha=50, k_req_kg_per_ha=150, water_reqs_mm_season=800, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=1460, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.40, kc_mid=0.90, kc_end=0.65, preferred_soil_types=["Sandy", "Loamy"], has_multiple_harvests=True, harvest_interval_days=365, is_tree_crop=True, optimal_altitude_min=600.0, optimal_altitude_max=1800.0),
    "Walnut": CropRequirement(name="Walnut", optimal_temp_min=15.0, optimal_temp_max=25.0, absolute_temp_min=-20.0, absolute_temp_max=38.0, ph_min=6.0, ph_max=7.5, n_req_kg_per_ha=100, p_req_kg_per_ha=50, k_req_kg_per_ha=100, water_reqs_mm_season=800, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=1800, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.50, kc_mid=0.90, kc_end=0.70, preferred_soil_types=["Loamy", "Clayey"], has_multiple_harvests=True, harvest_interval_days=365, is_tree_crop=True, optimal_altitude_min=1000.0, optimal_altitude_max=2500.0),
    "Pecan": CropRequirement(name="Pecan", optimal_temp_min=15.0, optimal_temp_max=28.0, absolute_temp_min=-15.0, absolute_temp_max=45.0, ph_min=6.0, ph_max=7.5, n_req_kg_per_ha=100, p_req_kg_per_ha=50, k_req_kg_per_ha=100, water_reqs_mm_season=1000, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=1800, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.50, kc_mid=0.90, kc_end=0.70, preferred_soil_types=["Loamy", "Clayey"], has_multiple_harvests=True, harvest_interval_days=365, is_tree_crop=True, optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Cashew": CropRequirement(name="Cashew", optimal_temp_min=25.0, optimal_temp_max=30.0, absolute_temp_min=15.0, absolute_temp_max=45.0, ph_min=5.0, ph_max=6.5, n_req_kg_per_ha=100, p_req_kg_per_ha=40, k_req_kg_per_ha=80, water_reqs_mm_season=800, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=1095, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.50, kc_mid=0.85, kc_end=0.60, preferred_soil_types=["Sandy", "Loamy", "Red"], has_multiple_harvests=True, harvest_interval_days=365, is_tree_crop=True, optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Pistachio": CropRequirement(name="Pistachio", optimal_temp_min=20.0, optimal_temp_max=35.0, absolute_temp_min=-10.0, absolute_temp_max=45.0, ph_min=7.0, ph_max=8.5, n_req_kg_per_ha=100, p_req_kg_per_ha=40, k_req_kg_per_ha=80, water_reqs_mm_season=600, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=1800, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.40, kc_mid=0.85, kc_end=0.60, preferred_soil_types=["Sandy", "Loamy"], has_multiple_harvests=True, harvest_interval_days=365, is_tree_crop=True, optimal_altitude_min=600.0, optimal_altitude_max=1800.0),
    "Macadamia": CropRequirement(name="Macadamia", optimal_temp_min=20.0, optimal_temp_max=25.0, absolute_temp_min=0.0, absolute_temp_max=35.0, ph_min=5.0, ph_max=6.5, n_req_kg_per_ha=100, p_req_kg_per_ha=50, k_req_kg_per_ha=100, water_reqs_mm_season=1000, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=1460, tolerant_to_drought=False, tolerant_to_waterlogging=False, kc_initial=0.50, kc_mid=0.85, kc_end=0.70, preferred_soil_types=["Loamy", "Red"], has_multiple_harvests=True, harvest_interval_days=365, is_tree_crop=True, optimal_altitude_min=0.0, optimal_altitude_max=1000.0),
    "Hazelnut": CropRequirement(name="Hazelnut", optimal_temp_min=15.0, optimal_temp_max=20.0, absolute_temp_min=-15.0, absolute_temp_max=30.0, ph_min=6.0, ph_max=7.5, n_req_kg_per_ha=80, p_req_kg_per_ha=40, k_req_kg_per_ha=80, water_reqs_mm_season=800, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=1460, tolerant_to_drought=False, tolerant_to_waterlogging=False, kc_initial=0.50, kc_mid=0.85, kc_end=0.70, preferred_soil_types=["Loamy"], has_multiple_harvests=True, harvest_interval_days=365, is_tree_crop=True, optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Mustard": CropRequirement(name="Mustard", optimal_temp_min=15.0, optimal_temp_max=20.0, absolute_temp_min=0.0, absolute_temp_max=35.0, ph_min=6.0, ph_max=7.5, n_req_kg_per_ha=80, p_req_kg_per_ha=40, k_req_kg_per_ha=40, water_reqs_mm_season=350, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=110, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.35, kc_mid=1.15, kc_end=0.35, preferred_soil_types=["Loamy", "Sandy"], optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Safflower": CropRequirement(name="Safflower", optimal_temp_min=20.0, optimal_temp_max=30.0, absolute_temp_min=0.0, absolute_temp_max=40.0, ph_min=6.0, ph_max=7.5, n_req_kg_per_ha=60, p_req_kg_per_ha=30, k_req_kg_per_ha=30, water_reqs_mm_season=400, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=150, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.35, kc_mid=1.05, kc_end=0.35, preferred_soil_types=["Loamy", "Clayey"], optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Sesame": CropRequirement(name="Sesame", optimal_temp_min=25.0, optimal_temp_max=35.0, absolute_temp_min=10.0, absolute_temp_max=45.0, ph_min=5.5, ph_max=8.0, n_req_kg_per_ha=60, p_req_kg_per_ha=30, k_req_kg_per_ha=30, water_reqs_mm_season=400, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=100, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.35, kc_mid=1.10, kc_end=0.25, preferred_soil_types=["Sandy", "Loamy"], optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Linseed": CropRequirement(name="Linseed", optimal_temp_min=15.0, optimal_temp_max=25.0, absolute_temp_min=0.0, absolute_temp_max=35.0, ph_min=6.0, ph_max=7.5, n_req_kg_per_ha=60, p_req_kg_per_ha=30, k_req_kg_per_ha=30, water_reqs_mm_season=450, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=130, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.30, kc_mid=1.10, kc_end=0.25, preferred_soil_types=["Loamy", "Clayey"], optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Castor": CropRequirement(name="Castor", optimal_temp_min=20.0, optimal_temp_max=30.0, absolute_temp_min=10.0, absolute_temp_max=45.0, ph_min=5.5, ph_max=8.0, n_req_kg_per_ha=80, p_req_kg_per_ha=40, k_req_kg_per_ha=40, water_reqs_mm_season=600, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=180, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.35, kc_mid=1.15, kc_end=0.55, preferred_soil_types=["Sandy", "Loamy"], optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Cacao": CropRequirement(name="Cacao", optimal_temp_min=25.0, optimal_temp_max=28.0, absolute_temp_min=15.0, absolute_temp_max=35.0, ph_min=5.0, ph_max=7.5, n_req_kg_per_ha=150, p_req_kg_per_ha=50, k_req_kg_per_ha=150, water_reqs_mm_season=1500, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=1460, tolerant_to_drought=False, tolerant_to_waterlogging=False, kc_initial=0.90, kc_mid=1.05, kc_end=1.00, preferred_soil_types=["Loamy", "Red"], has_multiple_harvests=True, harvest_interval_days=15, is_tree_crop=True, is_shade_tolerant=True, optimal_altitude_min=0.0, optimal_altitude_max=1200.0),
    "Vanilla": CropRequirement(name="Vanilla", optimal_temp_min=20.0, optimal_temp_max=30.0, absolute_temp_min=15.0, absolute_temp_max=35.0, ph_min=5.5, ph_max=7.0, n_req_kg_per_ha=50, p_req_kg_per_ha=20, k_req_kg_per_ha=60, water_reqs_mm_season=1500, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=1095, tolerant_to_drought=False, tolerant_to_waterlogging=False, kc_initial=0.80, kc_mid=1.00, kc_end=1.00, preferred_soil_types=["Loamy"], has_multiple_harvests=True, harvest_interval_days=365, is_shade_tolerant=True, optimal_altitude_min=0.0, optimal_altitude_max=1200.0),
    "Black Pepper": CropRequirement(name="Black Pepper", optimal_temp_min=20.0, optimal_temp_max=30.0, absolute_temp_min=15.0, absolute_temp_max=40.0, ph_min=5.5, ph_max=6.5, n_req_kg_per_ha=100, p_req_kg_per_ha=40, k_req_kg_per_ha=100, water_reqs_mm_season=2000, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=1095, tolerant_to_drought=False, tolerant_to_waterlogging=False, kc_initial=0.80, kc_mid=1.00, kc_end=1.00, preferred_soil_types=["Loamy", "Red"], has_multiple_harvests=True, harvest_interval_days=365, is_shade_tolerant=True, compatible_intercrops=["Coconut", "Mango"], optimal_altitude_min=0.0, optimal_altitude_max=1200.0),
    "Cardamom": CropRequirement(name="Cardamom", optimal_temp_min=15.0, optimal_temp_max=25.0, absolute_temp_min=10.0, absolute_temp_max=35.0, ph_min=5.5, ph_max=6.5, n_req_kg_per_ha=80, p_req_kg_per_ha=40, k_req_kg_per_ha=120, water_reqs_mm_season=1800, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=730, tolerant_to_drought=False, tolerant_to_waterlogging=False, kc_initial=0.80, kc_mid=1.00, kc_end=1.00, preferred_soil_types=["Loamy", "Red"], has_multiple_harvests=True, harvest_interval_days=45, is_shade_tolerant=True, compatible_intercrops=["Coffee"], optimal_altitude_min=600.0, optimal_altitude_max=1500.0),
    "Clove": CropRequirement(name="Clove", optimal_temp_min=20.0, optimal_temp_max=30.0, absolute_temp_min=15.0, absolute_temp_max=35.0, ph_min=5.5, ph_max=7.0, n_req_kg_per_ha=150, p_req_kg_per_ha=50, k_req_kg_per_ha=150, water_reqs_mm_season=1500, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=1825, tolerant_to_drought=False, tolerant_to_waterlogging=False, kc_initial=0.80, kc_mid=0.95, kc_end=0.95, preferred_soil_types=["Loamy", "Red"], has_multiple_harvests=True, harvest_interval_days=365, is_tree_crop=True, optimal_altitude_min=0.0, optimal_altitude_max=1200.0),
    "Cinnamon": CropRequirement(name="Cinnamon", optimal_temp_min=20.0, optimal_temp_max=30.0, absolute_temp_min=15.0, absolute_temp_max=35.0, ph_min=4.5, ph_max=5.5, n_req_kg_per_ha=150, p_req_kg_per_ha=50, k_req_kg_per_ha=100, water_reqs_mm_season=2000, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=1095, tolerant_to_drought=False, tolerant_to_waterlogging=False, kc_initial=0.80, kc_mid=0.95, kc_end=0.95, preferred_soil_types=["Loamy", "Red"], has_multiple_harvests=True, harvest_interval_days=365, is_tree_crop=True, optimal_altitude_min=0.0, optimal_altitude_max=1200.0),
    "Tobacco": CropRequirement(name="Tobacco", optimal_temp_min=20.0, optimal_temp_max=30.0, absolute_temp_min=10.0, absolute_temp_max=40.0, ph_min=5.5, ph_max=6.5, n_req_kg_per_ha=100, p_req_kg_per_ha=60, k_req_kg_per_ha=120, water_reqs_mm_season=600, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=120, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.40, kc_mid=1.15, kc_end=0.80, preferred_soil_types=["Sandy", "Loamy"], has_multiple_harvests=True, harvest_interval_days=15, optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Jute": CropRequirement(name="Jute", optimal_temp_min=25.0, optimal_temp_max=35.0, absolute_temp_min=15.0, absolute_temp_max=40.0, ph_min=5.5, ph_max=7.5, n_req_kg_per_ha=80, p_req_kg_per_ha=40, k_req_kg_per_ha=40, water_reqs_mm_season=1000, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=120, tolerant_to_drought=False, tolerant_to_waterlogging=True, kc_initial=0.40, kc_mid=1.15, kc_end=1.00, preferred_soil_types=["Loamy", "Clayey"], optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Hemp": CropRequirement(name="Hemp", optimal_temp_min=15.0, optimal_temp_max=25.0, absolute_temp_min=5.0, absolute_temp_max=35.0, ph_min=6.0, ph_max=7.5, n_req_kg_per_ha=150, p_req_kg_per_ha=50, k_req_kg_per_ha=100, water_reqs_mm_season=600, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=120, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.40, kc_mid=1.15, kc_end=0.80, preferred_soil_types=["Loamy", "Sandy"], optimal_altitude_min=0.0, optimal_altitude_max=3000.0),
    "Teff": CropRequirement(name="Teff", optimal_temp_min=15.0, optimal_temp_max=25.0, absolute_temp_min=5.0, absolute_temp_max=35.0, ph_min=5.5, ph_max=8.0, n_req_kg_per_ha=60, p_req_kg_per_ha=30, k_req_kg_per_ha=30, water_reqs_mm_season=350, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=90, tolerant_to_drought=True, tolerant_to_waterlogging=True, kc_initial=0.30, kc_mid=1.00, kc_end=0.30, preferred_soil_types=["Sandy", "Loamy"], optimal_altitude_min=1500.0, optimal_altitude_max=2800.0),
    "Lima Bean": CropRequirement(name="Lima Bean", optimal_temp_min=20.0, optimal_temp_max=25.0, absolute_temp_min=10.0, absolute_temp_max=35.0, ph_min=5.5, ph_max=6.5, n_req_kg_per_ha=20, p_req_kg_per_ha=40, k_req_kg_per_ha=40, water_reqs_mm_season=500, root_depth_min_mm=300, root_depth_max_mm=1200, days_to_maturity=120, tolerant_to_drought=True, tolerant_to_waterlogging=False, kc_initial=0.40, kc_mid=1.05, kc_end=0.60, preferred_soil_types=["Loamy", "Sandy"], compatible_intercrops=["Maize"], optimal_altitude_min=0.0, optimal_altitude_max=3000.0)
}

def get_crop_requirements(crop_name: str) -> CropRequirement:
    """Returns the requirements for a given crop, or None if unknown."""
    # Normalize
    name = crop_name.title() if crop_name else ""
    return CROP_DB.get(name)

def get_all_supported_crops() -> List[str]:
    """Returns a list of all supported crop names."""
    return list(CROP_DB.keys())

# Import extension database and update the primary engine dictionary


