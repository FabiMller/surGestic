import sounddevice as sd
import numpy as np
import sys
import time

print("--- Dynamische Audio-Hardware Diagnose ---")

# Timing-Kontrolle für die Pegel-Ausgabe (Dämpfung gegen Flackern)
last_update_time = 0.0
print_interval = 0.02  # Max 50 Updates pro Sekunde (20ms)

def audio_callback(indata, frames, time_info, status):
    global last_update_time
    if status:
        print(f"\n[STATUS WARNUNG]: {status}", file=sys.stderr)
    
    current_time = time.time()
    if current_time - last_update_time >= print_interval:
        # Root-Mean-Square (RMS) für eine präzise Lautstärkemessung
        rms = np.sqrt(np.mean(indata**2)) if len(indata) > 0 else 0
        
        # Skalierung für die visuelle Balken-Anzeige
        scaled_val = rms * 300.0
        
        # Generiere den dynamischen Lautstärkebalken
        bar_length = min(int(scaled_val), 50)
        visual_bar = '█' * bar_length + '░' * (50 - bar_length)
        
        # Ausgabe erzwingen und direkt im Terminal überschreiben (flush=True)
        sys.stdout.write(f"\r🔊 Pegel: {scaled_val:6.2f} | [{visual_bar}]")
        sys.stdout.flush()
        
        last_update_time = current_time

# --- AUTOMATISCHE GERÄTE-SUCHE (DEIN ANSATZ) ---
devices = sd.query_devices()
current_device_id = None
device_name = "Unbekannt"

# Schritt 1: Versuche das offizielle System-Standardgerät zu ermitteln
try:
    default_input = sd.query_devices(kind='input')
    current_device_id = default_input['index']
    device_name = default_input['name']
    print(f"✔ System-Standard-Mikrofon erkannt: '{device_name}' (ID: {current_device_id})")
except Exception:
    print("⚠ Kein Standard-Eingabegerät vom System gemeldet. Starte Hardware-Scan...")

# Schritt 2: Ausfallsicherer Fallback, falls kein Standard gesetzt ist
if current_device_id is None:
    for idx, dev in enumerate(devices):
        # Suche nach dem ersten Gerät, das Kanäle für INPUT besitzt (> 0)
        if dev['max_input_channels'] > 0:
            current_device_id = idx
            device_name = dev['name']
            print(f"✔ Erstes verfügbares Hardware-Mikrofon ausgewählt: '{device_name}' (ID: {current_device_id})")
            break

# Schritt 3: Stream starten oder abbrechen, falls gar kein Mikrofon existiert
if current_device_id is None:
    print("\n❌ Fehler: Es wurde absolut kein funktionierendes Mikrofon an diesem Gerät gefunden!")
    sys.exit(1)

try:
    print(f"\n🚀 Starte Audio-Stream auf Gerät: '{device_name}'")
    print("Bitte mach ein Geräusch, schnipse oder sprich in dein Mikrofon...\n")
    
    # Nutzt die dynamisch ermittelte ID
    with sd.InputStream(device=current_device_id, samplerate=16000, channels=1, latency='low', callback=audio_callback):
        while True:
            # Verhindert CPU-Spikes während der Hintergrund-Stream läuft
            sd.sleep(10)
            
except Exception as e:
    print(f"\n❌ Fehler beim Öffnen des Audio-Streams: {e}")
    print("Hinweis: Falls du macOS nutzt, prüfe 'Systemeinstellungen > Datenschutz & Sicherheit > Mikrofon'.")