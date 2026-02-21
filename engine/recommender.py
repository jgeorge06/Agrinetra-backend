
from .constants import CROP_NPK_REQUIREMENTS, CROP_FERTILIZER_RULES
import math

class Recommender:
    def __init__(self):
        pass

    def get_fertilizer_recommendation(self, crop_name, soil_n, soil_p, soil_k):
        """
        Generates fertilizer recommendations based on soil health and crop requirements.
        """
        # Normalize crop name (title case)
        crop = crop_name.title() if crop_name else ""
        
        # 1. Check if crop data exists
        if crop not in CROP_NPK_REQUIREMENTS:
            return ["General NPK Fertilizer (Crop data not found)"]

        required = CROP_NPK_REQUIREMENTS[crop]
        recommendations = []
        
        # Margin of error (e.g. if soil has 85% of required, it might be 'enough')
        margin = 0.85

        # 2. Analyze Deficiencies
        is_n_low = soil_n < required['Nitrogen'] * margin
        is_p_low = soil_p < required['Phosphorous'] * margin
        is_k_low = soil_k < required['Potassium'] * margin

        # 3. Select Fertilizers based on Crop Rules
        allowed_ferts = CROP_FERTILIZER_RULES.get(crop, ["Urea", "DAP", "MOP"]) # Default to all 3 if unknown

        if is_n_low:
            if "Urea" in allowed_ferts: recommendations.append("Urea (Nitrogen Source)")
            elif "DAP" in allowed_ferts: recommendations.append("DAP (Partial Nitrogen Source)")

        if is_p_low:
            if "DAP" in allowed_ferts: recommendations.append("DAP (Phosphorous Source)")
            elif "SSP" in allowed_ferts: recommendations.append("SSP (Single Super Phosphate)")

        if is_k_low:
            if "MOP" in allowed_ferts: recommendations.append("MOP (Potassium Source)")

        # 4. Fallback
        if not recommendations:
            if is_n_low or is_p_low or is_k_low:
                 recommendations.append("Apply NPK Complex Fertilizer (19:19:19)")
            else:
                 recommendations.append("Soil is healthy. No major fertilizers required.")

        return list(set(recommendations)) # Remove duplicates

    def analyze_health_status(self, crop, n, p, k):
        """
        Returning a simple health status string.
        """
        required = CROP_NPK_REQUIREMENTS.get(crop.title())
        if not required: return "Unknown"

        score = 0
        if n >= required['Nitrogen'] * 0.8: score += 1
        if p >= required['Phosphorous'] * 0.8: score += 1
        if k >= required['Potassium'] * 0.8: score += 1
        
        if score == 3: return "Excellent"
        if score == 2: return "Good"
        return "Needs Attention"

    def recommend_crops(self, n, p, k, temp, humidity, soil_type, moisture):
        """
        Recommends crops based on soil parameters (suitability score).
        Since ML models are opaque/broken, we use a suitability matching algorithm
        based on the known ideal NPK requirements.
        """
        suitability_scores = []

        for crop, requirements in CROP_NPK_REQUIREMENTS.items():
            # Calculate distance between soil NPK and crop requirement
            # Smaller distance = better fit
            
            # Normalize diffs to avoid skew
            n_diff = abs(n - requirements['Nitrogen']) / 100
            p_diff = abs(p - requirements['Phosphorous']) / 100
            k_diff = abs(k - requirements['Potassium']) / 100
            
            # Simple Euclidean-like distance
            distance = math.sqrt(n_diff**2 + p_diff**2 + k_diff**2)
            
            # Convert distance to a score (0 to 100)
            # This is a heuristic: closer is better
            score = max(0, 100 - (distance * 20)) 
            
            suitability_scores.append({
                "crop": crop,
                "score": round(score, 2),
                "requirements": requirements
            })

        # Sort by score descending
        suitability_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top 5
        return suitability_scores[:5]
