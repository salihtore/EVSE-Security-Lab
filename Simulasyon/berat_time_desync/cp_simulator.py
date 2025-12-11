# Dosya: Simulasyon/berat_time_desync/cp_simulator.py
import asyncio
import time
import random

# Core sistem fonksiyonları
from core.core_cp import send_message_to_core


async def send_start_transaction(cp_id: str, mode: str):
    """
    StartTransaction mesajını oluşturur ve core'a gönderir.
    - NORMAL modda transaction_id random (alarm tetiklemez)
    - ATTACK modunda transaction_id = 999 (alarm tetikler)
    """

    if mode.upper() == "NORMAL":
        transaction_id = random.randint(1000, 9999)
    else:
        transaction_id = 999  # Attack modda sabit ID

    payload = {
        "timestamp": time.time(),
        "senaryo": "TimeDesync",
        "cp_id": cp_id,
        "message_type": "StartTransaction",
        "transaction_id": transaction_id,
        "source": "CP"
    }

    await send_message_to_core(payload)

    return transaction_id



async def send_meter_values(cp_id: str, count: int, mode: str, get_manipulated_data=None):
    """
    MeterValue gönderir.
    - NORMAL mod: normal değerler
    - ATTACK mod: get_manipulated_data kullanılır
    """
    for i in range(count):
        await asyncio.sleep(1)

        if mode.upper() == "ATTACK" and get_manipulated_data:
            payload = get_manipulated_data(cp_id)
            print(f"[CP_{cp_id}] 💣 Anomali MeterValue gönderildi ({i+1}/{count}).")
        else:
            payload = {
                "timestamp": time.time(),
                "senaryo": "TimeDesync",
                "cp_id": cp_id,
                "message_type": "MeterValue",
                "value": 50.0,
                "source": "CP"
            }
            print(f"[CP_{cp_id}] 🟢 Normal MeterValue gönderildi ({i+1}/{count}).")

        await send_message_to_core(payload)



async def cp_event_flow(mode="NORMAL", get_manipulated_data=None):
    """
    Tam CP akışı:
    1. StartTransaction
    2. 3 adet MeterValue
    3. (İsteğe bağlı) StopTransaction eklenebilir
    """
    cp_id = "CP_BERAT"

    print(f"\n[CP_{cp_id}] 📡 StartTransaction gönderiliyor...")
    transaction_id = await send_start_transaction(cp_id, mode)

    await send_meter_values(cp_id, 3, mode, get_manipulated_data)

    print(f"[CP_{cp_id}] ✅ Senaryo Akışı Tamamlandı.")


