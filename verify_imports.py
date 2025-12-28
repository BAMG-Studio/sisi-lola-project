
import os
import sys
sys.path.append(os.getcwd())
try:
    from sisi_lola_api.app.services.api_manager import get_api_manager
    print("✅ API Manager Import Successful")
    from sisi_lola_api.app.services.google_creative_service import get_google_creative_service
    print("✅ Google Creative Service Import Successful")
    from sisi_lola_api.app.routers.vibe_router import router
    print("✅ Vibe Router Import Successful")
    from sisi_lola_api.app.main_updated import app
    print("✅ Main App Import Successful")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
