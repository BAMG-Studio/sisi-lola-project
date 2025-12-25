import os

# Files that contain hardcoded secrets
SECRET_FILES = [
    "inject_ig_token.py",
    "append_credentials.py",
    "final_config_sync.py",
    "update_dropbox_creds.py",
    "update_meta_ids.py",
    "sanitize_keys.py",
    "force_fix_youtube.py",
    "sisi_lola_api/app/services/api_manager.py"
]

def sanitize():
    print("🧹 SISI LOLA: SANITIZING CODE FOR GITHUB PUSH...")
    
    for filename in SECRET_FILES:
        if os.path.exists(filename):
            print(f"🗑️  Removing secret file: {filename}")
            # Instead of deleting, we replace with a placeholder version
            with open(filename, "w") as f:
                f.write("# This file was sanitized to remove secrets before GitHub push.\n")
                f.write("# Use .env for all sensitive keys.\n")
            
    print("\n✅ Code sanitized! GitHub should now allow the push.")
    print("⚠️  NOTE: Your .env is SAFE (it's in .gitignore).")

if __name__ == "__main__":
    sanitize()
