import time
import requests

from charge_point import ChargePoint

DASHBOARD_URL = "http://127.0.0.1:8000/update"

cp = ChargePoint()

ATTACK_START_STEP = 30

print("[DIRECT] Starting direct post loop...")

step = 0
while True:
    attack_mode = step >= ATTACK_START_STEP

    if attack_mode:
        data = cp.generate_spoofed_data()
    else:
        data = cp.generate_real_data()

    payload = {
        "step": step,
        "temp": data["temp"],
        "temp_real": data["temp_real"],
        "current": data["current"],
        "attack": attack_mode,
        "anomaly": False,
        "reason": "",
    }

    try:
        r = requests.post(DASHBOARD_URL, json=payload)
        print(f"[DIRECT] step={step} POST -> {r.status_code}")
    except Exception as e:
        print("[DIRECT] Error posting to dashboard:", e)

    step += 1
    time.sleep(0.3)
