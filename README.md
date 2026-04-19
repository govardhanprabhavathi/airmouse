# VisionGlobe 🌍✋

VisionGlobe is an interactive, browser-based Augmented Reality (AR) application that allows you to control a 3D, high-definition Earth model using real-time hand gestures. The globe floats seamlessly over your hand through your webcam feed and responds intuitively to various gestures.

## ✨ Features

- **AR Floating Globe:** The Earth intelligently tracks your primary open hand and floats smoothly above your palm.
- **Grab and Spin:** Bring your second open hand into the frame and swipe horizontally to spin the globe on its axis. It features physics-based momentum, smoothly coming to a stop just like a real physical globe.
- **Dynamic Zooming:** Hold up the "Peace Sign" ✌️ (index and middle finger raised) on *both* hands simultaneously. Moving your hands closer together or further apart dynamically zooms the globe in and out.
- **Pause Rotation:** Close your primary hand into a fist ✊ to instantly freeze the globe's rotation.
- **Premium Interface:** A stealthy, monochrome glassmorphic UI overlay provides real-time feedback on your active gestures.
- **Silky Smooth Tracking:** Built-in Linear Interpolation (Lerp) algorithms ensure that all hand tracking and 3D rendering interactions feel incredibly smooth and jitter-free.

## 🛠️ Tech Stack

This project is built using modern, professional-grade technologies designed for high performance in the browser:

- **Frontend Framework:** [React](https://react.dev/) + [Vite](https://vitejs.dev/) + [TypeScript](https://www.typescriptlang.org/)
- **3D Engine:** [Three.js](https://threejs.org/) powered by [@react-three/fiber](https://r3f.docs.pmnd.rs/) and [@react-three/drei](https://github.com/pmndrs/drei)
- **Computer Vision:** Google's modern [@mediapipe/tasks-vision](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker) running directly in the browser via WebAssembly/GPU (No backend server required!).
- **State Management:** [Zustand](https://github.com/pmndrs/zustand) for ultra-fast, uncoupled state updates between the CV loop and the 3D render loop.
- **Styling:** Pure, premium vanilla CSS.

## 🚀 How to Run Locally

1. **Install Dependencies:**
   Make sure you have Node.js installed, then run:
   ```bash
   npm install
   ```

2. **Start the Development Server:**
   ```bash
   npm run dev
   ```

3. **Launch the App:**
   Open the provided local URL (typically `http://localhost:3000/` or `http://localhost:5173/`) in your web browser. 

4. **Grant Camera Permissions:**
   The application requires webcam access to track your hands. Grant permission when prompted by your browser, step back, and raise your hand to start interacting!

## 📂 Project Structure

- `src/components/`: Contains the React UI and 3D Canvas components (`GlobeScene`, `Globe`, `CameraFeed`, `Overlay`).
- `src/lib/`: Houses the core Computer Vision and State logic (`handTracking.ts`, `gestureDetection.ts`, `store.ts`).
- `src/utils/`: Contains mathematical smoothing utilities like `lerp`.
- `public/`: High-resolution NASA Earth textures (Diffuse, Specular, and Normal maps).
