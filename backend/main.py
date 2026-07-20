from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

state = {
    "current_index": 0,
    "is_voice_active": False,
    "mic_level": 0,
    "selected_cell": None,
    "zoom_level": 1.0,
    "offset": {"x": 0.0, "y": 0.0},
    "zoom_origin": {"x": 50.0, "y": 50.0},
}

CT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "public", "ct"))

def get_ct_files():
    if not os.path.exists(CT_DIR):
        return []
    return sorted([f for f in os.listdir(CT_DIR) if f.endswith('.png')])

class SliceUpdate(BaseModel):
    index: int
    is_voice_active: bool = False
    mic_level: int = 0
    selected_cell: Optional[str] = None
    zoom_level: float = 1.0
    offset_x: float = 0.0
    offset_y: float = 0.0
    zoom_origin_x: float = 50.0
    zoom_origin_y: float = 50.0

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
        "mic_level": state["mic_level"],
        "selected_cell": state["selected_cell"],
        "zoom_level": state["zoom_level"],
        "offset_x": state["offset"]["x"],
        "offset_y": state["offset"]["y"],
        "zoom_origin_x": state["zoom_origin"]["x"],
        "zoom_origin_y": state["zoom_origin"]["y"],
    }

@app.post("/update-slice")
def update_slice(data: SliceUpdate):
    files = get_ct_files()
    if not files:
         raise HTTPException(status_code=400, detail="No files available")

    if data.index < 0 or data.index >= len(files):
        raise HTTPException(status_code=400, detail="Index out of range")
    
    state["current_index"] = data.index
    state["is_voice_active"] = data.is_voice_active
    state["mic_level"] = data.mic_level
    state["selected_cell"] = data.selected_cell
    state["zoom_level"] = data.zoom_level
    state["offset"]["x"] = data.offset_x
    state["offset"]["y"] = data.offset_y
    state["zoom_origin"]["x"] = data.zoom_origin_x
    state["zoom_origin"]["y"] = data.zoom_origin_y

    if data.is_voice_active:
        print(f"[API] Slice: {data.index} | 🎙️ REC | Level: {data.mic_level}%")
    else:
        print(f"[API] Slice: {data.index} | 💤 STANDBY")

    return {
        "status": "success", 
        "updated_index": state["current_index"],
        "is_voice_active": state["is_voice_active"],
        "mic_level": state["mic_level"],
        "selected_cell": state["selected_cell"],
        "zoom_level": state["zoom_level"],
        "offset_x": state["offset"]["x"],
        "offset_y": state["offset"]["y"],
        "zoom_origin_x": state["zoom_origin"]["x"],
        "zoom_origin_y": state["zoom_origin"]["y"],
    }
