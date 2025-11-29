import asyncio
import logging
import websockets
from datetime import datetime
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call_result
from ocpp.routing import on

# Log ayarı
logging.basicConfig(level=logging.INFO, format='%(asctime)s - CSMS - %(message)s')

class ChargePointHandler(cp):
    def __init__(self, id, connection):
        super().__init__(id, connection)
        self.transaction_active = False 

    @on('BootNotification')
    async def on_boot_notification(self, charge_point_vendor, charge_point_model, **kwargs):
        logging.info("BootNotification alındı. Cihaz kabul ediliyor.")
        # YENİ VERSİYON UYUMU: 'Payload' takısı yok
        return call_result.BootNotification(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status='Accepted'
        )

    @on('StartTransaction')
    async def on_start_transaction(self, connector_id, id_tag, meter_start, timestamp, **kwargs):
        self.transaction_active = True
        logging.info(f"StartTransaction: Şarj başladı. (Meter: {meter_start} kWh)")
        return call_result.StartTransaction(
            transaction_id=1,
            id_tag_info={"status": "Accepted"}
        )

    @on('StopTransaction')
    async def on_stop_transaction(self, meter_stop, timestamp, transaction_id, **kwargs):
        self.transaction_active = False
        logging.info(f"StopTransaction: Şarj DURDURULDU. (Meter: {meter_stop} kWh)")
        logging.info("--- Session Active: FALSE ---")
        return call_result.StopTransaction(
            id_tag_info={"status": "Accepted"}
        )

    @on('MeterValues')
    async def on_meter_values(self, connector_id, meter_value, **kwargs):
        try:
            current_value = float(meter_value[0]['sampled_value'][0]['value'])
            log_msg = f"MeterValues Alındı: {current_value} kWh"
        except:
            current_value = 0
            log_msg = "MeterValues Alındı (Değer okunamadı)"
        
        # RAPORDAKİ KURAL-1: ANOMALİ TESPİTİ
        if not self.transaction_active:
             logging.warning(f"!!! ANOMALİ TESPİT EDİLDİ !!! -> {log_msg}")
             logging.warning("Sebep: StopTransaction sonrası enerji akışı devam ediyor (Phantom Current).")
        else:
            logging.info(log_msg)
        return call_result.MeterValues()

# --- BAĞLANTIYI KABUL ETMEK İÇİN EN SADE FONKSİYON ---
async def on_connect(websocket):
    # Hiçbir header kontrolü yapmadan doğrudan kabul ediyoruz
    try:
        # Adresi almaya çalış, alamazsan varsayılan isim ver
        if hasattr(websocket, 'path'):
            charge_point_id = websocket.path.strip('/')
        else:
            charge_point_id = "CP_Unknown"
            
        logging.info(f"Bağlantı Geldi: {charge_point_id}")
        cp_instance = ChargePointHandler(charge_point_id, websocket)
        await cp_instance.start()
    except Exception as e:
        logging.error(f"Bağlantı hatası: {e}")

async def main():
    # Ping hatasını önlemek için ping_interval=None
    server = await websockets.serve(on_connect, 'localhost', 9000, subprotocols=['ocpp1.6'], ping_interval=None)
    logging.info("CSMS Sunucusu Başlatıldı. 9000 portu dinleniyor...")
    await server.wait_closed()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Sunucu durduruldu.")