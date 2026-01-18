# Dosya: Simulasyon/berat_time_desync/payload_generator.py
import time
from datetime import datetime, timezone, timedelta

# --- SALDIRI PARAMETRELERİ ---
TIME_SHIFT_HOURS = 10
ACTUAL_CONSUMPTION_KWH = 50.0 
REPORTED_CONSUMPTION_KWH = 35.0 # Manipüle edilen değer

def get_drifting_data(cp_id, iteration):
    """Zaman kaymasını kademeli olarak artırır (Drift)."""
    now = time.time()
    
    # Her iterasyonda +120 saniye kayma (Drift)
    # 1. iter: 120s, 2. iter: 240s, 3. iter: 360s (>300s limit)
    drift_seconds = iteration * 120
    
    cp_timestamp = now + drift_seconds
    
    print(f"[PAYLOAD_GEN] ⏳ Zaman Kayması (Drift): +{drift_seconds} sn")
    
    return {
        "cp_id": cp_id,                    
        "message_type": "MeterValues",     
        "timestamp": now,                  
        "csms_time": now,                  
        "cp_timestamp": cp_timestamp,      
        "meter_kWh": 35.0, # Sabit veya artan yapılabilir
        "plug_state": True,
        "session_active": True,
        "drift_seconds": drift_seconds
    }

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