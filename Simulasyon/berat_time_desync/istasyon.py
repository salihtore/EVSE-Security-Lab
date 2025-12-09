# Dosya: Simulasyon/berat_time_desync/istasyon.py
import asyncio
import logging
import json
from datetime import datetime, timezone, timedelta
import websockets
from .hacker import call_olust # Mesaj oluşturma fonksiyonunu kullan

def get_current_timestamp():
    """OCPP BootNotification yanıtı için zaman damgası oluşturur."""
    return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


async def istasyon_logic(websocket, mode="ATTACK"):
    """CP'nin BootNotification gönderimini ve genel mesaj döngüsünü yönetir."""
    
    boot_mesaj = call_olustar('BootNotification', 
                              {"chargePointModel": "Secure-CP-v1", "chargePointVendor": "Berat"}, 
                              "boot-001")
    await websocket.send(boot_mesaj)
    print(f"[CP_BERAT - {mode}] 📤 BootNotification gönderildi (Güvenli Akış Başladı).")

    try:
        async for message in websocket:
            mesaj = json.loads(message)
            [mesaj_tipi, mesaj_id, payload] = mesaj
            
            if mesaj_tipi == 3 and mesaj_id == "boot-001":
                print(f"[CP_BERAT - {mode}] ✅ BootNotification onayı alındı. Status: {payload.get('status')}")
            
            # Normal akışta (mode="NORMAL"), Heartbeat gönderimi gibi rutinler burada tanımlanabilir
            
            elif mesaj_tipi == 2:
                # CSMS'ten gelen RemoteStart/Stop gibi komutları işleme mantığı buraya gelir.
                pass
                
    except websockets.exceptions.ConnectionClosed:
        print(f"[CP_BERAT - {mode}] 🔌 Bağlantı kapandı.")
    except Exception as e:
        logging.error(f"[CP_BERAT - {mode}] İşlem hatası: {e}")
