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


def kill_existing_processes():
    """Kill any existing uvicorn/API processes"""
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
        # Unix: Use pkill
        try:
            subprocess.run(
                ["pkill", "-f", "uvicorn.*sisi_lola"],
                capture_output=True
            )
        except:
            pass


def start_server(port: int = 8000, reload: bool = True, workers: int = 1):
    """Start the FastAPI server with optimizations"""
    
    cmd = [
        sys.executable, "-m", "uvicorn",
        "sisi_lola_api.app.main:app",
        "--host", "0.0.0.0",
        "--port", str(port),
        "--workers", str(workers),
        "--log-level", "info",
    ]
    
    if reload:
        cmd.append("--reload")
    
    print(f"\n🚀 Starting server on port {port}...")
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
        print("\n📋 Step 1: Stopping existing processes...")
        kill_existing_processes()
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
