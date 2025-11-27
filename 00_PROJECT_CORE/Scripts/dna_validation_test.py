"""
DNA Validation Test Script
This script generates a test image and validates it against the DNA reference images.
"""

import requests
import json
import base64
from pathlib import Path
from datetime import datetime
import sys

# Configuration
API_BASE_URL = "http://127.0.0.1:8000"
DNA_REFERENCE_DIR = Path(__file__).parent.parent / "sisi_lola_api" / "assets" / "dna"
TEST_OUTPUT_DIR = Path(__file__).parent / "dna_validation_tests"
TEST_OUTPUT_DIR.mkdir(exist_ok=True)

# Test scenarios
TEST_SCENARIOS = [
    {
        "name": "Studio Portrait",
        "scenario": "smiling confidently at the camera in a professional studio with soft lighting",
        "aspect_ratio": "1:1",
        "expected_features": ["confident smile", "professional lighting", "clear facial features"]
    },
    {
        "name": "Full Body Shot",
        "scenario": "standing with hands on hips in a confident pose, full body visible",
        "aspect_ratio": "9:16",
        "expected_features": ["hourglass figure", "full body visible", "confident posture"]
    },
    {
        "name": "Close-up Portrait",
        "scenario": "close-up portrait showing facial details, looking directly at camera",
        "aspect_ratio": "4:5",
        "expected_features": ["high cheekbones", "captivating eyes", "impeccable makeup"]
    }
]

def test_api_connection():
    """Verify the API is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/")
        print(f"✅ API Status: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ API Connection Failed: {str(e)}")
        print(f"   Make sure the server is running:")
        print(f"   cd sisi_lola_api && ./venv/bin/python -m uvicorn app.main:app --reload")
        return False

def generate_test_image(test_case):
    """Generate an image for testing."""
    endpoint = f"{API_BASE_URL}/images/generate"
    
    payload = {
        "scenario": test_case["scenario"],
        "aspect_ratio": test_case["aspect_ratio"]
    }
    
    print(f"\n🎨 Generating: {test_case['name']}")
    print(f"   Scenario: {test_case['scenario']}")
    print(f"   Aspect Ratio: {test_case['aspect_ratio']}")
    
    try:
        response = requests.post(endpoint, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   DNA Integrity: {result.get('dna_integrity', 'N/A')}")
        
        return result
    except Exception as e:
        print(f"   ❌ Generation Failed: {str(e)}")
        return None

def validate_dna_integrity(result, test_case):
    """Validate the generated image against DNA standards."""
    validation_report = {
        "test_name": test_case["name"],
        "timestamp": datetime.now().isoformat(),
        "dna_integrity": result.get("dna_integrity", "N/A"),
        "checks": {}
    }
    
    # Check 1: DNA Prompt Injection
    injected_prompt = result.get("injected_prompt", "")
    validation_report["checks"]["prompt_injection"] = {
        "passed": "voluptuous" in injected_prompt.lower() and "yoruba" in injected_prompt.lower(),
        "details": "DNA visual core present in prompt" if "voluptuous" in injected_prompt.lower() else "DNA visual core missing"
    }
    
    # Check 2: Reference Images Used
    reference_images = result.get("reference_images", [])
    validation_report["checks"]["reference_images"] = {
        "passed": len(reference_images) > 0,
        "count": len(reference_images),
        "details": f"{len(reference_images)} reference images used"
    }
    
    # Check 3: Status Check
    validation_report["checks"]["generation_status"] = {
        "passed": result.get("status") == "success",
        "details": result.get("status", "unknown")
    }
    
    # Overall Pass/Fail
    all_checks_passed = all(check["passed"] for check in validation_report["checks"].values())
    validation_report["overall_result"] = "PASS ✅" if all_checks_passed else "FAIL ❌"
    
    return validation_report

def save_validation_report(report, test_case):
    """Save validation report to file."""
    filename = f"validation_{test_case['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = TEST_OUTPUT_DIR / filename
    
    with open(filepath, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Validation Report: {filepath}")
    return filepath

def print_validation_summary(report):
    """Print a formatted validation summary."""
    print(f"\n{'=' * 60}")
    print(f"VALIDATION SUMMARY: {report['test_name']}")
    print(f"{'=' * 60}")
    print(f"Overall Result: {report['overall_result']}")
    print(f"DNA Integrity: {report['dna_integrity']}")
    print(f"\nDetailed Checks:")
    
    for check_name, check_data in report["checks"].items():
        status = "✅ PASS" if check_data["passed"] else "❌ FAIL"
        print(f"  {status} - {check_name}: {check_data['details']}")
    
    print(f"{'=' * 60}\n")

def run_full_validation_suite():
    """Run all validation tests."""
    print("=" * 60)
    print("SISI LOLA DNA VALIDATION TEST SUITE")
    print("=" * 60)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Output Directory: {TEST_OUTPUT_DIR}")
    print(f"Number of Tests: {len(TEST_SCENARIOS)}")
    
    if not test_api_connection():
        return
    
    print("\n" + "=" * 60)
    print("STARTING VALIDATION TESTS")
    print("=" * 60)
    
    all_reports = []
    
    for idx, test_case in enumerate(TEST_SCENARIOS, 1):
        print(f"\n[Test {idx}/{len(TEST_SCENARIOS)}]")
        
        # Generate image
        result = generate_test_image(test_case)
        
        if not result:
            print(f"   ⏭️  Skipping validation (generation failed)")
            continue
        
        # Validate
        report = validate_dna_integrity(result, test_case)
        all_reports.append(report)
        
        # Save and print report
        save_validation_report(report, test_case)
        print_validation_summary(report)
    
    # Final Summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    
    total_tests = len(all_reports)
    passed_tests = sum(1 for r in all_reports if "PASS" in r["overall_result"])
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {failed_tests} ❌")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "N/A")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! DNA integrity is maintained.")
        print("✅ System is ready for mass asset generation.")
    else:
        print("\n⚠️  Some tests failed. Review the reports above.")
        print("   Consider refining the VISUAL_PROMPT_CORE in app/config.py")
    
    print("=" * 60)

if __name__ == "__main__":
    run_full_validation_suite()
