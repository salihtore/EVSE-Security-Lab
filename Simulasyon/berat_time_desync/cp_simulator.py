# Dosya: Simulasyon/berat_time_desync/cp_simulator.py
import asyncio
import time
import random

# Core sistem fonksiyonları
from core.core_cp import send_message_to_core


async def send_start_transaction(cp_id: str, mode: str):
    """
    StartTransaction oluşturur ve core'a yollar.
    - NORMAL mod: random transactionId → AUTH_BYPASS tetiklemez
    - ATTACK mod: sabit 999 → anomali için
    """

    if mode.upper() == "NORMAL":
        transaction_id = random.randint(1000, 9999)
    else:
        transaction_id = 999

    payload = {
        "timestamp": time.time(),
        "senaryo": "TimeDesync",
        "cp_id": cp_id,
        "message_type": "StartTransaction",
        "transactionId": transaction_id,    # ✔ doğru anahtar
        "idTag": "TEST123",                 # ✔ SWE korelasyon için gerekli
        "source": "CP"
    }

    await send_message_to_core(payload)
    return transaction_id


async def send_meter_values(cp_id: str, count: int, mode: str, get_manipulated_data=None):
    """
    MeterValues gönderir.
    NORMAL mod: sabit 50.0 kWh
    ATTACK mod: manipüle edilmiş payload
    """

    for i in range(count):
        await asyncio.sleep(1)

        if mode.upper() == "ATTACK" and get_manipulated_data:
            payload = get_manipulated_data(cp_id)
            print(f"[CP_{cp_id}] 💣 Anomali MeterValues gönderildi ({i+1}/{count}).")
        else:
            payload = {
                "timestamp": time.time(),
                "senaryo": "TimeDesync",
                "cp_id": cp_id,
                "message_type": "MeterValues",   # ✔ core formatı
                "meter_kWh": 50.0,               # ✔ core'da beklenen alan
                "source": "CP"
            }
            print(f"[CP_{cp_id}] 🟢 Normal MeterValues gönderildi ({i+1}/{count}).")

        await send_message_to_core(payload)


async def cp_event_flow(mode="NORMAL", get_manipulated_data=None):
    """
    CP Akışı:
    1) StartTransaction
    2) 3 adet MeterValues
    """

    cp_id = "CP_BERAT"

    print(f"\n[CP_{cp_id}] 📡 StartTransaction gönderiliyor...")
    transaction_id = await send_start_transaction(cp_id, mode)

    await send_meter_values(cp_id, 3, mode, get_manipulated_data)

    print(f"[CP_{cp_id}] ✅ Senaryo Akışı Tamamlandı.")
