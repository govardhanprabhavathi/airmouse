# AirMouse: Real-Time Hand Tracking & Gesture Control

AirMouse is an offline, real-time hand-tracking application that allows you to control your computer's mouse using hand gestures via your webcam. 

Built entirely in Python, it uses **MediaPipe Tasks API** for robust, fast hand landmark detection and **PyAutoGUI** to directly interface with your operating system's mouse controls.

## Features

- **High-DPI Mouse Movement**: Maps a comfortable box in your camera feed to your entire screen, eliminating the need to over-stretch your arm.
- **Smooth Cursor Tracking**: Utilizes Exponential Moving Average (EMA) to ensure the cursor glides butter-smooth without jitter.
- **Offline & Real-Time**: No internet connection required after the initial model download. Processed completely on your local CPU.
- **Custom UI Dashboard**: A sleek, custom-built OpenCV UI dashboard tracking FPS and the current active gesture.

## Gestures & Controls

- **Point hand**: Move cursor (smooth tracking via One Euro Filter)
- **Pinch thumb + index**: Left click (quick pinch)
- **Double pinch thumb + index**: Double click (two quick pinches)
- **Pinch and hold thumb + index**: Click & drag (hold pinch and move hand)
- **Thumb + middle finger pinch**: Right click
- **Thumb + ring finger pinch**: Middle click
- **Two-finger pinch (thumb + index + middle) & move up/down**: Vertical scroll
- **Two-finger pinch (thumb + index + middle) & move left/right**: Horizontal scroll
- **Ring pinch & hold & move**: Precision scroll (middle drag scroll)
- **Fist**: Play / Pause media (when media is playing)
- **Swipe hand Left / Right**: Previous / Next media track (when media is playing)
- **Rotate wrist Clockwise / Anti-clockwise**: Increase / Decrease system volume gradually (when media is playing)
- **Peace Sign**: Capture Screenshot (saved to `screenshots/` directory)

## Installation & Setup

1. Make sure you have Python installed.
2. Install the required dependencies:
   ```bash
   pip install opencv-python mediapipe pyautogui numpy
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Safety Mechanism

PyAutoGUI includes a built-in fail-safe. If the cursor ever behaves erratically, quickly drag your physical mouse to any of the four corners of your screen. This will instantly abort the script.
