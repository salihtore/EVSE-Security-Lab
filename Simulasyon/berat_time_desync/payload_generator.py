# Dosya: Simulasyon/berat_time_desync/payload_generator.py
from datetime import datetime, timezone, timedelta

# --- SALDIRI PARAMETRELERİ ---
TIME_SHIFT_HOURS = 10
ACTUAL_CONSUMPTION_KWH = 50.0 
REPORTED_CONSUMPTION_KWH = 35.0 # Manipüle edilen değer

def get_manipulated_data():
    """Zaman ve değer manipülasyonunu yaparak anomali verisini döndürür."""
    
    # 1. ZAMAN MANİPÜLASYONU
    dt = datetime.now(timezone.utc) - timedelta(hours=TIME_SHIFT_HOURS)
    recorded_time_str = dt.isoformat(timespec='seconds').replace('+00:00', 'Z')
    
    # Saldırının özeti (Loglama amaçlı)
    print(f"[PAYLOAD_GEN] 💾 Kaydırılmış Zaman: {recorded_time_str.split('T')[1]}... ")
    print(f"[PAYLOAD_GEN] ⚡ {ACTUAL_CONSUMPTION_KWH} yerine {REPORTED_CONSUMPTION_KWH} kWh raporluyor.")
    
    return {
        "timestamp": recorded_time_str,
        "reported_kwh": REPORTED_CONSUMPTION_KWH,
        "transaction_id": 999 
    }
