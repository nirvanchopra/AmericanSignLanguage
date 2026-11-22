"""
SignBridge AI — Unified Development Server Launcher
Runs both the FastAPI backend (port 8000) and the Next/Vite frontend (port 3000) concurrently.
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
VENV_PYTHON = ROOT_DIR / ".venv" / "Scripts" / "python.exe"
if not VENV_PYTHON.exists():
    VENV_PYTHON = ROOT_DIR / ".v" / "Scripts" / "python.exe"
if not VENV_PYTHON.exists():
    VENV_PYTHON = Path(sys.executable)

def print_banner():
    banner = r"""
  ==============================================================
    ____  _             ____       _     _               _    ___ 
   / ___|(_) __ _ _ __ | __ ) _ __(_) __| | __ _  ___   / \  |_ _|
   \___ \| |/ _` | '_ \|  _ \| '__| |/ _` |/ _` |/ _ \ / _ \  | | 
    ___) | | (_| | | | | |_) | |  | | (_| | (_| |  __// ___ \ | | 
   |____/|_|\__, |_| |_|____/|_|  |_|\__,_|\__, |\___/_/   \_\___|
            |___/                          |___/                  
   Intelligent American Sign Language Translation Platform
  ==============================================================
    * Backend API & Docs:   http://127.0.0.1:8000/docs
    * WebSocket Stream:     ws://127.0.0.1:8000/ws/recognize
    * Frontend Web Studio:  http://localhost:3000
  ==============================================================
    Press Ctrl+C to stop all services.
"""
    print(banner)

def main():
    print_banner()

    # 1. Initialize Database
    print("[1/3] Checking and initializing database...")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BACKEND_DIR)
    env["PYDANTIC_DISABLE_PLUGINS"] = "1"
    try:
        subprocess.run(
            [str(VENV_PYTHON), "-m", "app.db.init_db"],
            cwd=str(BACKEND_DIR),
            env=env,
            check=True
        )
    except Exception as e:
        print(f"[Warning] DB initialization: {e}")

    # 2. Start Backend API
    print("[2/3] Starting FastAPI backend on port 8000...")
    backend_proc = subprocess.Popen(
        [str(VENV_PYTHON), "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=str(BACKEND_DIR),
        env=env
    )

    # 3. Start Frontend App
    print("[3/3] Starting Vite React frontend on port 3000...")
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    frontend_proc = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=str(FRONTEND_DIR),
        shell=(os.name == "nt")
    )

    print("\n✅ SignBridge AI is running!")
    print("   Open your browser at: http://localhost:3000\n")

    try:
        while True:
            time.sleep(1)
            if backend_proc.poll() is not None:
                print("Backend process terminated.")
                break
            if frontend_proc.poll() is not None:
                print("Frontend process terminated.")
                break
    except KeyboardInterrupt:
        print("\nShutting down SignBridge AI services...")
    finally:
        try:
            backend_proc.terminate()
        except Exception:
            pass
        try:
            frontend_proc.terminate()
        except Exception:
            pass
        print("All processes stopped successfully. Goodbye!")

if __name__ == "__main__":
    main()
