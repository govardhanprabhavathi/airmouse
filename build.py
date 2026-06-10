import subprocess
import sys
import os

def check_and_install_pyinstaller():
    try:
        import PyInstaller
        print("PyInstaller is already installed.")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("PyInstaller installed successfully.")

def build_exe():
    check_and_install_pyinstaller()
    
    # Check if hand_landmarker.task exists
    model_file = "hand_landmarker.task"
    if not os.path.exists(model_file):
        print(f"Error: {model_file} not found in the current directory.")
        print("Please make sure you have the hand_landmarker.task model file in the workspace root.")
        sys.exit(1)
        
    print("Starting build process using PyInstaller...")
    
    # Build options
    # Note: On Windows, pyinstaller data files separator is ';'
    add_data_flag = f"{model_file};."
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--noconsole",
        "--add-data", add_data_flag,
        "--collect-all", "mediapipe",
        "--hidden-import", "mediapipe.tasks.c",
        "--name", "AirMouse",
        "main.py"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print("\nBuild Completed Successfully!")
    print("The standalone executable can be found at: dist/AirMouse.exe")

if __name__ == "__main__":
    build_exe()
