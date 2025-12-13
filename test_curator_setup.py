"""
Quick test for Voice Dataset Curator Integration

Run this to verify the curator system is properly set up.
"""

import json
import sys
from pathlib import Path

# Add paths - project root
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "sisi_lola_api"))

def test_curator_files():
    """Verify all curator files exist"""
    print("=" * 60)
    print("🔍 Testing Voice Dataset Curator Setup")
    print("=" * 60)
    
    curator_dir = PROJECT_ROOT / "ml_training" / "curator"
    
    required_files = [
        "african_language_datasets_catalog.csv",
        "audio_processing_recipes.py",
        "curator_manifest_schema.py",
        "dataset_licenses_guide.md",
        "language_coverage_matrix.json",
        "README.md",
        "CUSTOM_GPT_INSTRUCTIONS.md",
        "__init__.py"
    ]
    
    print("\n📁 Checking curator files...")
    all_exist = True
    for filename in required_files:
        path = curator_dir / filename
        if path.exists():
            print(f"  ✅ {filename}")
        else:
            print(f"  ❌ {filename} - MISSING")
            all_exist = False
    
    return all_exist


def test_manifest_schema():
    """Test the manifest schema"""
    print("\n📋 Testing manifest schema...")
    
    try:
        from ml_training.curator import CuratedDatasetManifest, CuratedSample, AudioSpecs
        
        # Create a test sample
        sample = CuratedSample(
            audio_path="test.wav",
            text="Ẹ káàbọ̀!",
            language="yoruba",
            duration=10.5,
            quality_score=0.85,
            sisi_compatible=True
        )
        
        # Create a test manifest
        manifest = CuratedDatasetManifest(
            dataset_id="test_dataset",
            name="Test Dataset",
            language="yoruba",
            samples=[sample]
        )
        
        manifest.calculate_stats()
        
        print(f"  ✅ Created manifest: {manifest.dataset_id}")
        print(f"     Samples: {manifest.total_samples}")
        print(f"     Duration: {manifest.total_duration_hours:.4f} hours")
        
        # Validate
        validation = manifest.validate()
        if validation["valid"]:
            print(f"  ✅ Manifest is valid")
        else:
            print(f"  ❌ Validation errors: {validation['errors']}")
            
        return True
        
    except Exception as e:
        print(f"  ❌ Schema test failed: {e}")
        return False


def test_coverage_matrix():
    """Test loading the coverage matrix"""
    print("\n📊 Testing coverage matrix...")
    
    matrix_path = PROJECT_ROOT / "ml_training" / "curator" / "language_coverage_matrix.json"
    
    try:
        with open(matrix_path, 'r') as f:
            matrix = json.load(f)
        
        languages = matrix.get("language_coverage", {})
        primary = matrix.get("sisi_lola_target_languages", {}).get("primary", [])
        
        print(f"  ✅ Loaded coverage matrix")
        print(f"     Languages tracked: {len(languages)}")
        print(f"     Primary targets: {', '.join(primary)}")
        
        # Show critical gaps
        gaps = matrix.get("gap_summary", {}).get("critical_gaps", [])
        if gaps:
            print(f"     ⚠️ Critical gaps: {', '.join(g['language'] for g in gaps)}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Coverage matrix test failed: {e}")
        return False


def test_catalog():
    """Test loading the datasets catalog"""
    print("\n📚 Testing datasets catalog...")
    
    import csv
    catalog_path = PROJECT_ROOT / "ml_training" / "curator" / "african_language_datasets_catalog.csv"
    
    try:
        with open(catalog_path, 'r') as f:
            reader = csv.DictReader(f)
            datasets = list(reader)
        
        print(f"  ✅ Loaded catalog with {len(datasets)} datasets")
        
        # Count by quality tier
        tiers = {}
        for d in datasets:
            tier = d.get("Quality_Tier", "unknown")
            tiers[tier] = tiers.get(tier, 0) + 1
        
        print(f"     By quality: {tiers}")
        
        # Count commercial-ready
        commercial = sum(1 for d in datasets if d.get("Commercial_Ready", "").lower() == "yes")
        print(f"     Commercial-ready: {commercial}/{len(datasets)}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Catalog test failed: {e}")
        return False


def test_api_router():
    """Test the API router can be imported"""
    print("\n🌐 Testing API router...")
    
    try:
        from app.routers.curator import router
        
        # Count endpoints
        routes = [r for r in router.routes if hasattr(r, 'path')]
        
        print(f"  ✅ Router loaded with {len(routes)} endpoints")
        for route in routes[:5]:
            print(f"     {route.methods} {route.path}")
        if len(routes) > 5:
            print(f"     ... and {len(routes) - 5} more")
        
        return True
        
    except Exception as e:
        print(f"  ❌ API router test failed: {e}")
        return False


def main():
    """Run all tests"""
    results = []
    
    results.append(("Curator Files", test_curator_files()))
    results.append(("Manifest Schema", test_manifest_schema()))
    results.append(("Coverage Matrix", test_coverage_matrix()))
    results.append(("Datasets Catalog", test_catalog()))
    results.append(("API Router", test_api_router()))
    
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
        if result:
            passed += 1
    
    print(f"\n  Total: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 Voice Dataset Curator is fully set up!")
        print("\nNext steps:")
        print("  1. Create the Custom GPT using CUSTOM_GPT_INSTRUCTIONS.md")
        print("  2. Start the API: cd sisi_lola_api && uvicorn app.main:app --reload")
        print("  3. Test curator endpoints at http://localhost:8000/curator/health")
        return 0
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
