import json
import ast

def fix_and_save_json_string(json_like_str, output_filename="output.json"):
    try:
        # Step 1: Convert pseudo-JSON string to Python dict safely
        data = ast.literal_eval(json_like_str)

        # Step 2: Dump proper JSON to file
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        print(f"✅ JSON saved successfully to '{output_filename}'")
        return True

    except (ValueError, SyntaxError) as e:
        print("❌ Conversion failed:", e)
        return False




