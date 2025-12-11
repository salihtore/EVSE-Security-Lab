# Dosya: Simulasyon/berat_time_desync/cp_simulator.py
import asyncio
from datetime import datetime, timezone

# Core için zorunlu event üreticisi
from Simulasyon.core.event_bus import emit_event 


# Senaryo meta verisi
CP_ID = "CP_BERAT"
SCENARIO_NAME = "TimeDesync"
IDTAG = "BERAT123"
TX_ID = 999


# ============================================================
# NORMAL METERVALUES
# ============================================================

async def send_normal_meter_values():
    """
    Normal akışta Core hiçbir alarm üretmemelidir.
    Tüm timestamp, meter_kWh ve transactionId tutarlıdır.
    """
    for i in range(1, 4):

        await asyncio.sleep(5)

        now_iso = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')

        emit_event(
            senaryo=SCENARIO_NAME,
            cp_id=CP_ID,
            message_type="MeterValues",
            meter_kWh=50.0,  
            transactionId=TX_ID,
            cp_timestamp=datetime.now(timezone.utc).timestamp(),
            timestamp=now_iso,
            source="CP"
        )

        print(f"[CP_BERAT] 🟢 Normal MeterValue gönderildi ({i}/3).")


# ============================================================
# ATTACK METERVALUES
# ============================================================

async def send_attack_meter_values(get_manipulated_data):
    """
    Anomali sadece MeterValues aşamasında uygulanır.
    """
    for i in range(1, 3 + 1):

        await asyncio.sleep(5)

        # Kullanıcı manipülasyon fonksiyonu
        data = get_manipulated_data()

        emit_event(
            senaryo=SCENARIO_NAME,
            cp_id=CP_ID,
            message_type="MeterValues",
            meter_kWh=data["reported_kwh"],
            transactionId=data["transaction_id"],
            cp_timestamp=data["cp_timestamp"],
            timestamp=data["timestamp"],
            source="CP"
        )

        print(f"[CP_BERAT] 💣 Anomali MeterValue gönderildi ({i}/3).")



# ============================================================
# ANA AKIŞ (BOOT → AUTH → STARTTXN → METERS → STOP → STATUS)
# ============================================================

async def cp_event_flow(mode="NORMAL", get_manipulated_data=None):
    """
    CP'nin tüm zorunlu OCPP akışını standarda uygun şekilde yürütür.
    """
    print(f"\n[CP_BERAT] ► Senaryo Modu: {mode}")

    # ------------------------------------------------------------
    # 1) BootNotification — ZORUNLU
    # ------------------------------------------------------------
    emit_event(
        senaryo=SCENARIO_NAME,
        cp_id=CP_ID,
        message_type="BootNotification",
        source="CP",
        cp_timestamp=datetime.now(timezone.utc).timestamp()
    )
    await asyncio.sleep(1)

    # ------------------------------------------------------------
    # 2) Authorize — ZORUNLU
    # ------------------------------------------------------------
    emit_event(
        senaryo=SCENARIO_NAME,
        cp_id=CP_ID,
        message_type="Authorize",
        idTag=IDTAG,
        source="CP",
        cp_timestamp=datetime.now(timezone.utc).timestamp()
    )
    await asyncio.sleep(0.3)

    # CSMS Onayı — sadece log için
    emit_event(
        senaryo=SCENARIO_NAME,
        cp_id=CP_ID,
        message_type="Authorize.conf",
        auth_status="Accepted",
        idTag=IDTAG,
        source="CSMS",
        cp_timestamp=datetime.now(timezone.utc).timestamp()
    )
    await asyncio.sleep(0.3)

    # ------------------------------------------------------------
    # 3) StartTransaction — ZORUNLU
    # ------------------------------------------------------------
    emit_event(
        senaryo=SCENARIO_NAME,
        cp_id=CP_ID,
        message_type="StartTransaction",
        transactionId=TX_ID,
        idTag=IDTAG,
        session_active=True,
        source="CP",
        cp_timestamp=datetime.now(timezone.utc).timestamp()
    )
    await asyncio.sleep(1)

    # ------------------------------------------------------------
    # 4) MeterValues — MODA GÖRE SEÇİLİR
    # ------------------------------------------------------------
    if mode == "ATTACK" and get_manipulated_data:
        await send_attack_meter_values(get_manipulated_data)
    else:
        await send_normal_meter_values()

    # ------------------------------------------------------------
    # 5) StopTransaction — ZORUNLU
    # ------------------------------------------------------------
    emit_event(
        senaryo=SCENARIO_NAME,
        cp_id=CP_ID,
        message_type="StopTransaction",
        transactionId=TX_ID,
        idTag=IDTAG,
        session_active=False,
        source="CP",
        cp_timestamp=datetime.now(timezone.utc).timestamp()
    )
    await asyncio.sleep(1)

    # ------------------------------------------------------------
    # 6) StatusNotification Zinciri — ZORUNLU
    # ------------------------------------------------------------
    emit_event(
        senaryo=SCENARIO_NAME,
        cp_id=CP_ID,
        message_type="StatusNotification",
        status="Charging",
        source="CP",
        cp_timestamp=datetime.now(timezone.utc).timestamp()
    )

    emit_event(
        senaryo=SCENARIO_NAME,
        cp_id=CP_ID,
        message_type="StatusNotification",
        status="Finishing",
        source="CP",
        cp_timestamp=datetime.now(timezone.utc).timestamp()
    )

    emit_event(
        senaryo=SCENARIO_NAME,
        cp_id=CP_ID,
        message_type="StatusNotification",
        status="Available",
        source="CP",
        cp_timestamp=datetime.now(timezone.utc).timestamp()
    )

    print(f"[CP_BERAT] ✅ Senaryo Akışı Tamamlandı.")
