# Dosya: Simulasyon/berat_time_desync/payload_generator.py
import time
from datetime import datetime, timezone, timedelta

# --- SALDIRI PARAMETRELERİ ---
TIME_SHIFT_HOURS = 10
ACTUAL_CONSUMPTION_KWH = 50.0 
REPORTED_CONSUMPTION_KWH = 35.0 # Manipüle edilen değer

def get_manipulated_data(cp_id):
    """Zaman ve değer manipülasyonunu yaparak anomali verisini döndürür."""
    now = time.time()
    # 1. ZAMAN MANİPÜLASYONU (UTC)
    dt = datetime.now(timezone.utc) - timedelta(hours=TIME_SHIFT_HOURS)
    recorded_time_str = dt.isoformat(timespec='seconds').replace('+00:00', 'Z')
    recorded_epoch = dt.timestamp()
    
    # Saldırının özeti (Loglama amaçlı)
    print(f"[PAYLOAD_GEN] 💾 Kaydırılmış Zaman: {recorded_time_str.split('T')[1]}... ")
    print(f"[PAYLOAD_GEN] ⚡ {ACTUAL_CONSUMPTION_KWH} yerine {REPORTED_CONSUMPTION_KWH} kWh raporluyor.")
    
    return {
        "cp_id": cp_id,                    
        "message_type": "MeterValues",     
        "timestamp": now,                  
        "csms_time": now,                  
        "cp_timestamp": now + 1000,        
        "meter_kWh": 35.0,
        "plug_state": True,
        "session_active": True,
    }