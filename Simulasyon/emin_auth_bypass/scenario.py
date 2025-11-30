# Simulasyon/emin_auth_bypass/scenario.py

import asyncio
import websockets
import logging

from Simulasyon.core.event_bus import emit_event

logging.basicConfig(level=logging.INFO)

CSMS_URI = "ws://127.0.0.1:9002/CP_EMIN"


async def run_normal():
    """
    Normal akış: Authorize -> Accepted -> StartTransaction
    Bu akışta alarm BEKLENMEZ.
    """
    async with websockets.connect(CSMS_URI, subprotocols=["ocpp1.6"]) as ws:
        
        # 1) AUTH
        emit_event(
            senaryo="AuthBypass",
            cp_id="CP_EMIN",
            message_type="Authorize",
            idTag="VALID123",
            source="CP"
        )
        await asyncio.sleep(1)

        # 2) Accept geldi varsayıyoruz (normal akış)
        emit_event(
            senaryo="AuthBypass",
            cp_id="CP_EMIN",
            message_type="Authorize.conf",
            idTag="VALID123",
            auth_status="Accepted",
            source="CSMS"
        )
        await asyncio.sleep(1)

        # 3) StartTransaction (normal)
        emit_event(
            senaryo="AuthBypass",
            cp_id="CP_EMIN",
            message_type="StartTransaction",
            idTag="VALID123",
            transactionId=111,
            session_active=True,
            source="CP"
        )

        await asyncio.sleep(2)


async def run_attack():
    """
    Saldırı akışı: AUTH YOK, DOĞRUDAN StartTransaction geliyor.
    Ana motor bunu AUTH_BYPASS olarak yakalayacak.
    """
    async with websockets.connect(CSMS_URI, subprotocols=["ocpp1.6"]) as ws:

        # Hiç AUTHORIZE yollamadan direk StartTransaction
        emit_event(
            senaryo="AuthBypass",
            cp_id="CP_EMIN",
            message_type="StartTransaction",
            idTag="HACKER123",
            transactionId=999,
            session_active=True,
            source="ATTACKER"
        )

        await asyncio.sleep(2)

        # Ek saldırı: sahte Accepted mesajını hacker gönderiyor
        emit_event(
            senaryo="AuthBypass",
            cp_id="CP_EMIN",
            message_type="Authorize.conf",
            idTag="HACKER123",
            auth_status="Accepted",
            source="ATTACKER"
        )

        await asyncio.sleep(2)

        # Normal Stop (mantık gereği)
        emit_event(
            senaryo="AuthBypass",
            cp_id="CP_EMIN",
            message_type="StopTransaction",
            session_active=False,
            transactionId=999,
            source="CP"
        )


def run_scenario(scenario="attack"):
    if scenario == "normal":
        asyncio.run(run_normal())
    else:
        asyncio.run(run_attack())
