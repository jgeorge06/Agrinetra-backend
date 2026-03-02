import re

def patch_crop_db():
    filepath = "C:/Users/91906/Programs/Agrinetra-backend/engine/crop_db.py"
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    # 1. Update Dataclass
    content = content.replace(
        "is_rainfed_only: bool = False        # Useful for crops generally not manually irrigated",
        "rainfed_after_days: int = -1         # Days after planting when the crop becomes strictly rainfed (-1 = never)"
    )
    content = content.replace(
        '"is_rainfed_only": self.is_rainfed_only,',
        '"rainfed_after_days": self.rainfed_after_days,'
    )
    
    # 2. Iterate and patch each crop entry
    # Find all crop instantiations: "Name": CropRequirement(...)
    pattern = re.compile(r'(\s*")([^"]+)("\s*:\s*CropRequirement\s*\()([\s\S]*?)(\n\s*\),?)')
    
    def replacer(match):
        prefix = match.group(1)
        crop_name = match.group(2)
        mid = match.group(3)
        body = match.group(4)
        suffix = match.group(5)
        
        # Remove old flag if present
        body = re.sub(r',\s*is_rainfed_only=True', '', body)
        body = re.sub(r',\s*is_rainfed_only=False', '', body)
        
        rainfed_val = -1
        
        # Heuristics for rainfed logic
        if "is_tree_crop=True" in body or "has_multiple_harvests=True" in body and "Rubber" in crop_name:
             # Most mature trees/orchards become rainfed after 2-3 years (sapling establishment)
             # Let's say 1095 days (3 years), except for Rubber which we will set to 1095.
             if crop_name in ["Rubber", "Cashew", "Coconut", "Arecanut", "Oil Palm", "Teak", "Cocoa", "Coffee"]:
                 rainfed_val = 1095
             elif crop_name in ["Mango", "Jackfruit", "Tamarind", "Nutmeg", "Clove", "Cinnamon"]:
                 rainfed_val = 1460 # 4 years for larger trees
             
        # Known dryland field crops are instantly rainfed (0 days) if they are typically grown without irrigation
        elif crop_name in ["Pearl Millet", "Finger Millet", "Sorghum", "Foxtail Millet", "Little Millet", "Kodo Millet"]:
             rainfed_val = 0
             
        # Append the new field before the last parameter
        if rainfed_val != -1:
            body = body + f", rainfed_after_days={rainfed_val}"
            
        return prefix + crop_name + mid + body + suffix

    new_content = pattern.sub(replacer, content)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
        
    print("Successfully patched crop_db.py with rainfed_after_days.")

if __name__ == "__main__":
    patch_crop_db()
