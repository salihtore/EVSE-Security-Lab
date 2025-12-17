import asyncio
import logging
import websockets
from ocpp.v16.enums import ChargePointStatus

# Aynı klasördeki charge_point.py modülünden sınıfı çekiyoruz
# Not: run_all.py üzerinden çalıştırılacağı için import yolu 'Simulasyon...' şeklinde olabilir
# ancak aynı dizindeysen bu import çalışır.
try:
    from .charge_point import SimulatedChargePoint
except ImportError:
    from charge_point import SimulatedChargePoint

logging.basicConfig(level=logging.INFO)

CP_ID = "CP_OMER_FLOOD"
CSMS_URL = f"ws://127.0.0.1:9000/{CP_ID}"

# --- NORMAL AKIŞ (Referans) ---
async def run_normal():
    logging.info(f"✔ NORMAL MOD BAŞLIYOR: {CP_ID}")
    async with websockets.connect(CSMS_URL, subprotocols=["ocpp1.6"]) as ws:
        cp = SimulatedChargePoint(CP_ID, ws)
        await asyncio.gather(
            cp.start(),
            normal_flow(cp),
        )

async def normal_flow(cp: SimulatedChargePoint):
    await cp.send_boot_notification()
    await asyncio.sleep(1)
    
    # 1. Status Available
    await cp.send_status_notification(ChargePointStatus.available)
    
    # 2. Şarjı Başlat (Normal Enerji Artışı)
    logging.info("Normal şarj başlatılıyor...")
    await cp.start_charging(id_tag="TAG_NORMAL_USER")
    
    # 3. 5 Adım Boyunca Enerji Tüket (Her adımda 0.5 kWh artar)
    for _ in range(5):
        await asyncio.sleep(2)
        await cp.simulate_meter_values(step_kwh=0.5)
        
    # 4. Şarjı Durdur
    await cp.stop_charging(reason="EVDisconnected")
    logging.info("Normal şarj bitti.")

# --- SALDIRI AKIŞI (Zero-Energy Flood) ---
async def run_attack():
    logging.error(f"⚠ SALDIRI MODU BAŞLIYOR: {CP_ID} (Zero-Energy Flood)")
    async with websockets.connect(CSMS_URL, subprotocols=["ocpp1.6"]) as ws:
        cp = SimulatedChargePoint(CP_ID, ws)
        await asyncio.gather(
            cp.start(),
            attack_flow(cp),
        )

async def attack_flow(cp: SimulatedChargePoint):
    """
    Raporun Senaryosu: CAN-Bus Replay Attack.
    Araç sürekli 'StopCharging' (0 enerji) sinyali yolluyor.
    Bu da CSMS üzerinde bir sel (flood) oluşturuyor.
    """
    await cp.send_boot_notification()
    await asyncio.sleep(1)
    
    # FLOOD DÖNGÜSÜ: 3 Kez Tekrarla
    for i in range(3):
        logging.info(f"--- FLOOD ATTACK ITERATION {i+1} ---")
        
        # 1. Hazır Ol
        await cp.send_status_notification(ChargePointStatus.available)
        await asyncio.sleep(0.2) # Hızlı
        
        # 2. Şarjı Başlat (Meter 0 ile başla)
        # Saldırgan ID kullanıyoruz
        await cp.start_charging(id_tag="TAG_ATTACKER_01", meter_start=0)
        
        # 3. MeterValues Gönder (Ama hep 0 kWh - Replay Attack etkisi)
        # step_kwh yok, force_value=0 var.
        for _ in range(3):
            await asyncio.sleep(0.5) # Çok kısa süre
            await cp.simulate_meter_values(force_value=0)
            
        # 4. Hemen Kapat (0 Tüketimle)
        await cp.stop_charging(reason="EVDisconnected")
        logging.info(f"Iteration {i+1} completed with 0 kWh.")
        
        await asyncio.sleep(1) # Bir sonraki flood dalgası için az bekle

    logging.info("Saldırı senaryosu tamamlandı.")

# --- ANA ÇALIŞTIRICI ---
def run_scenario(mode: str = "normal"):
    if mode == "attack":
        asyncio.run(run_attack())
    else:
        asyncio.run(run_normal())

if __name__ == "__main__":
    # Test için doğrudan çalıştırılabilir
    # python scenario.py (varsayılan normal)
    # python scenario.py attack (bunun için sys.argv bakmak gerekir ama şimdilik manuel test)
    run_scenario("attack")
