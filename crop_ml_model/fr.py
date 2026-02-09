import joblib

# Load crop-wise NPK requirement table
crop_npk = joblib.load("crop_npk_requirements.pkl")

def recommend_fertilizer(crop, soil_N, soil_P, soil_K):
    """
    Recommend fertilizer based on NPK deficiency
    """

    if crop not in crop_npk.index:
        return ["General NPK"]

    req = crop_npk.loc[crop]
    fertilizers = []

    # Nitrogen
    if soil_N < req["Nitrogen"]:
        fertilizers.append("Urea")

    # Phosphorous
    if soil_P < req["Phosphorous"]:
        fertilizers.append("DAP")

    # Potassium
    if soil_K < req["Potassium"]:
        fertilizers.append("MOP")

    if not fertilizers:
        return ["No fertilizer required"]

    return fertilizers
