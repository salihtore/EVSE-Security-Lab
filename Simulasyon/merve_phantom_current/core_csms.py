
import asyncio
import logging
import websockets
from datetime import datetime
from ocpp.routing import on
from ocpp.v16 import ChargePoint as Cp
from ocpp.v16 import call_result
from ocpp.v16.enums import RegistrationStatus

logging.basicConfig(level=logging.INFO)

class CSMS(Cp):
    def __init__(self, charge_point_id, websocket):
        super().__init__(charge_point_id, websocket)
        self.transaction_active = False

    @on('BootNotification')
    async def on_boot_notification(self, charge_point_vendor, charge_point_model, **kwargs):
        logging.info(f"Boot Bildirimi: {charge_point_vendor}")
        return call_result.BootNotification(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status=RegistrationStatus.accepted
        )

    @on('StatusNotification')
    async def on_status_notification(self, connector_id, error_code, status, **kwargs):
        logging.info(f"Status: {status}")
        return call_result.StatusNotification()

    @on('StartTransaction')
    async def on_start_transaction(self, connector_id, id_tag, meter_start, timestamp, **kwargs):
        self.transaction_active = True
        logging.info(f"ŞARJ BAŞLADI (ID: {id_tag})")
        return call_result.StartTransaction(
            transaction_id=1,
            id_tag_info={'status': 'Accepted'}
        )

    @on('StopTransaction')
    async def on_stop_transaction(self, meter_stop, timestamp, transaction_id, **kwargs):
        self.transaction_active = False
        logging.info(f"ŞARJ DURDURULDU. Son Sayaç: {meter_stop}")
        return call_result.StopTransaction(
            id_tag_info={'status': 'Accepted'}
        )

    @on('MeterValues')
    async def on_meter_values(self, connector_id, meter_value, **kwargs):
        try:
            # DÜZELTME BURADA: Kütüphane 'sampledValue'yu 'sampled_value' yapıyor.
            # Biz her ihtimale karşı ikisini de deneyen sağlam bir yapı kuralım.
            
            val = None
            reading = meter_value[0] # İlk okuma
            
            # Dictionary ise (Genelde böyle gelir)
            if isinstance(reading, dict):
                # Önce 'sampled_value' (yeni sürüm), yoksa 'sampledValue' (eski sürüm) dene
                samples = reading.get('sampled_value') or reading.get('sampledValue')
                if samples:
                    val = samples[0].get('value')
            else:
                # Nesne ise (Object notation)
                if hasattr(reading, 'sampled_value'):
                    val = reading.sampled_value[0].value
                elif hasattr(reading, 'sampledValue'):
                    val = reading.sampledValue[0].value

            # Değeri bulduysak kontrol et
            if val is not None:
                # logging.info(f"Sayaç Okundu: {val}") # Kalabalık yapmasın
                
                if not self.transaction_active:
                     # İŞTE O AN:
                     logging.warning(f"!!! ANOMALİ TESPİT EDİLDİ !!! -> {val} kWh")
                     logging.warning("Sebep: StopTransaction sonrası enerji akışı (Phantom Current).")
            else:
                logging.error("Veri formatı çözülemedi (Debug: sampled_value eksik)")

        except Exception as e:
            logging.error(f"Veri Okuma Hatası: {e}")
        
        return call_result.MeterValues()

async def on_connect(websocket):
    try:
        path = "Unknown"
        if hasattr(websocket, 'request') and hasattr(websocket.request, 'path'):
            path = websocket.request.path
        elif hasattr(websocket, 'path'):
            path = websocket.path
            
        charge_point_id = path.strip('/') if path else "Unknown"
        logging.info(f"Yeni Bağlantı Kabul Edildi: {charge_point_id}")
        
        cp = CSMS(charge_point_id, websocket)
        await cp.start()
    except Exception as e:
        logging.error(f"Bağlantı Hatası: {e}")

async def main():
    server = await websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6'])
    logging.info("CSMS Sunucusu 9000 portunda Hazır...")
    await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())
