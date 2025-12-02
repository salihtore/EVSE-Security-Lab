# Simulasyon/merve_phantom_current/scenario.py

import asyncio
import websockets
import logging
from ocpp.v16.enums import ChargePointStatus

from Simulasyon.core.event_bus import emit_event
from .cp_attacker import AttackerChargePoint   # Merve'nin CP kodu
from .csms_server import run_csms              # Merve'nin CSMS kodu

logging.basicConfig(level=logging.INFO)

CSMS_URI = "ws://127.0.0.1:9001/CP_MERVE"

async def run_normal():
    """
    Phantom Current oluşmayan normal akış.
    """
    async with websockets.connect(CSMS_URI, subprotocols=["ocpp1.6"]) as ws:
        cp = AttackerChargePoint("CP_MERVE", ws)

        # Boot
        await cp.send_boot_notification()

        # Normal başlat
        await cp.start_charging()

        # Normal meter values (plug_state=True, session_active=True)
        for _ in range(3):
            cp.meter_value += 0.1
            emit_event(
                senaryo="PhantomCurrent",
                cp_id="CP_MERVE",
                message_type="MeterValues",
                meter_kWh=cp.meter_value,
                plug_state=True,
                session_active=True,
                source="CP"
            )
            await asyncio.sleep(1)

        # Normal stop
        await cp.stop_charging()

        emit_event(
            senaryo="PhantomCurrent",
            cp_id="CP_MERVE",
            message_type="StopTransaction",
            plug_state=False,
            session_active=False,
            source="CP"
        )


async def run_attack():
    """
    Asıl saldırı: seans kapalı iken kWh artması.
    """
    async with websockets.connect(CSMS_URI, subprotocols=["ocpp1.6"]) as ws:
        cp = AttackerChargePoint("CP_MERVE", ws)

        # Boot
        await cp.send_boot_notification()

        # Normal başlat + durdur (seans bitiyor)
        await cp.start_charging()
        await asyncio.sleep(2)
        await cp.stop_charging()

        # plug/state bilgilerini event olarak gönderelim:
        emit_event(
            senaryo="PhantomCurrent",
            cp_id="CP_MERVE",
            message_type="StopTransaction",
            plug_state=False,
            session_active=False,
            source="CP"
        )

        # 🔥 Saldırı: MeterValues aracılığıyla kWh artmaya devam ediyor
        logging.warning("\n--- PHANTOM CURRENT SALDIRISI BAŞLIYOR ---")
        cp.meter_value = 10.0   # sanki bir enerji mevcutmuş gibi

        for _ in range(5):
            cp.meter_value += 0.2   # seans kapalı ama değer artıyor!
            emit_event(
                senaryo="PhantomCurrent",
                cp_id="CP_MERVE",
                message_type="MeterValues",
                meter_kWh=cp.meter_value,
                plug_state=False,
                session_active=False,
                source="ATTACKER"
            )
            await asyncio.sleep(1)


def run_scenario(scenario="normal"):
    if scenario == "normal":
        asyncio.run(run_normal())
    else:
        asyncio.run(run_attack())
