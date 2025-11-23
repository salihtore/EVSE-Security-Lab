import asyncio
import logging
from ocpp.v16 import call_result
from ocpp.v16.enums import Action
from ocpp.charge_point import ChargePoint
from ocpp.routing import on

logging.basicConfig(level=logging.INFO)

# Basit bir CSMS (Sunucu) simülasyonu
class ChargingStationManagementSystem(ChargePoint):
    
    # Gelen MeterValues mesajını dinle
    @on(Action.MeterValues)
    def on_meter_values(self, connector_id, meter_value, **kwargs):
        
        # Sayaç değerini çıkar
        energy_kwh = meter_value[0]['sampled_value'][0]['value']
        
        # Gelen veriyi logla
        logging.info(f"⚡ [SUNUCU] Şarj İstasyonu {self.id} -> Bağlantı {connector_id} için alınan kWh: {energy_kwh}")
        
        # Şarj istasyonuna başarılı yanıt gönder
        return call_result.MeterValues(
            **kwargs
        )

# Sunucuyu başlatma fonksiyonu
async def main():
    # WebSocket sunucusunu belirtilen adreste başlat
    # OCPP iletişimi için tipik olarak 9000-9003 aralığı kullanılır
    server = await asyncio.create_server(
        lambda websocket, path: ChargingStationManagementSystem(websocket, self.id),
        '0.0.0.0', 9003
    )
    logging.info("🌟 [SUNUCU] CSMS simülasyonu 'ws://0.0.0.0:9003' adresinde başlatıldı. Bağlantı bekleniyor...")
    
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Sunucu kapatılıyor...")
