#!/usr/bin/env python3
"""
SISI LOLA API SERVER LAUNCHER
Cross-platform startup script with all optimizations enabled.

Usage:
    python start_optimized_server.py
    
    # Or with specific port
    python start_optimized_server.py --port 8080
    
    # Production mode (no reload)
    python start_optimized_server.py --production
"""
import os
import sys
import subprocess
import signal
import argparse
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent

def setup_environment():
    """Set up environment variables for optimized inference"""
    
    # Nigerian Models Optimization
    optimizations = {
        "NIGERIAN_MODELS_ENABLED": "true",
        "NIGERIAN_BRAIN_MODEL_PATH": "sisilolalive/sisi-lola-brain-mistral",
        "NIGERIAN_VOICE_MODEL_PATH": "sisilolalive/sisi-lola-voice-xtts",
        "MODEL_CACHE_ENABLED": "true",
        "RESPONSE_CACHE_ENABLED": "true",
        "FLASH_ATTENTION_ENABLED": "true",
    }
    
    for key, value in optimizations.items():
        if key not in os.environ:
            os.environ[key] = value
            
    # Add project roots to PYTHONPATH
    current_pythonpath = os.environ.get("PYTHONPATH", "")
    new_paths = [str(PROJECT_ROOT), str(PROJECT_ROOT / "sisi_lola_api")]
    
    if current_pythonpath:
        os.environ["PYTHONPATH"] = f"{current_pythonpath}{os.pathsep}{os.pathsep.join(new_paths)}"
    else:
        os.environ["PYTHONPATH"] = os.pathsep.join(new_paths)
    
    # Load .env file
    env_file = PROJECT_ROOT / "sisi_lola_api" / ".env"
    if env_file.exists():
        print(f"📄 Loading environment from {env_file}")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    if key not in os.environ:
                        os.environ[key] = value
    
    return optimizations


def kill_existing_processes(port=8000):
    """Kill any existing uvicorn/API processes, specifically on the target port"""
    import platform
    
    if platform.system() == "Windows":
        # Windows: Use taskkill
        try:
            subprocess.run(
                ["taskkill", "/F", "/IM", "uvicorn.exe"],
                capture_output=True
            )
        except:
            pass
    else:
        # Unix/WSL: Target the port specifically
        print(f"   🔍 Checking for processes on port {port}...")
        try:
            # Use fuser to find and kill processes on the port
            subprocess.run(["fuser", "-k", f"{port}/tcp"], capture_output=True)
            # Fallback for systems without fuser
            lsof_proc = subprocess.run(["lsof", "-t", f"-i:{port}"], capture_output=True, text=True)
            if lsof_proc.stdout.strip():
                for pid in lsof_proc.stdout.strip().split('\n'):
                    subprocess.run(["kill", "-9", pid], capture_output=True)
            
            # General cleanup for any lingering Sisi processes
            subprocess.run(
                ["pkill", "-f", "uvicorn.*sisi_lola"],
                capture_output=True
            )
        except Exception as e:
            print(f"   ⚠️  Could not clean port {port}: {e}")
            pass


def find_python_executable():
    """Find the best python executable to use (current or from venv)"""
    import platform
    import os
    
    # Check if we're already in a venv
    if hasattr(sys, 'real_prefix') or (sys.base_prefix != sys.prefix):
        return sys.executable
        
    # Potential venv names in order of preference
    # We prioritize venv_wsl for Linux/WSL and venv for Windows
    venv_names = ["venv_fix", "venv_wsl", ".venv_sisi", "venv", ".venv"]
    
    for name in venv_names:
        venv_path = PROJECT_ROOT / name
        if platform.system() == "Windows":
            py_path = venv_path / "Scripts" / "python.exe"
        else:
            py_path = venv_path / "bin" / "python"
            
        if py_path.exists():
            # Test if it's actually executable and functional
            try:
                # 1. Test basic execution
                subprocess.run([str(py_path), "--version"], capture_output=True, check=True)
                
                # 2. Test if it's mostly functional
                # We check for uvicorn as the primary signal
                res = subprocess.run([str(py_path), "-c", "import uvicorn"], capture_output=True)
                if res.returncode == 0:
                    print(f"📦 Found and verified virtual environment: {name}")
                    return str(py_path)
                
                # 3. If uvicorn is missing, check if pip is functional
                print(f"📦 Found environment {name} but uvicorn is missing. Verifying Pip...")
                pip_res = subprocess.run([str(py_path), "-m", "pip", "--version"], capture_output=True)
                if pip_res.returncode == 0:
                    print(f"✅ Pip is functional in {name}")
                    return str(py_path)
                else:
                    print(f"⚠️  Venv {name} exists but pip/uvicorn are broken. Skipping...")
                    continue
                    
            except (OSError, subprocess.CalledProcessError):
                print(f"⚠️  Venv {name} found but not executable or broken. Skipping...")
                continue
            
    return sys.executable

