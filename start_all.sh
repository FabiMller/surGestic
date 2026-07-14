#!/bin/bash

# get the directory of the current script
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "🚀 Starting sterile OP-Assistant..."


osascript <<EOF
tell application "Terminal"
    activate
    
    # --- Tab 1: FastAPI Backend ---
    set window1 to do script "cd '$PROJECT_DIR/backend' && source ../venv/bin/activate && uvicorn main:app --reload"
    
    # --- Tab 2: MediaPipe Gestensteuerung ---
    # wait for the first tab to be ready
    tell application "System Events" to keystroke "t" using command down
    delay 0.5
    do script "cd '$PROJECT_DIR/backend' && source ../venv/bin/activate && sleep 2 && python ct_viewer.py" in front window
    
    # --- Tab 3: React Vite Frontend ---
    tell application "System Events" to keystroke "t" using command down
    delay 0.5
    do script "cd '$PROJECT_DIR/frontend' && npm run dev" in front window
    
end tell
EOF

echo "✅ All processes started in new terminal tabs!"


# use : " ./start_all.sh " in terminal to start application.