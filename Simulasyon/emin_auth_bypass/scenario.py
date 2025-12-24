import asyncio
import logging
import websockets
from typing import Optional
from src.core.scenario_adapter import ScenarioAdapter

from .charge_point import SimulatedChargePoint

logging.basicConfig(level=logging.INFO)

CP_ID = "CP_EMIN"
CSMS_URL = f"ws://127.0.0.1:9000/{CP_ID}"


# --------------------------------------------------
# NORMAL AKIŞ (REFERANS)
# --------------------------------------------------
async def normal_flow(cp: SimulatedChargePoint, adapter: Optional[ScenarioAdapter] = None):
    logging.info(" NORMAL AKIŞ BAŞLADI")

    await cp.send_boot_notification()
    if adapter:
        adapter.emit("BootNotification", {"chargePointModel": "CP-V1", "chargePointVendor": "SimuTech"})

    await cp.authorize("VALID_TAG_123")
    if adapter:
        adapter.emit("Authorize", {"idTag": "VALID_TAG_123", "status": "Accepted"})

    await cp.start_charging()
    if adapter:
        adapter.emit("StartTransaction", {"idTag": "VALID_TAG_123", "transactionId": 1})

    for i in range(5):
        await cp.simulate_meter_values()
        if adapter:
            adapter.emit("MeterValues", {
                "transactionId": 1,
                "meterValue": [{"sampledValue": [{"value": str(100 + i)}]}]
            })
        await asyncio.sleep(1)

    await cp.stop_charging()
    if adapter:
        adapter.emit("StopTransaction", {"transactionId": 1, "reason": "Local"})

    logging.info(" NORMAL AKIŞ BİTTİ")


# --------------------------------------------------
# AUTH BYPASS SALDIRISI
# --------------------------------------------------
async def attack_flow(cp: SimulatedChargePoint, adapter: Optional[ScenarioAdapter] = None):
    cp.attack_mode = True

    logging.error("⚠ AUTH BYPASS SALDIRISI BAŞLADI")

    await cp.send_boot_notification()
    if adapter:
        adapter.emit("BootNotification", {"chargePointModel": "CP-V1", "chargePointVendor": "SimuTech"})

    # ❌ Authorize yok
    if adapter:
        adapter.emit("Authorize", {"idTag": None, "status": "MISSING_AUTHORIZE"})

    await cp.start_charging()
    if adapter:
        adapter.emit("StartTransaction", {"idTag": None, "transactionId": 999})

    for i in range(5):
        await cp.simulate_meter_values()
        if adapter:
            adapter.emit("MeterValues", {
                "transactionId": 999,
                "meterValue": [{"sampledValue": [{"value": str(200 + i)}]}]
            })
        await asyncio.sleep(1)

    await cp.stop_charging()
    if adapter:
        adapter.emit("StopTransaction", {"transactionId": 999, "reason": "Local"})


    logging.error("⚠ AUTH BYPASS SALDIRISI TAMAMLANDI")


# --------------------------------------------------
# RUNNERS
# --------------------------------------------------
async def run_normal(adapter: Optional[ScenarioAdapter] = None):
    async with websockets.connect(CSMS_URL, subprotocols=["ocpp1.6"]) as ws:
        cp = SimulatedChargePoint(CP_ID, ws)
    await asyncio.gather(cp.start(), normal_flow(cp, adapter))



async def run_attack(adapter: Optional[ScenarioAdapter] = None):
    async with websockets.connect(CSMS_URL, subprotocols=["ocpp1.6"]) as ws:
        cp = SimulatedChargePoint(CP_ID, ws)

        # cp.start() ayrı task olarak çalışsın
        cp_task = asyncio.create_task(cp.start())

        # saldırıyı çalıştır
        await attack_flow(cp, adapter)

        # 🔴 KRİTİK: alarmın ana motora düşmesi için bekle
        await asyncio.sleep(1)

        # bağlantıyı kontrollü kapat
        cp_task.cancel()




# --------------------------------------------------
# ENTRY POINT
# --------------------------------------------------
def run_scenario(mode: str = "attack", adapter: Optional[ScenarioAdapter] = None):
    if mode == "normal":
        logging.info("▶ NORMAL MOD ÇALIŞTIRILIYOR")
        asyncio.run(run_normal(adapter))
    else:
        logging.error("▶ AUTH BYPASS SALDIRI MODU ÇALIŞTIRILIYOR")
        asyncio.run(run_attack(adapter))



if __name__ == "__main__":
    run_scenario("attack")

#python run_all.py --scenario emin_auth_bypass --mode attack
