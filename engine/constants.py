
# Crop NPK Requirements (Nitrogen, Phosphorous, Potassium)
# Extracted from crop_ml_model/crop_npk_requirements.pkl
CROP_NPK_REQUIREMENTS = {
    'Apple': {'Nitrogen': 20, 'Phosphorous': 125, 'Potassium': 200},
    'Banana': {'Nitrogen': 100, 'Phosphorous': 75, 'Potassium': 50},
    'Blackgram': {'Nitrogen': 40, 'Phosphorous': 60, 'Potassium': 20},
    'Chickpea': {'Nitrogen': 40, 'Phosphorous': 60, 'Potassium': 80},
    'Coconut': {'Nitrogen': 20, 'Phosphorous': 125, 'Potassium': 200},
    'Coffee': {'Nitrogen': 100, 'Phosphorous': 20, 'Potassium': 30},
    'Cotton': {'Nitrogen': 120, 'Phosphorous': 40, 'Potassium': 20},
    'Grapes': {'Nitrogen': 20, 'Phosphorous': 125, 'Potassium': 200},
    'Jute': {'Nitrogen': 80, 'Phosphorous': 40, 'Potassium': 40},
    'Kidneybeans': {'Nitrogen': 20, 'Phosphorous': 60, 'Potassium': 20},
    'Lentil': {'Nitrogen': 20, 'Phosphorous': 60, 'Potassium': 20},
    'Maize': {'Nitrogen': 80, 'Phosphorous': 40, 'Potassium': 20},
    'Mango': {'Nitrogen': 20, 'Phosphorous': 20, 'Potassium': 30},
    'Mothbeans': {'Nitrogen': 20, 'Phosphorous': 40, 'Potassium': 20},
    'Mungbean': {'Nitrogen': 20, 'Phosphorous': 40, 'Potassium': 20},
    'Muskmelon': {'Nitrogen': 100, 'Phosphorous': 10, 'Potassium': 50},
    'Orange': {'Nitrogen': 20, 'Phosphorous': 10, 'Potassium': 10},
    'Papaya': {'Nitrogen': 50, 'Phosphorous': 50, 'Potassium': 50},
    'Pigeonpeas': {'Nitrogen': 20, 'Phosphorous': 60, 'Potassium': 20},
    'Pomegranate': {'Nitrogen': 20, 'Phosphorous': 10, 'Potassium': 40},
    'Rice': {'Nitrogen': 80, 'Phosphorous': 40, 'Potassium': 40},
    'Watermelon': {'Nitrogen': 100, 'Phosphorous': 10, 'Potassium': 50}
}

# Crop Specific Fertilizer Rules
CROP_FERTILIZER_RULES = {
    "Pulses": ["DAP", "MOP"],          # nitrogen fixing
    "Paddy": ["Urea", "DAP"],
    "Oil seeds": ["DAP", "MOP"],
    "Sugarcane": ["Urea", "MOP"],
    "Barley": ["Urea", "DAP"],
    "Tobacco": ["Urea", "DAP", "MOP"],
    "Ground Nuts": ["DAP", "MOP"],
    "Cotton": ["Urea", "DAP", "MOP"],
    "Millets": ["DAP"],
    "Maize": ["Urea", "DAP", "MOP"]
}
