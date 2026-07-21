#!/bin/bash

echo "🛑 Beende alle OP-Assistant Prozesse..."

# 1. Beende die spezifischen Hintergrundprozesse gezielt (inkl. Python & Node/Vite)
pkill -9 -f "uvicorn main:app" 2>/dev/null
pkill -9 -f "ct_viewer.py" 2>/dev/null
pkill -9 -f "vite" 2>/dev/null

# Zusätzlich Eventuelle Kindprozesse von Node/Python aufräumen
pkill -9 -f "vosk" 2>/dev/null

echo "✅ Prozesse beendet."

# 2. Schließe die aktiven Terminal-Tabs / Fenster über AppleScript
osascript <<EOF
tell application "Terminal"
    set winList to every window
    repeat with aWin in winList
        set tabList to every tab of aWin
        repeat with aTab in tabList
            set tabHistory to history of aTab
            -- Prüfe, ob einer der Befehle aus start_all.sh im Verlauf des Tabs steht
            if (tabHistory contains "uvicorn main:app") or (tabHistory contains "ct_viewer.py") or (tabHistory contains "npm run dev") then
                close aWin -- Schließt das gesamte Fenster mit den Tabs
                exit repeat
            end if
        end repeat
    end repeat
end tell
EOF

echo "✨ Alle App-Terminals wurden erfolgreich geschlossen!"