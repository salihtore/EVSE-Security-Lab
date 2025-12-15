import asyncio [cite: 184]
import logging [cite: 185]
import websockets [cite: 186]
from .charge_point import SimulatedChargePoint # Kendi charge_point dosyanızı import edin [cite: 187]

logging.basicConfig(level=logging.INFO) [cite: 188]
# Yönergeye uygun CP ID: ws://127.0.0.1:9000/CP_<İSİM> [cite: 101]
CP_ID = "CP_MAHMUT" 
CSMS_URI = f"ws://127.0.0.1:9000/{CP_ID}"

# -----------------------------------------------------------
# NORMAL MOD: Standart OCPP Akışı (Start -> MeterValues -> Stop) [cite: 102]
# -----------------------------------------------------------

async def normal_flow(cp: SimulatedChargePoint):
    logging.info(">> NORMAL AKIŞ BAŞLADI (Gerçek Raporlama)")
    await cp.send_boot_notification() [cite: 199]
    await cp.start_charging() [cite: 200]
    
    for i in range(5): [cite: 201]
        await cp.simulate_meter_values_normal(step_kwh=0.1) 
        logging.info(f"   [Normal] Sayaç Raporu #{i+1}: {cp.meter_value:.2f} kWh")
        await asyncio.sleep(2) [cite: 203]
        
    await cp.stop_charging() [cite: 204]
    logging.info(f">> NORMAL AKIŞ SONLANDI. TOPLAM RAPORLANAN: {cp.meter_value:.2f} kWh")

async def run_normal():
    # Websockets bağlantısı ve subprotocol tanımı [cite: 191]
    async with websockets.connect(CSMS_URI, subprotocols=["ocpp1.6"]) as ws:
        cp = SimulatedChargePoint(CP_ID, ws) [cite: 192]
        await asyncio.gather(
            cp.start(), [cite: 195]
            normal_flow(cp), # Bizim senaryo akışımız [cite: 197]
        )

# -----------------------------------------------------------
# ATTACK MODU: Sayaç Manipülasyonu (Enerji Hırsızlığı)
# -----------------------------------------------------------

async def attack_flow(cp: SimulatedChargePoint):
    logging.error(">> SALDIRI AKIŞI BAŞLIYOR: ENERJİ MANİPÜLASYONU...") [cite: 226]
    await cp.send_boot_notification() [cite: 217]
    await cp.start_charging() [cite: 218]
    
    real_consumption_tracker = 0.0
    
    for i in range(5): [cite: 219]
        # Saldırı: Gerçek Tüketim (0.5 kWh) > Raporlanan Tüketim (0.1 kWh)
        await cp.simulate_meter_values_attack(real_step_kwh=0.5, reported_step_kwh=0.1) 
        real_consumption_tracker += 0.5 
        logging.error(f"   [SALDIRI RAPORU] Raporlanan: {cp.meter_value:.2f} kWh (Gerçek Harcanan: {real_consumption_tracker:.2f} kWh)")
        await asyncio.sleep(2) [cite: 221]

    # İşlem StopTransaction ile düşük değer raporlanarak sonlandırılır.
    await cp.stop_charging()
    logging.error(f">> SALDIRI SONLANDI. CSMS'e TOPLAM RAPOR: {cp.meter_value:.2f} kWh (Gerçekte {real_consumption_tracker:.2f} kWh harcandı.)")


async def run_attack():
    async with websockets.connect(CSMS_URI, subprotocols=["ocpp1.6"]) as ws: [cite: 207]
        cp = SimulatedChargePoint(CP_ID, ws) [cite: 208]
        await asyncio.gather(
            cp.start(), [cite: 210]
            attack_flow(cp), [cite: 211]
        )

def run_scenario(mode: str = "normal"): [cite: 224]
    if mode == "attack":
        logging.error("A SALDIRI MODU BAŞLIYOR...") [cite: 226]
        asyncio.run(run_attack()) [cite: 227]
    else:
        logging.info(" NORMAL MOD BAŞLIYOR...") [cite: 229]
        asyncio.run(run_normal()) [cite: 229]
