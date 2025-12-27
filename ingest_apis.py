import os

def ingest_env_example():
    example_path = "sisi_lola_api/.env.example"
    actual_path = "sisi_lola_api/.env"
    
    if not os.path.exists(example_path):
        print(f"❌ Could not find {example_path}")
        return

    print(f"🚀 INGESTING API KEYS FROM {example_path}...")
    
    with open(example_path, "r") as f:
        lines = f.readlines()

    # Read existing .env to avoid overwriting unless necessary
    existing_vars = {}
    if os.path.exists(actual_path):
        with open(actual_path, "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, val = line.split("=", 1)
                    existing_vars[key.strip()] = val.strip()

    # Update with example vars if they are placeholder values in .env or missing
    new_lines = []
    for line in lines:
        if "=" in line and not line.startswith("#"):
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip()
            
            # If the variable exists and isn't just a placeholder, keep it
            # Otherwise, use the one from .env.example
            if key in existing_vars and existing_vars[key] and "your-" not in existing_vars[key].lower():
                new_lines.append(f"{key}={existing_vars[key]}\n")
            else:
                new_lines.append(f"{key}={val}\n")
        else:
            new_lines.append(line)

    with open(actual_path, "w") as f:
        f.writelines(new_lines)

    print(f"✅ SUCCESS: {actual_path} is now fully super-charged with all APIs!")

if __name__ == "__main__":
    ingest_env_example()
