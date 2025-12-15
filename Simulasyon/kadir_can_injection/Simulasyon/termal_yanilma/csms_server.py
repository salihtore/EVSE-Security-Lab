import asyncio
import json

import requests
import websockets

from anomaly_detector import AnomalyDetector

detector = AnomalyDetector()
DASHBOARD_URL = "http://127.0.0.1:8000/update"


async def handle_client(websocket):
    print("[CSMS] Charge point connected.")

    async for message in websocket:
        ocpp = json.loads(message)
        print("[CSMS] Received:", ocpp)

        if ocpp.get("messageTypeId") != 2 or ocpp.get("action") != "MeterValues":
            continue

        payload = ocpp.get("payload", {})

        step = payload.get("step", 0)
        temp = payload.get("temp")
        temp_real = payload.get("temp_real")
        current = payload.get("current")
        attack = payload.get("attack", False)
        cooling = payload.get("cooling", True)
        ambient = payload.get("ambient", 25.0)

        anomaly, reason = detector.detect(
            {"temp": temp, "current": current}
        )

        # decide command based on anomaly + measured temp
        if anomaly:
            if temp is not None and temp >= 60:
                command = "STOP"
            else:
                command = "DERATE"
        else:
            command = "CONTINUE"

        # send to dashboard
        try:
            r = requests.post(
                DASHBOARD_URL,
                json={
                    "step": step,
                    "temp": temp,
                    "temp_real": temp_real,
                    "current": current,
                    "cooling": cooling,
                    "ambient": ambient,
                    "attack": attack,
                    "anomaly": anomaly,
                    "reason": reason or "",
                    "command": command,
                },
                timeout=2,
            )
            print("[CSMS] POST /update ->", r.status_code)
        except Exception as e:
            print("[CSMS] Dashboard error:", e)

        response = {
            "messageTypeId": 3,
            "uniqueId": ocpp.get("uniqueId"),
            "action": "MeterValues",
            "payload": {"command": command},
        }

        await websocket.send(json.dumps(response))
        print("[CSMS] Sent response:", response)


async def main():
    async with websockets.serve(handle_client, "localhost", 8765):
        print("[CSMS] Listening on ws://localhost:8765")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
