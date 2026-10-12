# 🩺 surGestic – a Sterile OR Assistant

> **OpenAI Build Week Challenge Submission**
> *Category:* **Work & Productivity** / **Apps for Your Life** (Healthcare & Medical Technology)
> *Built with:* **GPT-5.6** & **OpenAI Codex**

> ⚠️ **Demo only – not a medical device.** surGestic is a proof of concept that runs on **synthetic test data**. It must not be used for diagnosis, treatment decisions, or any clinical purpose. The "AI-Assistant" panel in the UI shows **static placeholder text**, not real analysis.

---

## 📋 Overview

In an operating room, maintaining **strict sterility** is critical. Surgeons often need to review CT scans mid-procedure, but touching a keyboard, mouse, or touchscreen breaks the sterile field and forces re-sterilization or reliance on a circulating nurse.

**surGestic** is a **touchless interface** for viewing CT slices. It combines hand-gesture tracking (MediaPipe) with offline voice recognition (VOSK) so a user can scroll through slices and zoom into a region of interest without touching anything.

---

## ✨ Features

- 🤏 **Gesture control (MediaPipe)**
  - **Pinch + swipe down:** next CT slice
  - **Pinch + swipe up:** previous CT slice
- 🎙️ **Voice-activated grid selection (VOSK, fully offline)**
  - **Double pinch and hold:** activates speech recognition
  - Say a grid cell, e.g. **"C 3"** or **"A 4"**, to select a region of the 4×4 overlay
  - Say **"reset"** to restore the default view
- 🔍 **Distance-based zoom**
  - After selecting a cell, keep pinching and move your hand away from where the pinch started to zoom in
- 📡 **Live display** – a React frontend polls a FastAPI backend for the current state and animates slice changes, zoom, and pan, plus a live microphone level indicator

---

## 🏗️ Architecture

Three processes run side by side:

1. **Vision & voice engine (`backend/ct_viewer.py`)**
   - Reads the webcam with OpenCV and tracks one hand with MediaPipe `HandLandmarker`.
   - Detects pinches (thumb tip to index tip), double pinches, and vertical swipes.
   - Captures microphone audio via `sounddevice` (audio callback + queue) and recognizes a small grammar (`a–d`, `1–4`, `one–four`, `reset`) with an offline VOSK model.
   - Computes slice index, selected cell, zoom level, and pan offsets, and sends them to the backend.
2. **Backend API (`backend/main.py`)**
   - FastAPI app holding the shared state: slice index, voice/mic status, selected cell, zoom, offsets.
   - Endpoints: `GET /current-slice`, `POST /update-slice`.
3. **Frontend (`frontend/`)**
   - React + Vite. Shows the CT slice, thumbnail list, 4×4 coordinate grid, zoom/pan transforms, and status indicators (server connection, microphone).

---

## 🚀 Getting Started

### Prerequisites

| Requirement | Notes |
| --- | --- |
| **Python 3.11 or 3.12** | Tested with 3.12. Very new versions (3.13+) may lack wheels for `mediapipe`, `opencv-python`, or `vosk`. |
| **Node.js 18+** and `npm` | For the frontend |
| **Webcam and microphone** | Camera and microphone permission must be granted to your terminal app |
| **macOS** (for `start_all.sh`) | On Linux/Windows, start the three processes manually (see below) |

### 1. Clone

```bash
git clone https://github.com/FabiMller/surGestic.git
cd surGestic
```

### 2. Python environment

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` should contain:

```
fastapi
uvicorn
pydantic
mediapipe
opencv-python
numpy
requests
sounddevice
vosk
```

Quick check that everything installed:

```bash
python -c "import cv2, mediapipe, sounddevice, vosk, requests, numpy; print('all good')"
```

### 3. Frontend dependencies

```bash
cd frontend
npm install
cd ..
```

### 4. Download the models

Both go into `backend/`.

```bash
cd backend

# MediaPipe hand model (required)
curl -L -o hand_landmarker.task \
  https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task

# VOSK English model (optional, needed for voice commands)
curl -L -O https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
rm vosk-model-small-en-us-0.15.zip

