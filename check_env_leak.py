import os

env_path = os.path.join("sisi_lola_api", ".env")

if os.path.exists(env_path):
    with open(env_path, "r") as f:
        lines = f.readlines()
    
    print("Checking for whitespace/unseen characters in critical keys:")
    for line in lines:
        if "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            val = value.strip()
            if key in ["DISCORD_BOT_TOKEN", "YOUTUBE_API_KEY"]:
                print(f"Key: {key}")
                print(f"Value Length: {len(val)}")
                print(f"Starts with space: {value.startswith(' ')}")
                print(f"Ends with space: {value.endswith(' ')}")
                if key == "DISCORD_BOT_TOKEN":
                    # Check for accidental newline or triple quotes if the user copy-pasted weirdly
                    print(f"Contains newline: {'\\n' in value}")
                    
else:
    print("No .env found")
