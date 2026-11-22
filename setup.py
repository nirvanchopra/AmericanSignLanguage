import argparse
import os
import subprocess
import sys
import venv
from pathlib import Path


ROOT = Path(__file__).resolve().parent
APP_DIR = ROOT / "Final Project" / "Source Code"
VENV_DIR = ROOT / ".v"
REQ_FILE = APP_DIR / "requirement.txt"
APP_FILE = APP_DIR / "final_pred.py"
MODEL_FILE = APP_DIR / "cnn8grps_rad1_model.h5"


def fail(message: str) -> None:
    print(f"\nERROR: {message}")
    sys.exit(1)


def venv_python() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def run(cmd, cwd=ROOT) -> None:
    print(f"\n> {' '.join(str(part) for part in cmd)}", flush=True)
    subprocess.check_call([str(part) for part in cmd], cwd=str(cwd))


def check_files() -> None:
    required = (APP_DIR, REQ_FILE, APP_FILE, MODEL_FILE)
    missing = [path for path in required if not path.exists()]
    if missing:
        fail("Missing required project files:\n" + "\n".join(str(path) for path in missing))


def check_python_version() -> None:
    version = sys.version_info
    if (version.major, version.minor) != (3, 10):
        fail(
            "This old TensorFlow app is expected to run with Python 3.10.x. "
            f"You are using Python {version.major}.{version.minor}.{version.micro}. "
            "Install Python 3.10, then run this setup again."
        )


def create_venv() -> None:
    if VENV_DIR.exists():
        print(f"Virtual environment already exists: {VENV_DIR}")
        return

    print(f"Creating virtual environment: {VENV_DIR}")
    venv.EnvBuilder(with_pip=True).create(VENV_DIR)


def install_dependencies() -> None:
    python = venv_python()
    run([python, "-m", "pip", "install", "--upgrade", "pip"])
    run([python, "-m", "pip", "install", "-r", REQ_FILE])
    run([python, "-m", "pip", "install", "--no-deps", "protobuf==3.20.3"])


def verify_setup() -> None:
    python = venv_python()
    code = (
        "import cv2, tensorflow, keras, cvzone, mediapipe, PIL, pyttsx3, enchant; "
        "from keras.models import load_model; "
        "load_model('./cnn8grps_rad1_model.h5'); "
        "print('Verification OK: imports and model load worked')"
    )
    run([python, "-c", code], cwd=APP_DIR)


def print_run_command() -> None:
    python = venv_python()
    print("\nSetup complete.")
    print("Run the app with:")
    print(f'cd "{APP_DIR}"')
    print(f'"{python}" final_pred.py')


def run_app() -> None:
    python = venv_python()
    print("\nStarting Sign Language GUI. Allow camera access if Windows asks.")
    subprocess.check_call([str(python), "final_pred.py"], cwd=str(APP_DIR))


def main() -> None:
    parser = argparse.ArgumentParser(description="Set up and run the ASL webcam app.")
    parser.add_argument("--run", action="store_true", help="Start the GUI after setup finishes.")
    parser.add_argument("--skip-install", action="store_true", help="Verify and run using the existing .v environment.")
    args = parser.parse_args()

    check_files()
    check_python_version()

    if not args.skip_install:
        create_venv()
        install_dependencies()

    verify_setup()

    if args.run:
        run_app()
    else:
        print_run_command()


if __name__ == "__main__":
    main()