def start_server(port: int = 8000, reload: bool = True, workers: int = 1):
    """Start the FastAPI server with optimizations"""
    
    python_exe = find_python_executable()
    
    # Check for multiple critical dependencies
    # If any are missing, trigger a full install
    check_code = "import uvicorn, fastapi, jwt, imageio, PIL, dotenv, cohere, aiohttp, transformers, torch, scipy"
    try:
        subprocess.run([python_exe, "-c", check_code], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"⚠️  Critical dependencies missing in {python_exe}. Repairing...")
        
        # Core dependencies from requirements.txt
        core_deps = [
            "fastapi", "uvicorn", "openai", "python-dotenv", "httpx", 
            "pillow", "requests", "PyJWT", "imageio", "imageio-ffmpeg",
            "cohere", "aiohttp", "transformers", "torch", "scipy"
        ]
        
        # Base install command
        install_cmd = [python_exe, "-m", "pip", "install"] + core_deps
        
        try:
            subprocess.run(install_cmd, check=True)
        except subprocess.CalledProcessError:
            print("⚠️  Standard install failed. Trying with --break-system-packages (PEP 668 fallback)...")
            try:
                subprocess.run(install_cmd + ["--break-system-packages"], check=True)
                print("✅ Dependencies installed successfully using fallback flag.")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install dependencies in {python_exe}.")
                if python_exe != sys.executable:
                    print("🔄 Falling back to system python...")
                    python_exe = sys.executable
                    try:
                        subprocess.run([python_exe, "-m", "pip", "install", "uvicorn", "fastapi", "--break-system-packages"], check=True)
                    except:
                        print("\n" + "!"*60)
                        print("CRITICAL ERROR: Could not secure a working environment.")
                        print("SUGGESTED FIX (Run in your terminal):")
                        print("    python3 -m venv --clear venv_fix --copies")
                        print("    source venv_fix/bin/activate")
                        print("    pip install uvicorn fastapi python-dotenv httpx openai")
                        print("Then run: python start_optimized_server.py")
                        print("!"*60 + "\n")
                        sys.exit(1)

    cmd = [
        python_exe, "-m", "uvicorn",
        "sisi_lola_api.app.main:app",
        "--host", "0.0.0.0",
        "--port", str(port),
        "--workers", str(workers),
        "--log-level", "info",
    ]
    
    if reload:
        cmd.append("--reload")
    
    print(f"\n🚀 Starting server on port {port}...")
    print(f"   Using Python: {python_exe}")
    print(f"   Command: {' '.join(cmd)}\n")
    
    # Start process
    process = subprocess.Popen(
        cmd,
        cwd=PROJECT_ROOT,
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    
    # Handle graceful shutdown
    def signal_handler(sig, frame):
        print("\n\n⏹️  Shutting down gracefully...")
        process.terminate()
        process.wait()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Wait for process
    process.wait()


def main():
    parser = argparse.ArgumentParser(description="Start Sisi Lola API Server")
    parser.add_argument("--port", type=int, default=8000, help="Port to run on")
    parser.add_argument("--production", action="store_true", help="Production mode (no reload)")
    parser.add_argument("--workers", type=int, default=1, help="Number of workers")
    parser.add_argument("--no-kill", action="store_true", help="Don't kill existing processes")
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎭 SISI LOLA API SERVER - OPTIMIZED")
    print("=" * 60)
    
    # Step 1: Kill existing
    if not args.no_kill:
        print(f"\n📋 Step 1: Stopping existing processes on port {args.port}...")
        kill_existing_processes(port=args.port)
        print("   ✅ Done")
    
    # Step 2: Setup environment
    print("\n📋 Step 2: Setting up environment...")
    optimizations = setup_environment()
    for key, value in optimizations.items():
        print(f"   • {key}={value}")
    print("   ✅ Environment ready")
    
    # Step 3: Show optimization summary
    print("\n" + "=" * 60)
    print("🎯 OPTIMIZATIONS ENABLED:")
    print("   • Singleton Model Cache (40x faster startup)")
    print("   • Response Caching (instant repeated queries)")
    print("   • Flash Attention 2 (GPU acceleration)")
    print("   • Bracket Pollution Fix (clean text)")
    print("   • Paragraph Formatting (readable responses)")
    print("   • Repetition Removal (no spam expressions)")
    print("=" * 60)
    
    # Step 4: Start server
    print(f"\n📋 Step 3: Starting server on port {args.port}...")
    start_server(
        port=args.port,
        reload=not args.production,
        workers=args.workers
    )


if __name__ == "__main__":
    main()
