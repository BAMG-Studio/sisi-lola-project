"""Run the quick and full DNA validation suites sequentially."""
from __future__ import annotations

import subprocess
import sys
import time
import requests
from pathlib import Path

API_BASE_URL = "http://127.0.0.1:8000"
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
API_DIR = PROJECT_ROOT / "sisi_lola_api"
START_SCRIPT = API_DIR / "start_server.sh"

SERVER_STARTUP_TIMEOUT = 45


def is_server_online() -> bool:
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def start_server() -> subprocess.Popen[bytes] | None:
    if not START_SCRIPT.exists():
        print(f"[ERROR] start_server.sh not found at {START_SCRIPT}")
        return None

    print("\n==> Starting API server via start_server.sh")
    proc = subprocess.Popen(["bash", str(START_SCRIPT)], cwd=str(API_DIR))

    # Wait for server to come online
    for _ in range(SERVER_STARTUP_TIMEOUT):
        if is_server_online():
            print("✅ API server is online")
            return proc
        time.sleep(1)

    print("⚠️  Server did not respond in time")
    return proc


def stop_server(proc: subprocess.Popen[bytes] | None):
    if proc and proc.poll() is None:
        print("\n==> Stopping API server")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def run_script(script_name: str) -> subprocess.CompletedProcess[str]:
    print(f"\n==> Running {script_name}")
    script_path = SCRIPT_DIR / script_name
    if not script_path.exists():
        raise FileNotFoundError(script_path)

    result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("[stderr]", result.stderr)
    return result


def main():
    server_proc = None
    server_started_here = False

    if not is_server_online():
        server_proc = start_server()
        server_started_here = True
        time.sleep(2)
    else:
        print("✅ API server already running")

    quick_result = run_script("quick_dna_test.py")
    full_result = run_script("dna_validation_test.py")

    print("\n==> Summary")
    print(f"Quick Test: {'PASS' if quick_result.returncode == 0 else 'FAIL'}")
    print(f"Full Suite: {'PASS' if full_result.returncode == 0 else 'FAIL'}")

    if server_started_here:
        stop_server(server_proc)


if __name__ == "__main__":
    main()
