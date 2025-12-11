# Dosya: Simulasyon/berat_time_desync/cp_simulator.py
import asyncio
import logging
from datetime import datetime

# CRITICAL: Core CSMS'e event üretmek için zorunlu import
from Simulasyon.core.event_bus import emit_event 
# Saldırı verisini hazırlayan modül
# NOTE: Bu dosya, scenario.py'den içe aktarılan payload_generator.py'yi temsil eder.

# Senaryo Tanımlayıcıları
CP_ID = "CP_BERAT"
SCENARIO_NAME = "TimeDesync" 

# --- GÖREVLER (Attack/Normal) ---

async def send_attack_meter_values(get_manipulated_data):
    """Saldırı verilerini içeren MeterValues akışını gönderir (Attack mod için)."""
    
    for i in range(1, 4): # 3 adet MeterValues gönder
        await asyncio.sleep(5)
        
        # Manipülasyon verisini al
        data = get_manipulated_data()
        
        # CRITICAL: EMIT EVENT formatında MeterValues gönderimi
        emit_event(
            senaryo=SCENARIO_NAME,
            cp_id=CP_ID,
            message_type="MeterValues",
            timestamp=data["timestamp"],       # MANİPÜLE EDİLMİŞ ZAMAN
            meter_value=data["reported_kwh"],  # MANİPÜLE EDİLMİŞ DEĞER
            transaction_id=data["transaction_id"],
            source="ATTACKER"
        )
        print(f"[CP_BERAT] 💣 Anomali MeterValue gönderildi ({i}/3).")


async def send_normal_meter_values():
    """Normal (anomalisiz) MeterValues akışını gönderir (Normal mod için)."""
    
    for i in range(1, 4): # 3 adet MeterValues gönder
        await asyncio.sleep(5)
        
        # Normal, temiz MeterValues gönderme
        emit_event(
            senaryo=SCENARIO_NAME,
            cp_id=CP_ID,
            message_type="MeterValues",
            timestamp=datetime.now().isoformat(), # Normal zaman
            meter_value=50.0, # Normal değer
            transaction_id=999,
            source="CP"
        )
        print(f"[CP_BERAT] 🟢 Normal MeterValue gönderildi ({i}/3).")


async def cp_event_flow(mode="ATTACK", get_manipulated_data=None):
    """CP'nin zorunlu BootNotification ve Transaction akışını yönetir."""
    
    # --- ZORUNLU OCPP AKIŞI ---
    
    # 1. BootNotification
    emit_event(senaryo=SCENARIO_NAME, cp_id=CP_ID, message_type="BootNotification", source="CP")
    await asyncio.sleep(1) 

    # 2. Authorize (CP İsteği)
    emit_event(senaryo=SCENARIO_NAME, cp_id=CP_ID, message_type="Authorize", idTag="BERAT123", source="CP")
    await asyncio.sleep(1)
    
    # 2.5. KRİTİK EKLEME: Authorize.conf (CSMS Onayı)
    # Bu, "AUTH_BYPASS" yanlış alarmını engeller.
    emit_event(
        senaryo=SCENARIO_NAME,
        cp_id=CP_ID,
        message_type="Authorize.conf",
        auth_status="Accepted", # Kabul edildi onayı
        idTag="BERAT123",
        source="CSMS" # Kaynak CSMS olmalı
    )
    await asyncio.sleep(1)


    # 3. StartTransaction (CP işleme başlar)
    emit_event(senaryo=SCENARIO_NAME, cp_id=CP_ID, message_type="StartTransaction", transaction_id=999, source="CP")
    await asyncio.sleep(1)

    # 4. MeterValues Akışını Başlat
    if mode == "ATTACK" and get_manipulated_data:
        await send_attack_meter_values(get_manipulated_data)
    else:
        await send_normal_meter_values()

    # 5. StopTransaction
    emit_event(senaryo=SCENARIO_NAME, cp_id=CP_ID, message_type="StopTransaction", transaction_id=999, source="CP")
    await asyncio.sleep(1)

    # 6. Status Notification Akışı
    emit_event(senaryo=SCENARIO_NAME, cp_id=CP_ID, message_type="StatusNotification", status="Available", source="CP")
    print(f"[CP_BERAT] ✅ Senaryo Akışı Tamamlandı.")
