import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2, 
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

cap = cv2.VideoCapture(0)
print("Starte Webcam mit 2-Hand-Erkennung... Drücke 'q' zum Beenden.")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    
    if results.multi_hand_landmarks and results.multi_handedness:
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            hand_label = results.multi_handedness[idx].classification[0].label
            
            color = (0, 255, 0) if hand_label == "Right" else (255, 0, 0)
            
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            index_tip = hand_landmarks.landmark[8]
            
            y_offset = 0 if hand_label == "Right" else 60
            
            cv2.putText(
                frame, 
                f"{hand_label} Hand - Index X: {index_tip.x:.2f} Y: {index_tip.y:.2f}", 
                (10, 40 + y_offset), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.9, 
                color, 
                2
            )

    cv2.imshow('Steriler OP-Assistent - 2-Hand-Test', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()