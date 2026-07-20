# Sterile AI OR Assistant

> **Note:** This is a demonstration prototype. It is not medical software and must not be used for clinical care, diagnostic decisions, or processing real patient data.

The Sterile AI OR Assistant explores a touch-free interface for the operating-room environment. A digital monitor displays CT slices that can be selected with hand gestures. A local voice mode also provides visible microphone feedback. The project establishes a foundation for an assistant that could eventually let surgeons interact with imaging and patient information while remaining sterile.

## Current Features

- CT viewer using PNG slices from `frontend/public/ct/`
- React monitor with a thumbnail sidebar, active CT slice, 4×4 orientation grid, and connection status
- FastAPI interface for synchronizing the currently selected slice
- MediaPipe-based single-hand detection through a webcam
- Pinch plus vertical movement selects the previous or next CT slice cyclically
- Double pinch activates local voice mode; the UI displays recording state and microphone level
- Local Vosk recognition for grid coordinates `A`–`D` and `1`–`4` (for example, “A 4”); a recognized grid cell is currently printed to the terminal only

The sample files in `data/` contain anonymized patient and laboratory data for a later implementation step. They are **not yet connected** to the API or user interface.

## Architecture

```text
Webcam / microphone
        │
        ▼
ct_viewer.py ── MediaPipe Hands + Vosk ──► FastAPI (port 8000)
        │                                      │
        └── local OpenCV window                 ▼
                                    React/Vite monitor (port 5173)
                                    CT slices + status + microphone HUD
```

| Area | Technology | Purpose |
| --- | --- | --- |
| Frontend | React 19, Vite | OR monitor and CT display |
| Backend | FastAPI, Uvicorn, Pydantic | Exposes slice and microphone state over HTTP |
| Gestures | MediaPipe Tasks, OpenCV | Hand tracking, pinch, and swipe interaction |
| Voice | Vosk, SoundDevice | Local, constrained speech recognition and level metering |

Although `openai` is listed in `backend/requirements.txt`, it is not called by the current code. No OpenAI API key or external AI API is currently required.

## Requirements

- Python 3.10 or later
- Node.js 20 or later and npm
- Webcam and microphone (for gesture and voice interaction)
- macOS: `start_all.sh` opens three Terminal tabs through AppleScript

Gesture control requires the MediaPipe model at `backend/hand_landmarker.task`. Speech recognition additionally requires a Vosk model at `backend/vosk-model-small-en-us-0.15/`. If the Vosk model is unavailable, gesture control and microphone-level feedback still work, but local speech recognition is disabled.

## Run Locally

### 1. Set up the Python environment and backend

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
pip install vosk sounddevice requests numpy
```

The final command installs libraries used by the current gesture and voice script that are not yet included in `backend/requirements.txt`.

### 2. Set up the frontend

```bash
cd frontend
npm install
cd ..
```

### 3. Start all components (macOS)

```bash
chmod +x start_all.sh
./start_all.sh
```

The script starts:

1. FastAPI at `http://127.0.0.1:8000`
2. gesture control with webcam and microphone
3. the Vite server at `http://localhost:5173`

Alternatively, start the three processes in separate terminals:

```bash
# Terminal 1
source venv/bin/activate
cd backend && uvicorn main:app --reload

# Terminal 2
source venv/bin/activate
cd backend && python ct_viewer.py

# Terminal 3
cd frontend && npm run dev
```

## HTTP API

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | Backend availability status |
| `GET` | `/current-slice` | Current slice, image URL, slice list, and microphone state |
| `POST` | `/update-slice` | Updates the current slice and voice/microphone state |

Example update payload:

```json
{
  "index": 2,
  "is_voice_active": true,
  "mic_level": 42
}
```

## Roadmap

The vision extends beyond the current image viewer:

- Display patient records, laboratory values, and vital signs from structured data
- Translate voice commands such as “Show me the allergies” into UI and data actions
- Add gestures for zooming, freezing, windows, and layouts
- Add an AI agent with tools for patient, laboratory, and imaging data
- Provide intelligent OR-relevant summaries and trend comparisons

Before any real-world clinical use, privacy, security validation, medical-device approval, and safe integration with clinical systems must be addressed separately.

## Project Structure

```text
backend/
  main.py              # FastAPI synchronization API
  ct_viewer.py         # Webcam, gesture, and voice control
  hand_landmarker.task # MediaPipe hand model
frontend/
  src/App.jsx          # React OR monitor
  public/ct/           # Example CT slices
data/
  patient.json         # Sample data, not yet integrated
  labs.json            # Sample data, not yet integrated
start_all.sh           # Starts all components on macOS
```
