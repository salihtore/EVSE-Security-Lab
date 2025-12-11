# Dosya: Simulasyon/berat_time_desync/cp_simulator.py
import asyncio
import logging
from datetime import datetime

# CRITICAL: Core CSMS'e event üretmek için zorunlu import
from Simulasyon.core.event_bus import emit_event 

# Senaryo Tanımlayıcıları
CP_ID = "CP_BERAT"
SCENARIO_NAME = "TimeDesync" 

# --- GÖREVLER (Attack/Normal) ---
# NOTE: send_attack_meter_values ve send_normal_meter_values fonksiyonları bu blokta yer almaz ancak 
# diğer dosyalardan doğru bir şekilde import edilmiştir ve doğru çalışmaktadır. 

async def send_attack_meter_values(get_manipulated_data):
    # Bu fonksiyonun içeriği önceki yanıtlarda olduğu gibi kalır.
    for i in range(1, 4):
        await asyncio.sleep(5)
        data = get_manipulated_data()
        emit_event(
            senaryo=SCENARIO_NAME,
            cp_id=CP_ID,
            message_type="MeterValues",
            timestamp=data["timestamp"],
            meter_value=data["reported_kwh"],
            transaction_id=data["transaction_id"],
            source="ATTACKER"
        )
        print(f"[CP_BERAT] 💣 Anomali MeterValue gönderildi ({i}/3).")


async def send_normal_meter_values():
    # Bu fonksiyonun içeriği önceki yanıtlarda olduğu gibi kalır.
    for i in range(1, 4):
        await asyncio.sleep(5)
        emit_event(
            senaryo=SCENARIO_NAME,
            cp_id=CP_ID,
            message_type="MeterValues",
            timestamp=datetime.now().isoformat(),
            meter_value=50.0,
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
    # Bu, CSMS'in yetkiyi verdiğini simüle eder.
    emit_event(
        senaryo=SCENARIO_NAME,
        cp_id=CP_ID,
        message_type="Authorize.conf",
        auth_status="Accepted", 
        idTag="BERAT123", 
        source="CSMS" 
    )
    await asyncio.sleep(1)


    # 3. StartTransaction (KRİTİK DÜZELTME BURADA!)
    # StartTransaction olayına idTag eklenmelidir ki CSMS, onayla ilişkilendirsin ve AUTH_BYPASS hatası vermesin.
    emit_event(
        senaryo=SCENARIO_NAME,
        cp_id=CP_ID,
        message_type="StartTransaction",
        transaction_id=999,
        idTag="BERAT123", # <--- EKLENEN KRİTİK ALAN
        source="CP"
    )
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
