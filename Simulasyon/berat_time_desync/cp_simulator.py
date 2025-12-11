# Dosya: Simulasyon/berat_time_desync/cp_simulator.py
import asyncio
from datetime import datetime, timezone

# CRITICAL: Core CSMS'e event üretmek için zorunlu import
from Simulasyon.core.event_bus import emit_event

# Senaryo Tanımlayıcıları
CP_ID = "CP_BERAT"
SCENARIO_NAME = "TimeDesync"
ID_TAG = "BERAT123"
TX_ID = 999


# ============================================================
# NORMAL METERVALUES
# ============================================================
async def send_normal_meter_values():
    """
    Normal akışta Core hiçbir alarm üretmemelidir.
    Tüm timestamp, meter_kWh ve transaction_id tutarlıdır.
    """
    for i in range(1, 4):
        await asyncio.sleep(5)

        now_iso = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')

        emit_event(
            senaryo=SCENARIO_NAME,
            cp_id=CP_ID,
            message_type="MeterValues",
            meter_kWh=50.0,
            transaction_id=TX_ID,
            cp_timestamp=datetime.now(timezone.utc).timestamp(),
            timestamp=now_iso,
            source="CP"
        )

        print(f"[{CP_ID}] 🟢 Normal MeterValue gönderildi ({i}/3).")


# ============================================================
# ATTACK METERVALUES
# ============================================================
async def send_attack_meter_values(get_manipulated_data):
    """
    Anomali sadece MeterValues aşamasında uygulanır.
    get_manipulated_data fonksiyonu payload_generator tarafında tanımlıdır ve
    aşağıdaki sözleşmeyi karşılamalıdır:
      {
        "timestamp": iso_string,
        "cp_timestamp": epoch_float,
        "reported_kwh": float,
        "transaction_id": int
      }
    """
    for i in range(1, 4):
        await asyncio.sleep(5)

        data = get_manipulated_data()

        emit_event(
            senaryo=SCENARIO_NAME,
            cp_id=CP_ID,
            message_type="MeterValues",
            meter_kWh=data["reported_kwh"],
            transaction_id=data["transaction_id"],
            cp_timestamp=data.get("cp_timestamp", datetime.now(timezone.utc).timestamp()),
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            source="CP"
        )

        print(f"[{CP_ID}] 💣 Anomali MeterValue gönderildi ({i}/3).")


# ============================================================
# ANA AKIŞ (BOOT → AUTHORIZE → STARTTXN → METERS → STOP → STATUS)
# ============================================================
async def cp_event_flow(mode="NORMAL", get_manipulated_data=None):
    """
    CP'nin tüm zorunlu OCPP akışını standarda uygun şekilde yürütür.
    mode: "NORMAL" veya "ATTACK"
    get_manipulated_data: attack modunda çağrılacak fonksiyon (payload_generator.get_manipulated_data)
    """
    print(f"\n[{CP_ID}] ► Senaryo Modu: {mode}")

    # 1) BootNotification (Zorunlu)
    emit_event(
        senaryo=SCENARIO_NAME,
        cp_id=CP_ID,
        message_type="BootNotification",
        source="CP",
        cp_timestamp=datetime.now(timezone.utc).timestamp()
    )
    await asyncio.sleep(1)

    # 2) Authorize (Zorunlu adım — core'un last_auth_idTag kontrolü için)
    emit_event(
        senaryo=SCENARIO_NAME,
        cp_id=CP_ID,
        message_type="Authorize",
        id_tag=ID_TAG,
        source="CP",
        cp_timestamp=datetime.now(timezone.utc).timestamp()
    )
    await asyncio.sleep(0.25)

    # 2.5) Authorize.conf (CSMS onayı simülasyonu — log amaçlı)
    emit_event(
        senaryo=SCENARIO_NAME,
        cp_id=CP_ID,
        message_type="Authorize.conf",
        auth_status="Accepted",
        id_tag=ID_TAG,
        source="CSMS",
        cp_timestamp=datetime.now(timezone.utc).timestamp()
    )
    await asyncio.sleep(0.25)

    # 3) StartTransaction (Zorunlu)
    emit_event(
        senaryo=SCENARIO_NAME,
        cp_id=CP_ID,
        message_type="StartTransaction",
        transaction_id=TX_ID,
        id_tag=ID_TAG,
        session_active=True,
        source="CP",
        cp_timestamp=datetime.now(timezone.utc).timestamp()
    )
    await asyncio.sleep(1)

    # 4) MeterValues (mode'a göre)
    if mode.upper() == "ATTACK" and get_manipulated_data:
        await send_attack_meter_values(get_manipulated_data)
    else:
        await send_normal_meter_values()

    # 5) StopTransaction (Zorunlu)
    emit_event(
        senaryo=SCENARIO_NAME,
        cp_id=CP_ID,
        message_type="StopTransaction",
        transaction_id=TX_ID,
        id_tag=ID_TAG,
        session_active=False,
        source="CP",
        cp_timestamp=datetime.now(timezone.utc).timestamp()
    )
    await asyncio.sleep(0.5)

    # 6) StatusNotification zinciri (Zorunlu — dashboard için)
    emit_event(
        senaryo=SCENARIO_NAME,
        cp_id=CP_ID,
        message_type="StatusNotification",
        status="Charging",
        source="CP",
        cp_timestamp=datetime.now(timezone.utc).timestamp()
    )
    await asyncio.sleep(0.2)

    emit_event(
        senaryo=SCENARIO_NAME,
        cp_id=CP_ID,
        message_type="StatusNotification",
        status="Finishing",
        source="CP",
        cp_timestamp=datetime.now(timezone.utc).timestamp()
    )
    await asyncio.sleep(0.2)

    emit_event(
        senaryo=SCENARIO_NAME,
        cp_id=CP_ID,
        message_type="StatusNotification",
        status="Available",
        source="CP",
        cp_timestamp=datetime.now(timezone.utc).timestamp()
    )

    print(f"[{CP_ID}] ✅ Senaryo Akışı Tamamlandı.")
