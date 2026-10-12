#!/bin/bash
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "🧹 Cleaning up old processes..."
lsof -ti :8000 | xargs kill -9 2>/dev/null
pkill -f ct_viewer.py 2>/dev/null
sleep 1

echo "🚀 Starting sterile OP-Assistant..."

osascript <<EOF
tell application "Terminal"
    activate
    do script "cd '$PROJECT_DIR/backend' && source ../venv/bin/activate && uvicorn main:app"
    delay 2
    do script "cd '$PROJECT_DIR/backend' && source ../venv/bin/activate && python ct_viewer.py"
    do script "cd '$PROJECT_DIR/frontend' && npm run dev"
end tell
EOF

echo "✅ Started in separate Terminal windows."