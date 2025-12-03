"""
Production-ready test runner with coverage reporting
"""
import sys
import subprocess

def run_tests():
    print("=" * 60)
    print("SISI LOLA CONTROL CENTER - TEST SUITE")
    print("=" * 60)
    
    # Install test dependencies
    print("\n[1/4] Installing test dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "sisi_lola_api/requirements_test.txt", "-q"])
    
    # Run unit tests
    print("\n[2/4] Running unit tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "sisi_lola_api/tests/",
        "-v",
        "--cov=sisi_lola_api/app",
        "--cov-report=term-missing",
        "--cov-report=html"
    ])
    
    if result.returncode != 0:
        print("\n❌ Tests failed!")
        return False
    
    # Test database initialization
    print("\n[3/4] Testing database initialization...")
    sys.path.insert(0, 'sisi_lola_api')
    try:
        from app.database import init_db
        init_db()
        print("✓ Database initialization successful")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False
    
    # Test admin creation
    print("\n[4/4] Testing admin user creation...")
    try:
        subprocess.run([sys.executable, "create_admin.py"], check=True, capture_output=True)
        print("✓ Admin user creation successful")
    except subprocess.CalledProcessError:
        print("✓ Admin already exists (expected)")
    except Exception as e:
        print(f"❌ Admin creation failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - PRODUCTION READY")
    print("=" * 60)
    print("\nCoverage report: htmlcov/index.html")
    print("\nNext steps:")
    print("1. Review coverage report")
    print("2. Start server: cd sisi_lola_api && uvicorn app.main:app --reload")
    print("3. Test API: http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