cd ..
```

Without the VOSK model the app still starts, but voice recognition stays in standby.

### 5. Generate the synthetic CT series

```bash
cd backend
python generate_test_images.py
cd ..
```

This writes 12 synthetic slices (`slice_001.png` … `slice_012.png`, 2048×2048) to `frontend/public/ct/`. The app exits at startup if that folder is empty.

---

## 🏃 Running

### Option A: one command (macOS)

```bash
chmod +x start_all.sh stop_all.sh
./start_all.sh
```

This frees port 8000 and opens separate Terminal windows for the backend, the vision engine, and the frontend. Open **http://localhost:5173** in your browser.

> The first time, macOS will ask for **camera** and **microphone** access for Terminal (or iTerm / VS Code). Allow both, then quit and reopen the terminal app if the camera does not start.

### Option B: manual (any OS)

Open three terminals in the project root.

```bash
# Terminal 1 – backend
cd backend
source ../venv/bin/activate
uvicorn main:app

# Terminal 2 – vision & voice engine
cd backend
source ../venv/bin/activate
python ct_viewer.py

# Terminal 3 – frontend
cd frontend
npm run dev
```

Start the backend first so the vision engine has something to talk to.

- **Frontend:** http://localhost:5173
- **API:** http://127.0.0.1:8000

---

## 🛑 Stopping

- **Manual run:** press `Ctrl+C` in each terminal. In the camera window, press **`q`** to quit the vision engine.
- **Script:** `./stop_all.sh`
- **If something keeps running**, kill everything directly:

```bash
lsof -ti :8000 | xargs kill -9 2>/dev/null   # backend
pkill -f ct_viewer.py                         # vision & voice engine
pkill -f "vite|npm run dev"                   # frontend
```

Verify nothing is left (both commands should print nothing):

```bash
pgrep -fl "ct_viewer|uvicorn|vite"
lsof -i :8000
```

---

## 🎮 How to Use

Hold your hand in view of the webcam. Use one hand at a time.

| Action | Gesture / Voice | Result |
| --- | --- | --- |
| **Next slice** | Pinch (thumb + index) and **swipe down** | Moves to the next slice |
| **Previous slice** | Pinch and **swipe up** | Moves to the previous slice |
| **Voice mode** | **Double pinch and hold** the second pinch | Microphone listens (red "REC" indicator in the UI) |
| **Select a region** | Say a cell such as **"C 3"** or **"A 4"** | Focuses the view on that grid cell |
| **Zoom** | After selecting a cell, keep pinching and move your hand **away from** the pinch start | Zooms in (up to 4×) |
| **Reset view** | While in voice mode, say **"reset"** | Back to 1.0× and the full view |

**Grid layout:** columns **A–D** run left to right, rows **4–1** run top to bottom (row 4 at the top, row 1 at the bottom).

**Tips and behavior**

- Say the letter and number as two separate words, e.g. "C … three" or "C 3". Voice mode ends automatically after a cell is selected or when you release the pinch or lose the hand.
- Releasing the pinch ends the zoom gesture, but the current zoom level stays until you change slice or say "reset".
- Moving your hand back toward the pinch start zooms out only down to the level you had when you selected the cell. Use "reset" for a full reset.
- Changing slice resets zoom and pan.
- Slice swipes have a short cooldown (0.4 s) to avoid skipping several slices at once.

---

## ⚠️ Limitations

- **Synthetic data only.** No real patient data or DICOM files are handled.
- **AI-Assistant panel is a mock.** Its text, confidence value, and "validated" status are hardcoded placeholders.
- Single hand, single camera, English voice commands, 4×4 grid only.
- Gesture and speech recognition accuracy depend on lighting, camera quality, and background noise; this has not been evaluated for clinical environments.
- `start_all.sh` is macOS-only.

---

## 🤖 Built with GPT-5.6 & OpenAI Codex

This project was built during the **OpenAI Build Week Challenge**. **GPT-5.6** was used for architecture design and **OpenAI Codex** for code generation, debugging, and optimization, including:

1. **Spatial mapping:** the transformation math that maps hand-landmark coordinates and grid anchors to CSS transform offsets.
2. **Audio handling:** the `sounddevice` + `queue` audio pipeline feeding VOSK speech recognition alongside the OpenCV camera loop.
3. **Launch automation:** the macOS AppleScript start/stop scripts for the backend, vision engine, and Vite frontend.