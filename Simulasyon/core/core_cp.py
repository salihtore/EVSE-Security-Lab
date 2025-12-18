# Simulasyon/core/core_cp.py
from .event_bus import emit_event
import time

class CoreCP:
    def __init__(self, cp_id="CP1"):
        self.id = cp_id

    def boot(self):
        emit_event(
            cp_id=self.id,
            message_type="BootNotification",
            source="CP"
        )
        time.sleep(0.5)

    def authorize(self, idTag="TEST123"):
        emit_event(
            cp_id=self.id,
            message_type="Authorize",
            idTag=idTag,
            source="CP"
        )
        time.sleep(0.5)

    def start_transaction(self, tx_id=1, idTag="TEST123"):
        emit_event(
            cp_id=self.id,
            message_type="StartTransaction",
            transactionId=tx_id,
            idTag=idTag,
            session_active=True,
            source="CP"
        )
        time.sleep(0.5)

    def send_meter_values(self, kwh):
        emit_event(
            cp_id=self.id,
            message_type="MeterValues",
            meter_kWh=kwh,
            source="CP"
        )
        time.sleep(0.5)

    def stop_transaction(self, tx_id=1, idTag="TEST123"):
        emit_event(
            cp_id=self.id,
            message_type="StopTransaction",
            transactionId=tx_id,
            idTag=idTag,
            session_active=False,
            source="CP"
        )
        time.sleep(0.5)
