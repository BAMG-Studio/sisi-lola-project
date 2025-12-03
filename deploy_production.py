"""
Production deployment script with validation
"""
import os
import sys
import subprocess
from pathlib import Path

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
    
    # Step 4: Install production dependencies
    print("\nInstalling production dependencies...")
    subprocess.run([
        sys.executable, "-m", "pip", "install",
        "-r", "sisi_lola_api/requirements.txt",
        "-r", "sisi_lola_api/requirements_control_center.txt",
        "gunicorn", "psycopg2-binary"
    ])
    
    # Step 5: Initialize database
    print("\nInitializing database...")
    sys.path.insert(0, 'sisi_lola_api')
    from app.database import init_db
    init_db()
    
    # Step 6: Create admin if needed
    print("\nSetting up admin user...")
    subprocess.run([sys.executable, "create_admin.py"])
    
    print("\n" + "=" * 60)
    print("✅ DEPLOYMENT COMPLETE - READY FOR PRODUCTION")
    print("=" * 60)
    print("\nProduction checklist:")
    print("[ ] Change JWT_SECRET_KEY to secure random value")
    print("[ ] Switch DATABASE_URL to PostgreSQL")
    print("[ ] Configure HTTPS/SSL")
    print("[ ] Set up monitoring (Sentry, Datadog)")
    print("[ ] Configure automated backups")
    print("[ ] Review CORS_ORIGINS")
    print("[ ] Enable rate limiting")
    print("[ ] Set up CI/CD pipeline")
    print("\nStart production server:")
    print("cd sisi_lola_api")
    print("gunicorn app.main:app --bind 0.0.0.0:8000 --workers 4")
    
    return True

if __name__ == "__main__":
    success = deploy()
    sys.exit(0 if success else 1)
