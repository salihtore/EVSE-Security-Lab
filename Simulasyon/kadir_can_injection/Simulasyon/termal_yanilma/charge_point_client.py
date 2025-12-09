import asyncio
import json

import websockets

from charge_point import ChargePoint

ATTACK_START_STEP = 30


async def main():
    uri = "ws://localhost:8765"
    print(f"[CP] Connecting to CSMS: {uri}")

    cp = ChargePoint()

    async with websockets.connect(uri) as websocket:
        print("[CP] Connected to CSMS.")
        step = 0

        while True:
            attack_mode = step >= ATTACK_START_STEP

            # *** ÖNEMLİ: charge_point.py'deki gerçek fonksiyon isimleri ***
            if attack_mode:
                data = cp.generate_spoofed_data()
            else:
                data = cp.generate_real_data()

            cooling = getattr(cp, "cooling_active", True)
            ambient = getattr(cp, "ambient_temp", 25.0)

            msg = {
                "messageTypeId": 2,
                "uniqueId": f"msg-{step}",
                "action": "MeterValues",
                "payload": {
                    "step": step,
                    "temp": data["temp"],
                    "temp_real": data.get("temp_real", data["temp"]),
                    "current": data["current"],
                    "cooling": cooling,
                    "ambient": ambient,
                    "attack": attack_mode,
                },
            }

            await websocket.send(json.dumps(msg))
            print("[CP] Sent:", msg)

            resp_raw = await websocket.recv()
            resp = json.loads(resp_raw)
            print("[CP] Response:", resp)

            cmd = resp.get("payload", {}).get("command", "CONTINUE")

            if cmd == "STOP":
                print("[CP] STOP received — stopping charging loop.")
                break

            if cmd == "DERATE":
                if hasattr(cp, "current"):
                    cp.current = max(8.0, getattr(cp, "current"))
                print("[CP] DERATE received — reducing current.")

            step += 1
            await asyncio.sleep(0.3)


if __name__ == "__main__":
    asyncio.run(main())
