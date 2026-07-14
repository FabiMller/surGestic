import os
import sys
import time
import math
import cv2
import mediapipe as mp
import requests
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions, RunningMode

API_URL = "http://127.0.0.1:8000/update-slice"
ct_dir = os.path.join("..", "frontend", "public", "ct")

if not os.path.exists(ct_dir):
    print(f"Fehler: Ordner '{ct_dir}' nicht gefunden!")
    sys.exit(1)

# Einlesen aller Bilder (nur .png wie in main.py gefordert!)
ct_files = sorted([f for f in os.listdir(ct_dir) if f.endswith('.png')])
if not ct_files:
    print(f"Fehler: Keine .png Bilder im Ordner '{ct_dir}' gefunden!")
    sys.exit(1)

current_slice_idx = 0

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),           # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),           # Index finger
    (5, 9), (9, 10), (10, 11), (11, 12),      # Middle finger
    (9, 13), (13, 14), (14, 15), (15, 16),    # Ring finger
    (13, 17), (17, 18), (18, 19), (19, 20),   # Pinky
    (0, 17)
]

def send_index_to_api(idx):
    try:
        # send index to FastAPI backend
        requests.post(API_URL, json={"index": idx}, timeout=0.2)
    except requests.exceptions.RequestException as e:
        print(f"[API-FEHLER] Konnte Index nicht senden: {e}")

def main():
    global current_slice_idx
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Fehler: Kamera konnte nicht geöffnet werden.")
        return

    options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=os.path.join(os.path.dirname(__file__), "hand_landmarker.task")),        running_mode=RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.6,
        min_tracking_confidence=0.6,
    )

    last_y = None
    last_action_time = 0.0
    cooldown_seconds = 0.4
    start_time = time.time()

    print("🚀 Gesture control active. Pinch and move your hand CLEARLY up or down.")

    with HandLandmarker.create_from_options(options) as landmarker:
        while cap.isOpened():
            success, frame = cap.read()
            if not success: 
                continue

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            timestamp_ms = int((time.time() - start_time) * 1000)
            detection_result = landmarker.detect_for_video(mp_image, timestamp_ms)
            current_time = time.time()
            
            if not detection_result.hand_landmarks:
                last_y = None

            if detection_result.hand_landmarks:
                for hand_landmarks in detection_result.hand_landmarks:
                    points = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks]
                    
                    # White lines between landmarks for better visualization
                    for start_idx, end_idx in HAND_CONNECTIONS:
                        cv2.line(frame, points[start_idx], points[end_idx], (255, 255, 255), 2)

                    # get the thumb tip and index finger tip
                    thumb_tip = hand_landmarks[4]
                    index_tip = hand_landmarks[8]

                    distance = math.sqrt((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)
                    is_pinching = distance < 0.05  

                    # Draw landmarks with different colors based on pinching state
                    for idx, point in enumerate(points):
                        # change color from green to red for index finger tip and thumb tip when pinching
                        if is_pinching and idx in [4, 8]:
                            color = (0, 0, 255)
                            radius = 7
                        else:
                            color = (0, 255, 0)
                            radius = 4
                            
                        cv2.circle(frame, point, radius, color, -1)

                    current_y = index_tip.y
                    
                    # only process the gesture if the hand is pinching
                    if is_pinching:
                        if last_y is not None and (current_time - last_action_time > cooldown_seconds):
                            y_diff = current_y - last_y
                            
                            # Check for significant vertical movement
                            if y_diff < -0.04:
                                if current_slice_idx > 0: 
                                    current_slice_idx -= 1
                                else: 
                                    current_slice_idx = len(ct_files) - 1
                                last_action_time = current_time
                                print(f"<- Vorheriger Slice (Wisch OBEN): {ct_files[current_slice_idx]}")
                                send_index_to_api(current_slice_idx)
                                    
                            elif y_diff > 0.04:  # Check for downward movement
                                if current_slice_idx < len(ct_files) - 1: 
                                    current_slice_idx += 1
                                else: 
                                    current_slice_idx = 0
                                last_action_time = current_time
                                print(f"-> Nächster Slice (Wisch UNTEN): {ct_files[current_slice_idx]}")
                                send_index_to_api(current_slice_idx)
                        
                        last_y = current_y
                    else:
                        last_y = None

            # Lokale Fenster
            active_ct_path = os.path.join(ct_dir, ct_files[current_slice_idx])
            ct_image = cv2.imread(active_ct_path)
            
            cv2.imshow('Kamera-Feed (Gesten-Erkennung)', frame)
            if ct_image is not None:
                cv2.imshow('Steriler OP-Monitor (CT Viewer)', ct_image)
            
            if cv2.waitKey(1) & 0xFF == ord('q'): 
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()