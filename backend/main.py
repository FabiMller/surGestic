from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

app = FastAPI()

# CORS configuration for the React frontend (Port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global system state tracking
state = {
    "current_index": 0,
    "is_voice_active": False,
    "mic_level": 0
}

# Path to the CT images directory
CT_DIR = os.path.join("..", "frontend", "public", "ct")

def get_ct_files():
    if not os.path.exists(CT_DIR):
        return []
    return sorted([f for f in os.listdir(CT_DIR) if f.endswith('.png')])

class SliceUpdate(BaseModel):
    index: int
    is_voice_active: bool = False
    mic_level: int = 0

@app.get("/")
def read_root():
    return {"status": "online", "message": "Sterile OR Assistant API is running perfectly."}

@app.get("/current-slice")
def get_current_slice():
    files = get_ct_files()
    if not files:
        raise HTTPException(status_code=444, detail="No CT images found in the assets folder.")
    
    idx = max(0, min(state["current_index"], len(files) - 1))
    slice_name = files[idx]
    
    return {
        "index": idx,
        "slice_name": slice_name,
        "image_url": f"/ct/{slice_name}",
        "all_slices": files,
        "is_voice_active": state["is_voice_active"],
        "mic_level": state["mic_level"]
    }

@app.post("/update-slice")
def update_slice(data: SliceUpdate):
    files = get_ct_files()
    if data.index < 0 or data.index >= len(files):
        raise HTTPException(status_code=400, detail="Index out of range")
    
    state["current_index"] = data.index
    state["is_voice_active"] = data.is_voice_active
    state["mic_level"] = data.mic_level

    # Server-side terminal logging
    if data.is_voice_active:
        print(f"[API] Slice: {data.index} | 🎙️ REC | Level: {data.mic_level}%")
    else:
        print(f"[API] Slice: {data.index} | 💤 STANDBY")

    return {
        "status": "success", 
        "updated_index": state["current_index"],
        "is_voice_active": state["is_voice_active"],
        "mic_level": state["mic_level"]
    }