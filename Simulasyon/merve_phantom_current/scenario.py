import asyncio
import logging
import websockets
from src.core.scenario_adapter import ScenarioAdapter
from .charge_point import SimulatedChargePoint

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def attack_logic(cp, adapter):
    await asyncio.sleep(1)
    
    # 1. Boot
    await cp.send_boot_notification()
    adapter.emit("BootNotification", {"model": "PhantomFix-104", "vendor": "MerveSec"})
    await asyncio.sleep(1)
    
    # 2. Start Charging
    await cp.start_charging()
    adapter.emit("StartTransaction", {"idTag": cp.id_tag, "transactionId": cp.transaction_id})
    await asyncio.sleep(1)
    
    # 3. Normal Charging
    logger.info("⚡ Normal şarj fazı...")
    for _ in range(2):
        await cp.simulate_meter_values()
        adapter.emit("MeterValues", {"transactionId": cp.transaction_id, "meterValue": str(cp.meter_value)})
        await asyncio.sleep(1)

    # 4. Stop Charging (Session ends but energy continues)
    logger.warning("🛑 Şarj durduruluyor ancak enerji çekilmeye devam edecek (ANOMALİ)!")
    await cp.stop_charging()
    adapter.emit("StopTransaction", {"transactionId": cp.transaction_id, "reason": "Local"})
    await asyncio.sleep(1)

    # 5. SALDIRI (Hayalet Akım)
    logger.error("👻 SALDIRI AKTİF: Hayalet Akım (Phantom Current)!")
    logger.info("⏳ [MERVE] Zaman akışı hızlandırılıyor (Uzun süreli sızıntı simülasyonu)...")

    for i in range(10):
        await cp.simulate_meter_values(phantom_mode=True, step_kwh=0.005)
        # Phantom mode'da transactionId None olsa bile adapter üzerinden bildirmeliyiz
        # Bu MeterValues mesajı PhantomCurrentDetector tarafından yakalanacaktır.
        adapter.emit("MeterValues", {"transactionId": None, "meterValue": str(cp.meter_value)})
        await asyncio.sleep(0.5)

async def run_attack_with_adapter(adapter):
    uri = f"ws://127.0.0.1:9000/{adapter.cp_id}"
    try:
        async with websockets.connect(uri, subprotocols=["ocpp1.6"]) as ws:
            cp = SimulatedChargePoint(adapter.cp_id, ws)
            cp_task = asyncio.create_task(cp.start())
            await attack_logic(cp, adapter)
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
    adapter = ScenarioAdapter("CP_HAYALET", "merve_phantom_current")
    run_scenario("attack", adapter)
