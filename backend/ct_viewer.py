import os
import sys
import time
import math
import cv2
import json
import sounddevice as sd
import queue
import mediapipe as mp
import requests
import numpy as np
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions, RunningMode
from vosk import Model, KaldiRecognizer

API_URL = "http://127.0.0.1:8000/update-slice"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

ct_dir = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "frontend", "public", "ct"))

if not os.path.exists(ct_dir):
    print(f"Error: Folder '{ct_dir}' not found!")
    sys.exit(1)

ct_files = sorted([f for f in os.listdir(ct_dir) if f.endswith('.png')])
if not ct_files:
    print(f"Error: No .png images found in folder '{ct_dir}'!")
    sys.exit(1)

current_slice_idx = 0
interaction = {
    "selected_cell": None,
    "zoom_level": 1.0,
    "offset_x": 0.0,
    "offset_y": 0.0,
    "zoom_origin_x": 50.0,
    "zoom_origin_y": 50.0,
}

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),           # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),           # Index finger
    (5, 9), (9, 10), (10, 11), (11, 12),      # Middle finger
    (9, 13), (13, 14), (14, 15), (15, 16),    # Ring finger
    (13, 17), (17, 18), (18, 19), (19, 20),   # Pinky
    (0, 17)
]

vosk_model = None
recognizer = None
model_path = os.path.join(SCRIPT_DIR, "vosk-model-small-en-us-0.15")

try:
    if os.path.exists(model_path):
        vosk_model = Model(model_path) 
        allowed_words = ["a", "b", "c", "d", "1", "2", "3", "4", "one", "two", "three", "four", "reset"]
        recognizer = KaldiRecognizer(vosk_model, 16000, json.dumps(allowed_words))
        print("✔ VOSK Speech Recognition (Small Model) successfully loaded.")
    else:
        print(f"\n❌ [VOSK NOTICE] Model folder not found at:\n   '{model_path}'")
        print("-> Microphone levels will still work during double-pinch, text recognition is in standby.\n")
except Exception as e:
    print(f"\n[VOSK WARNING] Error loading model: {e}\n")

audio_queue = queue.Queue()

def audio_callback(indata, frames, time_info, status):
    if status:
        print(status, file=sys.stderr)
    audio_queue.put(bytes(indata))

def send_index_to_api(idx, is_voice_active=False, mic_level=0):
    try:
        requests.post(
            API_URL, 
            json={
                "index": idx, 
                "is_voice_active": is_voice_active,
                "mic_level": int(mic_level),
                "selected_cell": interaction["selected_cell"],
                "zoom_level": interaction["zoom_level"],
                "offset_x": interaction["offset_x"],
                "offset_y": interaction["offset_y"],
                "zoom_origin_x": interaction["zoom_origin_x"],
                "zoom_origin_y": interaction["zoom_origin_y"],
            }, 
            timeout=0.1
        )
    except requests.exceptions.RequestException:
        pass

number_mapping = {"one": "1", "two": "2", "three": "3", "four": "4"}

def process_voice_input(text):
    words = text.split()
    if len(words) >= 2:
        col = words[0].lower()
        row = words[1].lower()
        row = number_mapping.get(row, row)
        if col in ["a", "b", "c", "d"] and row in ["1", "2", "3", "4"]:
            return f"{col.upper()}{row}"
    return None

def get_cell_origin(cell):
    columns = {"A": 12.5, "B": 37.5, "C": 62.5, "D": 87.5}
    rows = {"4": 12.5, "3": 37.5, "2": 62.5, "1": 87.5}
    return columns[cell[0]], rows[cell[1]]

def reset_interaction():
    interaction["selected_cell"] = None
    interaction["zoom_level"] = 1.0
    interaction["offset_x"] = 0.0
    interaction["offset_y"] = 0.0
    interaction["zoom_origin_x"] = 50.0
    interaction["zoom_origin_y"] = 50.0

