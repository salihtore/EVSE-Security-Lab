import asyncio
import logging
import websockets
import json
from datetime import datetime, timezone, timedelta

logging.basicConfig(level=logging.INFO)

# --- FİNANSAL VE TARİFE MANTIĞI ---
HIGH_TARIFF_START = 12
HIGH_TARIFF_END = 20
STATIK_CIHAZ_ID = "CP_TimeShift" # Path sorunu nedeniyle cihaz ID'si statik

def timestamp_olustur():
    """OCPP BootNotification yanıtı için zaman damgası oluşturur."""
    return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')

def call_result_olustur(mesajId, payload):
    """OCPP CallResult (onay) mesajı oluşturur."""
    return json.dumps([3, mesajId, payload])

def alarm_ver(recorded_time, actual_time, consumption):
    """Zaman kaydırma saldırısı durumunda alarm basar."""
    print("\n" + "="*70)
    print(f"🚨 ALARM - ZAMAN KAYDIRMA ANOMALİSİ TESPİT EDİLDİ! (TEK ARGÜMAN)")
    print("="*70)
    print(f"║  Gerçek Tüketim : {consumption} kWh")
    print(f"║  Gerçek Zaman   : {actual_time.strftime('%d.%m %H:%M')} (Yüksek Tarife)")
    print(f"║  Raporlanan Zaman: {recorded_time.strftime('%d.%m %H:%M')} (Düşük Tarife)")
    print(f"║  Durum          : GELİR KAYBI RİSKİ! Yanlış Faturalandırma Oluştu.")
    print("="*70 + "\n")

def check_tariff_anomaly(recorded_time, actual_time, actual_consumption):
    """Kayıtlı ve Gerçek Zamanı Karşılaştırarak Finansal Anomalileri Kontrol Eder."""
    
    is_actual_high_tariff = HIGH_TARIFF_START <= actual_time.hour < HIGH_TARIFF_END
    is_recorded_low_tariff = not (HIGH_TARIFF_START <= recorded_time.hour < HIGH_TARIFF_END)

    print(f"\n[SUNUCU] ⏰ Gerçek Zaman: {actual_time.strftime('%H:%M')} (Yüksek Tarife? {is_actual_high_tariff})")
    print(f"[SUNUCU] 💾 Kayıtlı Zaman: {recorded_time.strftime('%H:%M')} (Düşük Tarife? {is_recorded_low_tariff})")

    if is_actual_high_tariff and is_recorded_low_tariff and actual_consumption > 0:
        alarm_ver(recorded_time, actual_time, actual_consumption)
        return True
    return False

# YENİ İŞLEYİCİ FONKSİYONU: SADECE websocket alacak
async def handle_connection(websocket): 
    """Gelen WebSocket bağlantılarını işler (Sadece websocket argümanı alır)."""
    cihaz_id = STATIK_CIHAZ_ID # Statik ID kullanılır
    print(f"[SUNUCU] 🔗 Yeni bağlantı: {cihaz_id}")

    try:
        async for message in websocket:
            mesaj = json.loads(message)
            [mesaj_tipi, mesaj_id, action, payload] = mesaj
            
            if action == 'BootNotification':
                print(f"[SUNUCU] 📡 BootNotification alındı: {cihaz_id}")
                
                yanit = call_result_olustur(mesaj_id, {
                    "status": "Accepted",
                    "currentTime": timestamp_olustur(),
                    "interval": 10
                })
                await websocket.send(yanit)
                
            elif action == 'MeterValues':
                actual_time = datetime.now(timezone.utc)
                
                meter_value = payload['meterValue'][0]
                recorded_time = datetime.fromisoformat(meter_value['timestamp'].replace('Z', '+00:00'))
                
                consumption_value = next(s['value'] for s in meter_value['sampledValue'] if s['measurand'] == 'Energy.Active.Import.Register')
                consumption = float(consumption_value)
                
                check_tariff_anomaly(recorded_time, actual_time, consumption)

                await websocket.send(call_result_olustur(mesaj_id, {}))

    except websockets.exceptions.ConnectionClosed:
        print(f"[SUNUCU] 🔌 Bağlantı kapandı: {cihaz_id}")
    except Exception as e:
        print(f"[SUNUCU] ❌ İşleme Hatası: {e}. Bağlantı Kapatılıyor.")
        
# MAIN FONKSİYONU
async def main():
    print("==================================================")
    print(" ZAMAN KAYDIRMA TESPİT SUNUCUSU (TEK ARGÜMAN) - Port 9000")
    print("==================================================")
    
    # Websockets'i başlatırken SUBPROTOCOLS'ü kaldırıyoruz ve path'i ihmal ediyoruz
    async with websockets.serve(handle_connection, '0.0.0.0', 9000): 
        print(f"[SUNUCU] 🚀 WebSocket sunucusu başlatıldı: ws://0.0.0.0:9000")
        await asyncio.Future()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSunucu kapatılıyor...")