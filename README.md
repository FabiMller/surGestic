# 🩺 surGestic - a Sterile OR Assistant


  > **OpenAI Build Week Challenge Submission**  
  > *Category:* **Work & Productivity**  / **Apps for Your Life** (Healthcare & Medical Technology)
  > *Built with:* **GPT-5.6** & **OpenAI Codex**



---
## 📋 Overview

In a surgical operating room (OR), maintaining **strict sterility** is a matter of life and death. Surgeons frequently need to review DICOM/CT medical scans during procedures, but touching traditional keyboards, mice, or touchscreens breaks the sterile field, requiring laborious re-sterilization or assistance from circulating nurses.

**Sterile OR Assistant** solves this critical healthcare challenge by introducing a completely **touchless, sterile interface** for medical imaging. Combining high-precision hand-gesture tracking and offline voice recognition, surgeons can seamlessly navigate CT slices and zoom into specific ROI (Region of Interest) grid sectors without ever breaking sterility.

---

## ✨ Key Features & Demo

- 🤏 **Touchless Gesture Control (MediaPipe):**
  - **Single Pinch + Swipe Down:** Advance to the next CT slice.
  - **Single Pinch + Swipe Up:** Return to the previous CT slice.
- 🎙️ **Voice-Activated Grid Selection (VOSK):**
  - **Double Pinch & Hold:** Activates real-time speech recognition.
  - **Grid Navigation:** Call out grid coordinates (e.g., `"C3"`, `"A4"`) overlaying the CT scan to pinpoint regions.
  - **Voice Command `"reset"`:** Restores the view to default scaling and centering.
- 🔍 **Dynamic Distance Zooming:**
  - After selecting a grid cell, moving your hand further from the pinch origin zooms in dynamically; moving closer zooms back out.
- ⚡ **Low-Latency Architecture:**
  - **FastAPI** backend with asynchronous state synchronization to a high-performance **React + Vite** frontend interface.

---

## 🤖 Built with GPT-5.6 & OpenAI Codex

This project was built from ground zero during the **OpenAI Build Week Challenge**, leveraging **GPT-5.6** for architecture design and **OpenAI Codex** for rapid code generation, bug fixing, and optimization.

### Where Codex Accelerated the Workflow:
1. **Mathematical Spatial Mapping:** Codex generated the coordinate transformation formulas mapping camera-space hand landmark coordinates to 2D image grid anchors and CSS transform offsets.
2. **Audio-Stream Threading & State Sync:** Codex wrote the concurrent audio buffer loop using `sounddevice` and `queue`, integrating VOSK speech recognition without blocking OpenCV's 30 FPS camera feed.
3. **Cross-Platform Script Automation:** Codex created the macOS shell automation (`start_all.sh` / `stop_all.sh`) using AppleScript to launch and manage backend, vision module, and Vite frontend servers in separate terminal tabs effortlessly.

---

## 🏗️ Architecture

The **Sterile OR Assistant** uses a low-latency, modular system architecture designed to maintain a smooth 30 FPS visual experience while concurrently processing vision and audio input.

### System Components

1. **Vision & Voice Engine (`ct_viewer.py`)**
   - **Video Processing:** Captures real-time webcam feed via OpenCV.
   - **Gesture Tracking:** Leverages Google MediaPipe `HandLandmarker` to track hand landmarks, detect single/double pinches, and measure vertical swipe deltas.
   - **Speech Recognition:** Processes live microphone input through an offline VOSK model (`vosk-model-small-en-us-0.15`) running in a dedicated audio buffer thread to recognize grid coordinates (e.g., `"C3"`) and commands like `"reset"`.
   - **State Calculation:** Dynamically calculates spatial offsets, zoom levels based on hand distance, and selected grid origin coordinates.

2. **Backend API (`backend/main.py`)**
   - **Framework:** Built with **FastAPI** running on Uvicorn.
   - **State Management:** Serves as the central state hub holding real-time parameters (current slice index, active grid cell, zoom factor, pan offsets, and microphone audio levels).
   - **Endpoints:** Exposes RESTful endpoints (`/update-slice` and `/current-slice`) for state synchronization with sub-100ms response times.

3. **Frontend User Interface (`frontend/`)**
   - **Framework:** Built with **React** and **Vite** for maximum rendering performance.
   - **OR Display GUI:** Continuously polls the backend API to update the CT image display, overlay the dynamic coordinate grid, apply smooth CSS transform animations for zooming and panning, and render real-time audio visualizers.

---

## 🚀 Getting Started

### Prerequisites

- **Operating System:** macOS / Linux / Windows (macOS recommended for start/stop shell scripts)
- **Python:** 3.14.3
- **Node.js:** v18+ & `npm`
- **Webcam & Microphone**

---

### Installation & Setup

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/FabiMller/surGestic.git
    cd surGestic

    ```


2. **Set Up Python Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

    ```


3. **Install Frontend Dependencies:**
    ```bash
    cd frontend
    npm install
    cd ..

    ```


4. **Download Required Assets & Models:**
* **MediaPipe Hand Landmarker:** Download `hand_landmarker.task` into the `backend/` directory.
* **VOSK Offline Model:** Download `vosk-model-small-en-us-0.15` and extract it into `backend/vosk-model-small-en-us-0.15`.



---

### 🩻 Generating Sample Data

Before starting the application, generate the synthetic CT scan series:

```bash
python generate_test_images.py

```

*This generates CT slice image assets in `frontend/public/ct/`.*

---

### 🏃 Running the Application

Start all services (FastAPI Backend, MediaPipe/VOSK Vision Engine, and React Frontend) with a single command:

```bash
chmod +x start_all.sh stop_all.sh
./start_all.sh

```

* **Frontend Viewer:** Runs at `http://localhost:5173`
* **FastAPI API:** Runs at `http://127.0.0.1:8000`

---

### 🛑 Stopping the Application

To shut down all running servers and clean up terminal processes:

```bash
./stop_all.sh

```

---

## 🎮 How to Use (Surgeon Instructions)

| Action | Physical/Voice Gesture | Result |
| --- | --- | --- |
| **Next Slice** | Single Pinch (Index + Thumb) & **Swipe Down** | Moves to next CT slice |
| **Previous Slice** | Single Pinch (Index + Thumb) & **Swipe Up** | Moves to previous CT slice |
| **Voice Mode** | **Double Pinch & Hold** | Activates microphone listener |
| **Select ROI** | Speak grid cell (e.g., `"C 3"`, `"A 4"`) | Centers view on target coordinate |
| **Zoom In / Out** | Hold pinch and move hand away / towards pinch origin | Adjusts continuous zoom level |
| **Reset View** | Speak `"reset"` | Restores CT scan to full 1.0x view |

---
---