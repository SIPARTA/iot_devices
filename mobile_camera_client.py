import os
import time
import threading
import requests
import argparse
import cv2
from dotenv import load_dotenv

load_dotenv()

# --- Config ---
# e.g., http://192.168.1.3:4747
DROIDCAM_BASE_URL = os.getenv("DROIDCAM_URL", "http://192.168.1.3:4747/video").split('/video')[0]
DROIDCAM_VIDEO_URL = f"{DROIDCAM_BASE_URL}/video"

BACKEND_UPLOAD_URL = os.getenv("BACKEND_UPLOAD_URL", "http://localhost:8000/api/v1/incidents/report")
_parsed = BACKEND_UPLOAD_URL.split("/incidents/report")
BACKEND_HEARTBEAT_URL = f"{_parsed[0]}/devices/heartbeat" if len(_parsed) > 1 else "http://localhost:8000/api/v1/devices/heartbeat"

DEVICE_ID = "11111111-1111-1111-1111-111111111111"
DEVICE_API_KEY = os.getenv("DEVICE_API_KEY", "")
HEARTBEAT_INTERVAL = 10  # seconds

def check_droidcam_status():
    """Melakukan health check ringan ke DroidCam tanpa membuka video stream."""
    try:
        # Any response from DroidCam means it's online. If offline, it raises RequestException.
        res = requests.get(DROIDCAM_BASE_URL, timeout=3)
        return True
    except requests.exceptions.RequestException:
        return False

def send_heartbeat():
    """Mengirim heartbeat ke backend SIPARTA."""
    try:
        headers = {'X-API-Key': DEVICE_API_KEY} if DEVICE_API_KEY else {}
        res = requests.post(BACKEND_HEARTBEAT_URL, json={"device_id": DEVICE_ID}, headers=headers, timeout=5)
        return res.status_code == 200
    except requests.exceptions.RequestException:
        return False

def heartbeat_daemon():
    print(f"\n[DAEMON] Memulai background heartbeat setiap {HEARTBEAT_INTERVAL} detik...")
    print(f"[DAEMON] DroidCam URL: {DROIDCAM_BASE_URL}")
    while True:
        if check_droidcam_status():
            success = send_heartbeat()
            if success:
                # Silenced successful heartbeat to avoid spamming the console
                pass
            else:
                print(f"\r[DAEMON] ERROR: Gagal mengirim heartbeat ke backend.", end='', flush=True)
        else:
            print(f"\r[DAEMON] WARNING: DroidCam tidak terdeteksi (Offline).", end='', flush=True)
            
        time.sleep(HEARTBEAT_INTERVAL)

def capture_and_upload(incident_event_id=None):
    print(f"\n[DROIDCAM] Connecting to video stream at {DROIDCAM_VIDEO_URL}")
    print("[DROIDCAM] Capturing TKP photo...")
    
    try:
        # 1. Fetch image from DroidCam using OpenCV
        cap = cv2.VideoCapture(DROIDCAM_VIDEO_URL)
        
        if not cap.isOpened():
            print("[DROIDCAM] ERROR: Failed to open video stream.")
            return

        print("[DROIDCAM] Stabilizing camera sensor (Auto-Focus/Exposure)...")
        # WARMUP PHASE
        for _ in range(15):
            cap.read()
            time.sleep(0.05)
            
        ret, frame = cap.read()
        cap.release()
        
        if not ret or frame is None:
            print("[DROIDCAM] ERROR: Failed to capture frame from video stream.")
            return

        success, encoded_image = cv2.imencode('.jpg', frame)
        if not success:
            print("[DROIDCAM] ERROR: Failed to encode frame to JPEG.")
            return
            
        image_bytes = encoded_image.tobytes()
        print("[DROIDCAM] Capture successful. Uploading to SIPARTA backend...")
        
        # 2. Upload to FastAPI
        files = {
            'file': ('capture.jpg', image_bytes, 'image/jpeg')
        }
        data = {
            'device_id': DEVICE_ID,
            'source': 'droidcam'
        }
        if incident_event_id:
            data['incident_event_id'] = incident_event_id
            
        headers = {'X-API-Key': DEVICE_API_KEY} if DEVICE_API_KEY else {}
        res_api = requests.post(BACKEND_UPLOAD_URL, files=files, data=data, headers=headers, timeout=10)
        res_api.raise_for_status()
        
        print("\n--- JSON PAYLOAD FROM BACKEND ---")
        import json
        print(json.dumps(res_api.json(), indent=2))
        print("---------------------------------")
        
    except requests.exceptions.RequestException as e:
        print(f"[DROIDCAM] ERROR: Failed to communicate: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SIPARTA Mobile Camera Client (DroidCam)")
    parser.add_argument("--incident", "-i", type=str, help="Link photo to a specific incident_event_id", default=None)
    parser.add_argument("--capture-only", action="store_true", help="Capture and exit immediately (no daemon)")
    args = parser.parse_args()
    
    if args.capture_only:
        capture_and_upload(args.incident)
    else:
        # Jalankan background daemon untuk heartbeat
        daemon_thread = threading.Thread(target=heartbeat_daemon, daemon=True)
        daemon_thread.start()
        
        # Mode interaktif di main thread
        print("\n=======================================================")
        print(" SIPARTA Mobile Camera Client (Daemon Mode Active)")
        print("=======================================================")
        print("Klien akan terus memonitor DroidCam dan mengirim heartbeat.")
        print("Tekan [ENTER] kapan saja untuk mengambil foto TKP secara manual.")
        print("Ketik 'q' atau 'exit' lalu [ENTER] untuk berhenti.")
        print("=======================================================\n")
        
        while True:
            try:
                cmd = input()
                if cmd.strip().lower() in ['q', 'exit', 'quit']:
                    print("Exiting...")
                    break
                else:
                    capture_and_upload(args.incident)
            except KeyboardInterrupt:
                print("\nExiting...")
                break
