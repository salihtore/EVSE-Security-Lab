# Simulasyon/berat_time_desync/scenario.py

import asyncio
import time
import logging

from Simulasyon.core.event_bus import emit_event

logging.basicConfig(level=logging.INFO)

CP_ID = "CP_BERAT"


async def run_normal():
    """
    Normal durumda CP ve CSMS saatleri senkron:
    cp_timestamp ≈ csms_time → ALARM BEKLENMEZ.
    """
    logging.info("\n--- TIME DESYNC NORMAL SENARYO ---")

    for i in range(5):
        csms_ts = time.time()            # CSMS'in gerçek saati
        cp_ts = csms_ts                  # CP saati doğru

        emit_event(
            senaryo="TimeDesync",
            cp_id=CP_ID,
            message_type="MeterValues",
            cp_timestamp=cp_ts,
            csms_time=csms_ts,
            source="CP"
        )

        logging.info(f"[NORMAL] cp_ts={cp_ts}, csms_ts={csms_ts}")
        await asyncio.sleep(1)


async def run_attack(offset_hours: float = 2.0):
    """
    Saldırı: CP'nin saati kaydırılıyor (ör: +2 saat).
    cp_timestamp ile csms_time arasındaki fark > 300 saniye → TIME_DESYNC ALARMI.
    """
    logging.warning("\n--- TIME DESYNC SALDIRI SENARYOSU (CP SAATİ KAYMIŞ) ---")

    offset_sec = offset_hours * 3600

    for i in range(5):
        csms_ts = time.time()               # CSMS'in gerçek saati
        cp_ts = csms_ts + offset_sec        # CP'nin bozulan saati

        emit_event(
            senaryo="TimeDesync",
            cp_id=CP_ID,
            message_type="MeterValues",
            cp_timestamp=cp_ts,
            csms_time=csms_ts,
            source="CP_ATTACKER"
        )

        logging.info(
            f"[ATTACK] cp_ts={cp_ts}, csms_ts={csms_ts}, diff={cp_ts - csms_ts:.1f} s"
        )
        await asyncio.sleep(1)


def run_scenario(scenario: str = "attack"):
    """
    Dışarıdan şu şekilde çağrılacak:
      - run_scenario("normal")
      - run_scenario("attack")
    """
    if scenario == "normal":
        asyncio.run(run_normal())
    else:
        asyncio.run(run_attack())
