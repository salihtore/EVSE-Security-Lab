import asyncio
import logging
import websockets
# charge_point.py dosyanızdan SimulatedChargePoint sınıfını import eder
from .charge_point import SimulatedChargePoint 

logging.basicConfig(level=logging.INFO)
CP_ID = "CP_MAHMUT" 
CSMS_URI = f"ws://127.0.0.1:9000/{CP_ID}"

# -----------------------------------------------------------
# NORMAL MOD
# -----------------------------------------------------------

async def normal_flow(cp: SimulatedChargePoint):
    """ Normal şarj seansı: 5 döngüde 0.5 kWh raporlanır. """
    logging.info(">> NORMAL AKIŞ BAŞLADI (Gerçek Raporlama)")
    await cp.send_boot_notification()
    await cp.start_charging()
    
    for i in range(5):
        await cp.simulate_meter_values_normal(step_kwh=0.1) 
        logging.info(f"   [Normal] Sayaç Raporu #{i+1}: {cp.meter_value:.2f} kWh")
        await asyncio.sleep(2)
        
    await cp.stop_charging()
    logging.info(f">> NORMAL AKIŞ SONLANDI. TOPLAM RAPORLANAN: {cp.meter_value:.2f} kWh")

async def run_normal():
    async with websockets.connect(CSMS_URI, subprotocols=["ocpp1.6"]) as ws:
        cp = SimulatedChargePoint(CP_ID, ws)
        await asyncio.gather(
            cp.start(),
            normal_flow(cp),
        )

# -----------------------------------------------------------
# ATTACK MODU
# -----------------------------------------------------------

async def attack_flow(cp: SimulatedChargePoint):
    """ Enerji Manipülasyonu Saldırısı: Gerçek 2.5 kWh harcanır, 0.5 kWh raporlanır. """
    logging.error(">> SALDIRI AKIŞI BAŞLIYOR: ENERJİ MANİPÜLASYONU...")
    await cp.send_boot_notification()
    await cp.start_charging()
    
    real_consumption_tracker = 0.0
    
    for i in range(5):
        # Saldırı: Gerçek Tüketim (0.5 kWh) > Raporlanan Tüketim (0.1 kWh)
        await cp.simulate_meter_values_attack(real_step_kwh=0.5, reported_step_kwh=0.1) 
        real_consumption_tracker += 0.5 
        logging.error(f"   [SALDIRI RAPORU] Raporlanan: {cp.meter_value:.2f} kWh (Gerçek Harcanan: {real_consumption_tracker:.2f} kWh)")
        await asyncio.sleep(2)

    await cp.stop_charging()
    logging.error(f">> SALDIRI SONLANDI. CSMS'e TOPLAM RAPOR: {cp.meter_value:.2f} kWh (Gerçekte {real_consumption_tracker:.2f} kWh harcandı.)")


async def run_attack():
    async with websockets.connect(CSMS_URI, subprotocols=["ocpp1.6"]) as ws:
        cp = SimulatedChargePoint(CP_ID, ws)
        await asyncio.gather(
            cp.start(),
            attack_flow(cp),
        )

def run_scenario(mode: str = "normal"):
    if mode == "attack":
        logging.error("A SALDIRI MODU BAŞLIYOR...")
        asyncio.run(run_attack())
    else:
        logging.info(" NORMAL MOD BAŞLIYOR...")
        asyncio.run(run_normal())