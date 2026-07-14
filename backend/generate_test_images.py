import cv2
import numpy as np
import os

# Pfad definieren
target_dir = os.path.join("..", "assets", "ct")
os.makedirs(target_dir, exist_ok=True)

for i in range(1, 6):
    # Schwarzer Hintergrund
    img = np.zeros((512, 512, 3), dtype=np.uint8)
    
    # 1. Äußere Körperform (abgerundetes Oval) simulieren
    cv2.ellipse(img, (256, 240), (160, 120), 0, 0, 360, (40, 40, 40), -1)
    cv2.ellipse(img, (256, 240), (158, 118), 0, 0, 360, (20, 20, 20), -1)
    
    # 2. Wirbelsäule simulieren (unten in der Mitte des Körpers)
    cv2.circle(img, (256, 320), 22, (70, 70, 70), -1)
    cv2.circle(img, (256, 320), 15, (120, 120, 120), -1)
    # Rückenmarkskanal
    cv2.circle(img, (256, 320), 6, (0, 0, 0), -1) 
    
    # 3. Organe simulieren (variieren je nach Slice-Nummer)
    # Magen/Leber-Dummies
    cv2.ellipse(img, (180, 220), (45, 30 + i*4), 30, 0, 360, (60, 60, 60), -1)
    cv2.ellipse(img, (320, 210), (55 - i*2, 35), -20, 0, 360, (55, 55, 55), -1)
    
    # 4. Medizinisches Overlay (Fadenkreuz / Achsen)
    # Dezente Linien am Rand
    cv2.line(img, (256, 20), (256, 40), (100, 100, 100), 1)
    cv2.line(img, (256, 472), (256, 492), (100, 100, 100), 1)
    cv2.line(img, (20, 256), (40, 256), (100, 100, 100), 1)
    cv2.line(img, (472, 256), (492, 256), (100, 100, 100), 1)
    
    # 5. Medizinische Text-Anzeigen (Klinik-Stil)
    font = cv2.FONT_HERSHEY_SIMPLEX
    # Oben Links: Patientendaten
    cv2.putText(img, "ID: TEST-ID-12345678", (20, 30), font, 0.5, (0, 255, 0), 1)
    cv2.putText(img, "ANONYMOUS_SUBJECT_A", (20, 50), font, 0.4, (200, 200, 200), 1)
    
    # Oben Rechts: Scan-Parameter
    cv2.putText(img, f"SLICE: {i}/5", (380, 30), font, 0.5, (0, 255, 255), 1)
    cv2.putText(img, "KV: 120 / MA: 240", (360, 50), font, 0.4, (150, 150, 150), 1)
    
    # Unten Links: Orientierung im Raum
    cv2.putText(img, "R", (20, 262), font, 0.6, (255, 255, 255), 1)
    cv2.putText(img, "L", (480, 262), font, 0.6, (255, 255, 255), 1)
    cv2.putText(img, "AXIAL VIEW", (20, 490), font, 0.4, (120, 120, 120), 1)
    
    # Ein kleiner simulierter "Befund" (z.B. Entzündungsherd) bei Slice 3 und 4
    if i in [3, 4]:
        cv2.circle(img, (190, 230), 8, (180, 180, 180), -1)
        cv2.putText(img, "CRITICAL AREA", (140, 195), font, 0.4, (0, 0, 255), 1)
        cv2.line(img, (180, 200), (190, 220), (0, 0, 255), 1)

    # Bild speichern
    filename = os.path.join(target_dir, f"slice_{i}.png")
    cv2.imwrite(filename, img)
    print(f"Grafisches CT-Bild generiert: {filename}")

print("\nFertig! Die Bilder sehen jetzt deutlich mehr nach einem echten OP-Monitor aus.")