def main():
    global current_slice_idx
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Camera could not be opened.")
        return

    task_path = os.path.join(SCRIPT_DIR, "hand_landmarker.task")
    options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=task_path),
        running_mode=RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.6,
        min_tracking_confidence=0.6,
    )

    last_y = None
    last_action_time = 0.0
    cooldown_seconds = 0.4
    start_time = time.time()

    last_pinch_time = 0.0
    double_pinch_window = 0.4
    is_voice_active = False
    can_select_field = False
    was_pinching = False
    is_zooming = False

    zoom_anchor_level = 1.0
    zoom_anchor_position = None

    last_api_send_time = 0.0
    API_SEND_INTERVAL = 0.05  
    smoothed_mic_level = 0.0

    selected_device_id = None
    try:
        default_input = sd.query_devices(kind='input')
        selected_device_id = default_input['index']
        print(f"✔ Microphone active: '{default_input['name']}'")
    except Exception:
        devices = sd.query_devices()
        for idx, dev in enumerate(devices):
            if dev['max_input_channels'] > 0:
                selected_device_id = idx
                print(f"✔ Fallback microphone active: '{dev['name']}'")
                break

    audio_stream = None
    if selected_device_id is not None:
        try:
            audio_stream = sd.RawInputStream(
                device=selected_device_id, 
                samplerate=16000, 
                blocksize=4000,
                dtype='int16',
                channels=1, 
                callback=audio_callback
            )
            audio_stream.start()
        except Exception as e:
            print(f"❌ Audio Error: {e}")

    print("🚀 Gesture control active. HOLD double-pinch for voice input.")

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
                if is_voice_active:
                    is_voice_active = False
                    print("🎙️ Voice control stopped (Hand lost).")
                    send_index_to_api(current_slice_idx, is_voice_active=False, mic_level=0)

            hand_is_currently_pinching = False

            if detection_result.hand_landmarks:
                for hand_landmarks in detection_result.hand_landmarks:
                    points = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks]
                    
                    for start_idx, end_idx in HAND_CONNECTIONS:
                        cv2.line(frame, points[start_idx], points[end_idx], (255, 255, 255), 2)

                    thumb_tip = hand_landmarks[4]
                    index_tip = hand_landmarks[8]

                    distance = math.sqrt((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)
                    is_pinching = distance < 0.05
                    hand_is_currently_pinching = is_pinching
                    pinch_position = ((thumb_tip.x + index_tip.x) / 2, (thumb_tip.y + index_tip.y) / 2)

                    if is_pinching and not was_pinching:
                        time_since_last = current_time - last_pinch_time
                        if time_since_last < double_pinch_window and audio_stream is not None:
                            is_voice_active = True
                            can_select_field = True
                            last_y = None  
                            audio_queue.queue.clear()
                            print("🎙️ Listening (e.g. 'A 4')...")
                            send_index_to_api(current_slice_idx, is_voice_active=True, mic_level=0)

                        last_pinch_time = current_time
                    was_pinching = is_pinching

                    for idx, point in enumerate(points):
                        if is_voice_active:
                            color = (255, 0, 0)
                            radius = 7 if idx in [4, 8] else 4
                        elif is_pinching and idx in [4, 8]:
                            color = (0, 0, 255)
                            radius = 7
                        else:
                            color = (0, 255, 0)
                            radius = 4
                        cv2.circle(frame, point, radius, color, -1)

                    current_y = index_tip.y
                    
                    if is_pinching and is_zooming and zoom_anchor_position:
                        hand_distance = math.dist(pinch_position, zoom_anchor_position)
                        desired_zoom = min(4.0, zoom_anchor_level + max(0.0, hand_distance - 0.03) * 4.0)
                        next_zoom = interaction["zoom_level"] + (desired_zoom - interaction["zoom_level"]) * 0.06
                        zoom_changed = abs(next_zoom - interaction["zoom_level"]) >= 0.002

                        if zoom_changed:
                            interaction["zoom_level"] = next_zoom

                        if zoom_changed and current_time - last_api_send_time >= API_SEND_INTERVAL:
                            send_index_to_api(current_slice_idx, is_voice_active=False, mic_level=0)
                            last_api_send_time = current_time

                    elif is_pinching and not is_voice_active:
                        if last_y is not None and (current_time - last_action_time > cooldown_seconds):
                            y_diff = current_y - last_y
                            if y_diff < -0.04:
                                if current_slice_idx > 0: 
                                    current_slice_idx -= 1
                                else: 
                                    current_slice_idx = len(ct_files) - 1
                                interaction["zoom_level"] = 1.0
                                interaction["offset_x"] = 0.0
                                interaction["offset_y"] = 0.0
                                interaction["zoom_origin_x"] = 50.0
                                interaction["zoom_origin_y"] = 50.0
                                last_action_time = current_time
                                print(f"<- Previous slice (Swipe UP): {ct_files[current_slice_idx]}")
                                send_index_to_api(current_slice_idx, is_voice_active=False, mic_level=0)
                                    
                            elif y_diff > 0.04:
                                if current_slice_idx < len(ct_files) - 1: 
                                    current_slice_idx += 1
                                else: 
                                    current_slice_idx = 0
                                interaction["zoom_level"] = 1.0
                                interaction["offset_x"] = 0.0
                                interaction["offset_y"] = 0.0
                                interaction["zoom_origin_x"] = 50.0
                                interaction["zoom_origin_y"] = 50.0
                                last_action_time = current_time
                                print(f"-> Next slice (Swipe DOWN): {ct_files[current_slice_idx]}")
                                send_index_to_api(current_slice_idx, is_voice_active=False, mic_level=0)
                        
                        last_y = current_y
                    elif not is_pinching:
                        last_y = None

            current_mic_level = 0

            if audio_stream:
                if is_voice_active:
                    amplitudes = []
                    
                    while not audio_queue.empty():
                        data = audio_queue.get()
                        audio_data = np.frombuffer(data, dtype=np.int16)
                        if len(audio_data) > 0:
                            mean_amp = np.mean(np.abs(audio_data))
                            amplitudes.append(mean_amp)
                        
                        if recognizer and recognizer.AcceptWaveform(data):
                            result = json.loads(recognizer.Result())
                            recognized_text = result.get("text", "").strip().lower()

                            if recognized_text == "reset" and can_select_field:
                                reset_interaction()
                                zoom_anchor_level = 1.0
                                zoom_anchor_position = None
                                is_zooming = False
                                can_select_field = False
                                is_voice_active = False
                                smoothed_mic_level = 0.0
                                print("🎙️ [VOICE COMMAND] Reset auf Standardansicht.")
                                send_index_to_api(current_slice_idx, is_voice_active=False, mic_level=0)
                            else:
                                selected_cell = process_voice_input(recognized_text)
                                if selected_cell and can_select_field:
                                    origin_x, origin_y = get_cell_origin(selected_cell)
                                    zoom_delta = 1.0 - interaction["zoom_level"]
                                    interaction["offset_x"] += zoom_delta * (interaction["zoom_origin_x"] - origin_x)
                                    interaction["offset_y"] += zoom_delta * (interaction["zoom_origin_y"] - origin_y)
                                    interaction["zoom_origin_x"] = origin_x
                                    interaction["zoom_origin_y"] = origin_y
                                    interaction["selected_cell"] = selected_cell
                                    zoom_anchor_level = interaction["zoom_level"]
                                    zoom_anchor_position = pinch_position
                                    is_zooming = True
                                    can_select_field = False
                                    is_voice_active = False
                                    smoothed_mic_level = 0.0
                                    print(f"🎙️ [VOICE COMMAND] Grid selected: {selected_cell}")
                                    send_index_to_api(current_slice_idx, is_voice_active=False, mic_level=0)
                    
                    if amplitudes:
                        max_amplitude = max(amplitudes)
                        scaled_val = (max_amplitude / 1500.0) * 100.0
                        current_mic_level = max(5, min(int(scaled_val), 100))
                    else:
                        current_mic_level = 0

                    alpha = 0.25 
                    
                    if current_mic_level > smoothed_mic_level:
                        smoothed_mic_level = smoothed_mic_level + 0.5 * (current_mic_level - smoothed_mic_level)
                    else:
                        smoothed_mic_level = smoothed_mic_level + alpha * (current_mic_level - smoothed_mic_level)
                    
                    if is_voice_active and current_time - last_api_send_time >= API_SEND_INTERVAL:
                        send_index_to_api(current_slice_idx, is_voice_active=True, mic_level=int(smoothed_mic_level))
                        last_api_send_time = current_time
                else:
                    while not audio_queue.empty():
                        audio_queue.get()
                    smoothed_mic_level = 0.0

            if is_voice_active and not hand_is_currently_pinching:
                is_voice_active = False
                can_select_field = False
                smoothed_mic_level = 0.0
                if recognizer:
                    result = json.loads(recognizer.Result())
                    process_voice_input(result.get("text", ""))
                print("🎙️ Voice control stopped.")
                send_index_to_api(current_slice_idx, is_voice_active=False, mic_level=0)

            if not hand_is_currently_pinching and is_zooming:
                is_zooming = False
                interaction["selected_cell"] = None
                send_index_to_api(current_slice_idx, is_voice_active=False, mic_level=0)

            active_ct_path = os.path.join(ct_dir, ct_files[current_slice_idx])
            ct_image = cv2.imread(active_ct_path)
            
            cv2.imshow('Kamera-Feed (OP-Gesten)', frame)
            if ct_image is not None:
                cv2.imshow('Steriler Monitor (CT-Viewer)', ct_image)
            
            if cv2.waitKey(1) & 0xFF == ord('q'): 
                break

    if audio_stream:
        audio_stream.stop()
        audio_stream.close()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
