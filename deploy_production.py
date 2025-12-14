"""
Production deployment script with validation and model auto-selection

Features:
- Environment validation
- Test suite execution
- Database backup
- Automatic best model selection from registry
- Health checks
"""
import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime


def check_environment():
    print("Checking environment variables...")
    required = ["JWT_SECRET_KEY", "DATABASE_URL", "CORS_ORIGINS"]
    missing = [var for var in required if not os.getenv(var)]
    
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        return False
    
    if os.getenv("JWT_SECRET_KEY") == "sisi-lola-jwt-secret-key-2025-production-change-this":
        print("⚠️  WARNING: Using default JWT secret! Change in production!")
    
    print("✓ Environment variables configured")
    return True


def select_best_model():
    """
    Select the best model from the registry based on evaluation scores.
    
    Returns:
        dict: Selected model info or None if no suitable model found
    """
    print("\nSelecting best model from registry...")
    
    registry_path = Path("ml_training/configs/model_registry.json")
    
    if not registry_path.exists():
        print("⚠️  Model registry not found. Using default model.")
        return None
    
    with open(registry_path) as f:
        registry = json.load(f)
    
    # Check if there's a recommended model
    recommended = registry.get("recommended_model")
    if recommended:
        print(f"✓ Found recommended model: {recommended}")
        return {"model_path": recommended, "source": "recommended"}
    
    # Otherwise, find best from models list
    models = registry.get("models", [])
    criteria = registry.get("selection_criteria", {})
    
    min_total = criteria.get("min_total_score", 0.7)
    min_safety = criteria.get("min_safety_score", 0.8)
    min_identity = criteria.get("min_identity_score", 0.7)
    max_time = criteria.get("max_response_time_ms", 5000)
    
    eligible_models = []
    for model in models:
        # Check if meets criteria
        if model.get("total_score", 0) < min_total:
            continue
        if model.get("safety_score", 0) < min_safety:
            continue
        if model.get("identity_score", 0) < min_identity:
            continue
        if model.get("avg_response_time_ms", float("inf")) > max_time:
            continue
        
        eligible_models.append(model)
    
    if not eligible_models:
        print("⚠️  No models meet selection criteria. Using default.")
        return None
    
    # Sort by total_score and pick best
    eligible_models.sort(key=lambda x: x.get("total_score", 0), reverse=True)
    best = eligible_models[0]
    
    print(f"✓ Selected model: {best.get('model_id', 'unknown')}")
    print(f"  Total score: {best.get('total_score', 0):.3f}")
    print(f"  Safety score: {best.get('safety_score', 0):.3f}")
    print(f"  Response time: {best.get('avg_response_time_ms', 0):.0f}ms")
    
    return best


def configure_model(model_info):
    """Configure the application to use the selected model"""
    if model_info is None:
        return True
    
    print("\nConfiguring selected model...")
    
    model_path = model_info.get("model_path") or model_info.get("model_id")
    
    if model_path:
        # Set environment variable for the app to use
        os.environ["SISI_LOLA_MODEL_PATH"] = str(model_path)
        
        # Also save to a config file for persistence
        config_path = Path("sisi_lola_api/model_config.json")
        config = {
            "model_path": str(model_path),
            "model_id": model_info.get("model_id", "unknown"),
            "configured_at": datetime.now().isoformat(),
            "scores": {
                "total": model_info.get("total_score"),
                "safety": model_info.get("safety_score"),
                "identity": model_info.get("identity_score")
            }
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✓ Model configuration saved to {config_path}")
    
    return True

def run_tests():
    print("\nRunning test suite...")
    result = subprocess.run([sys.executable, "run_tests.py"])
    return result.returncode == 0

def backup_database():
    print("\nBacking up database...")
    db_path = Path("sisi_lola_api/sisi_lola_control.db")
    if db_path.exists():
        backup_path = db_path.with_suffix(".db.backup")
        import shutil
        shutil.copy(db_path, backup_path)
        print(f"✓ Database backed up to {backup_path}")
    return True

def deploy():
    print("=" * 60)
    print("SISI LOLA CONTROL CENTER - PRODUCTION DEPLOYMENT")
    print("=" * 60)
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv("sisi_lola_api/.env")
    
    # Step 1: Check environment
    if not check_environment():
        return False
    
    # Step 2: Run tests
    if not run_tests():
        print("\n❌ Tests failed. Fix issues before deploying.")
        return False
    
    # Step 3: Backup database
    if not backup_database():
        return False
    
    # Step 4: Select and configure best model
    best_model = select_best_model()
    if not configure_model(best_model):
        return False
    
    # Step 5: Install production dependencies
    print("\nInstalling production dependencies...")
    subprocess.run([
        sys.executable, "-m", "pip", "install",
        "-r", "sisi_lola_api/requirements.txt",
        "-r", "sisi_lola_api/requirements_control_center.txt",
        "gunicorn", "psycopg2-binary"
    ])
    
    # Step 6: Initialize database
    print("\nInitializing database...")
    sys.path.insert(0, 'sisi_lola_api')
    from app.database import init_db
    init_db()
    
    # Step 7: Create admin if needed
    print("\nSetting up admin user...")
    subprocess.run([sys.executable, "create_admin.py"])
    
    print("\n" + "=" * 60)
    print("✅ DEPLOYMENT COMPLETE - READY FOR PRODUCTION")
    print("=" * 60)
    
    # Show model info
    if best_model:
        print(f"\n🧠 Active Model: {best_model.get('model_id', best_model.get('model_path', 'default'))}")
    
    print("\nProduction checklist:")
    print("[ ] Change JWT_SECRET_KEY to secure random value")
    print("[ ] Switch DATABASE_URL to PostgreSQL")
    print("[ ] Configure HTTPS/SSL")
    print("[ ] Set up monitoring (Sentry, Datadog)")
    print("[ ] Configure automated backups")
    print("[ ] Review CORS_ORIGINS")
    print("[ ] Enable rate limiting")
    print("[ ] Set up CI/CD pipeline")
    print("[ ] Run model comparison (python ml_training/scripts/compare_models.py --all)")
    print("\nStart production server:")
    print("cd sisi_lola_api")
    print("gunicorn app.main:app --bind 0.0.0.0:8000 --workers 4")
    
    return True

if __name__ == "__main__":
    success = deploy()
    sys.exit(0 if success else 1)
