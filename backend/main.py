from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

app = FastAPI()

# active CORS settings to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# global state to keep track of the current slice index
state = {
    "current_index": 0
}

# define the path to the CT images directory
CT_DIR = os.path.join("..", "frontend", "public", "ct")

def get_ct_files():
    if not os.path.exists(CT_DIR):
        return []
    return sorted([f for f in os.listdir(CT_DIR) if f.endswith('.png')])

class SliceUpdate(BaseModel):
    index: int

@app.get("/")
def read_root():
    return {"status": "online", "message": "Steriler OP-Assistent API läuft perfekt!"}


@app.get("/current-slice")
def get_current_slice():
    files = get_ct_files()
    if not files:
        raise HTTPException(status_code=444, detail="Keine CT-Bilder im Assets-Ordner gefunden.")
    
    # ensure the index is within bounds
    idx = max(0, min(state["current_index"], len(files) - 1))
    slice_name = files[idx]
    
    # return the current slice information.
    return {
        "index": idx,
        "slice_name": slice_name,
        "image_url": f"/ct/{slice_name}",
        "all_slices": files  # return the full list of slices for the frontend to use
    }

# API endpoint to update the current slice index
@app.post("/update-slice")
def update_slice(data: SliceUpdate):
    files = get_ct_files()
    if data.index < 0 or data.index >= len(files):
        raise HTTPException(status_code=400, detail="Index außerhalb des gültigen Bereichs")
    
    state["current_index"] = data.index
    print(f"[API] Index aktualisiert auf: {data.index} ({files[data.index]})")
    return {"status": "success", "updated_index": state["current_index"]}