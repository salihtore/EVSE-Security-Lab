import asyncio
import logging
import websockets
from src.core.scenario_adapter import ScenarioAdapter
from .charge_point import SimulatedChargePoint

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def attack_flow(cp: SimulatedChargePoint, adapter: ScenarioAdapter):
    logger.error("🚨 [MAHMUT] ENERJİ MANIPULASYONU SALDIRISI BAŞLATILIYOR")
    
    await cp.send_boot_notification()
    adapter.emit("BootNotification", {"model": "EnergyCheat-X", "vendor": "MahmutSec"})
    await asyncio.sleep(1)
    
    await cp.start_charging()
    adapter.emit("StartTransaction", {"idTag": cp.id_tag, "transactionId": cp.transaction_id})
    await asyncio.sleep(1)
    
    # 🕵️ Saldırı Fazı
    logger.error("🔥 Gerçek harcanan 2.5 kWh, ama raporlanan 0.5 kWh!")
    
    # Manuel alarm kaldırıldı - EnergyMismatchDetector tarafından yakalanacak
    # adapter.emit_alarm(...)

    for i in range(3):
        await cp.simulate_meter_values_attack(real_step_kwh=0.5, reported_step_kwh=0.1)
        adapter.emit("MeterValues", {"transactionId": cp.transaction_id, "meterValue": str(cp.meter_value)})
        await asyncio.sleep(1)

    await cp.stop_charging()
    adapter.emit("StopTransaction", {"transactionId": cp.transaction_id, "reason": "Local"})
    logger.info("🚨 [MAHMUT] SENARYO TAMAMLANDI")

async def run_attack_with_adapter(adapter):
    uri = f"ws://127.0.0.1:9000/{adapter.cp_id}"
    try:
        async with websockets.connect(uri, subprotocols=["ocpp1.6"]) as ws:
            cp = SimulatedChargePoint(adapter.cp_id, ws)
            cp_task = asyncio.create_task(cp.start())
            await attack_flow(cp, adapter)
            await asyncio.sleep(1)
            cp_task.cancel()
    except Exception as e:
        logger.error(f"❌ Bağlantı hatası: {e}")

def run_scenario(mode: str = "attack", adapter: ScenarioAdapter = None):
    if mode == "attack":
        asyncio.run(run_attack_with_adapter(adapter))
    else:
        logger.info("Normal mod bu senaryo için tasarlanmadı.")

if __name__ == "__main__":
    from src.core.scenario_adapter import ScenarioAdapter
    adapter = ScenarioAdapter("CP_MAHMUT", "mahmut_attack_automation")
    run_scenario("attack", adapter)