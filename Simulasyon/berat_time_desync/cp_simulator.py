# Dosya: Simulasyon/berat_time_desync/cp_simulator.py
import asyncio
import logging
from datetime import datetime, timezone

# CRITICAL: Core CSMS'e event üretmek için zorunlu import
from Simulasyon.core.event_bus import emit_event 

# Senaryo Tanımlayıcıları
CP_ID = "CP_BERAT"
SCENARIO_NAME = "TimeDesync" 

# --- GÖREVLER (Attack/Normal) ---

async def send_attack_meter_values(get_manipulated_data):
    # Bu fonksiyonun içeriği önceki yanıtlarda olduğu gibi kalır.
    for i in range(1, 4):
        await asyncio.sleep(5)
        data = get_manipulated_data()
        emit_event(
            senaryo=SCENARIO_NAME,
            cp_id=CP_ID,
            message_type="MeterValues",
            # Core'un beklediği anahtar: meter_kWh
            meter_kWh=data["reported_kwh"],
            # transactionId camelCase ile Core tarafına uyumlu
            transactionId=data["transaction_id"],
            # Orijinal CP zaman bilgisinin epoch olarak da iletilmesi (Time Desync kontrolü için)
            cp_timestamp=data["cp_timestamp"],
            # Ayrıca ISO timestamp stringi debugging/log amaçlı
            timestamp=data["timestamp"],
            source="CP"
        )
        print(f"[CP_BERAT] 💣 Anomali MeterValue gönderildi ({i}/3).")


async def send_normal_meter_values(tx_id=999, idTag="BERAT123"):
    # Bu fonksiyonun içeriği önceki yanıtlarda olduğu gibi kalır.
    for i in range(1, 4):
        await asyncio.sleep(5)
        now_iso = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
        emit_event(
            senaryo=SCENARIO_NAME,
            cp_id=CP_ID,
            message_type="MeterValues",
            meter_kWh=50.0,
            transactionId=tx_id,
            cp_timestamp=datetime.now(timezone.utc).timestamp(),
            timestamp=now_iso,
            source="CP"
        )
        print(f"[CP_BERAT] 🟢 Normal MeterValue gönderildi ({i}/3).")


async def cp_event_flow(mode="ATTACK", get_manipulated_data=None):
    """CP'nin zorunlu BootNotification ve Transaction akışını yönetir."""
    
    # Sabit idTag kullanıyoruz — Core'un eşleştirme kuralı için aynı idTag her adımda gönderilmeli.
    IDTAG = "BERAT123"

    # --- ZORUNLU OCPP AKIŞI ---
    
    # 1. BootNotification
    emit_event(
        senaryo=SCENARIO_NAME,
        cp_id=CP_ID,
        message_type="BootNotification",
        source="CP",
        cp_timestamp=datetime.now(timezone.utc).timestamp()
    )
    await asyncio.sleep(1) 

    # 2. Authorize (CP İsteği)
    emit_event(
        senaryo=SCENARIO_NAME,
        cp_id=CP_ID,
        message_type="Authorize",
        idTag=IDTAG,
        source="CP",
        cp_timestamp=datetime.now(timezone.utc).timestamp()
    )
    await asyncio.sleep(0.2)

    # 2.5. KRİTİK EKLEME: Authorize.conf (CSMS Onayı)
    # Bu, CSMS'in yetkiyi verdiğini simüle eder. (Authorize.conf Core içinde kullanılmıyor ama log için bırakıyoruz)
    emit_event(
        senaryo=SCENARIO_NAME,
        cp_id=CP_ID,
        message_type="Authorize.conf",
        auth_status="Accepted",
        idTag=IDTAG,
        source="CSMS",
        cp_timestamp=datetime.now(timezone.utc).timestamp()
    )
    await asyncio.sleep(0.2)

    # 3. StartTransaction (KRİTİK DÜZELTME BURADA!)
    # StartTransaction olayına idTag eklenmelidir ki CSMS, onayla ilişkilendirsin ve AUTH_BYPASS hatası vermesin.
    emit_event(
        senaryo=SCENARIO_NAME,
        cp_id=CP_ID,
        message_type="StartTransaction",
        transactionId=999,          # camelCase ile core uyumu
        idTag=IDTAG,                # <--- CRITICAL: kesinlikle olmalı ve Authorize ile birebir aynı
        session_active=True,
        source="CP",
        cp_timestamp=datetime.now(timezone.utc).timestamp()
    )
    await asyncio.sleep(1)

    # 4. MeterValues Akışını Başlat
    if mode == "ATTACK" and get_manipulated_data:
        await send_attack_meter_values(get_manipulated_data)
    else:
        await send_normal_meter_values(tx_id=999, idTag=IDTAG)

    # 5. StopTransaction (aynı idTag ile bitiriyoruz)
    emit_event(
        senaryo=SCENARIO_NAME,
        cp_id=CP_ID,
        message_type="StopTransaction",
        transactionId=999,
        idTag=IDTAG,
        session_active=False,
        source="CP",
        cp_timestamp=datetime.now(timezone.utc).timestamp()
    )
    await asyncio.sleep(1)

    # 6. Status Notification Akışı
    emit_event(
        senaryo=SCENARIO_NAME,
        cp_id=CP_ID,
        message_type="StatusNotification",
        status="Available",
        source="CP",
        cp_timestamp=datetime.now(timezone.utc).timestamp()
    )
    print(f"[CP_BERAT] ✅ Senaryo Akışı Tamamlandı.")
