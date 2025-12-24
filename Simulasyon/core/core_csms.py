import asyncio
import logging
import websockets
from src.core.anomaly_engine import AnomalyEngine
import time


from ocpp.routing import on
from ocpp.v16 import ChargePoint as Cp
from ocpp.v16.enums import Action, RegistrationStatus
from ocpp.v16 import call_result as result

from .event_bus import emit_event

logging.basicConfig(level=logging.INFO)

class CoreCSMS(Cp):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.anomaly_engine = AnomalyEngine()

    @on(Action.boot_notification)
    async def on_boot(self, charge_point_model, charge_point_vendor, **kwargs):
        logging.info(f"[CSMS] BootNotification → {charge_point_model} / {charge_point_vendor}")

        emit_event(
            cp_id=self.id,
            message_type="BootNotification",
            charge_point_model=charge_point_model,
            charge_point_vendor=charge_point_vendor,
            source="CP"
        )

        # ❗ Burada en uyumlu sınıf → BootNotification
        return result.BootNotification(
            current_time="2025-01-01T00:00:00Z",
            interval=10,
            status=RegistrationStatus.accepted
        )

    @on(Action.status_notification)
    async def on_status(self, connector_id, status, **kwargs):
        logging.info(f"[CSMS] StatusNotification → CP={self.id}, {status}")

        emit_event(
            cp_id=self.id,
            message_type="StatusNotification",
            status=status,
            connector_id=connector_id,
            source="CP"
        )

        return result.StatusNotification()

    @on(Action.start_transaction)
    async def on_start(self, connector_id, id_tag, meter_start, timestamp, **kwargs):
        logging.info(f"[CSMS] StartTransaction → CP={self.id}, idTag={id_tag}")

        emit_event(
            cp_id=self.id,
            message_type="StartTransaction",
            idTag=id_tag,
            session_active=True,
            source="CP"
        )
        event = {
            "cp_id": self.id,
            "message_type": "StartTransaction",
            "idTag": id_tag,
            "timestamp": time.time(),
        }

        self.anomaly_engine.process(event)


        return result.StartTransaction(
            transaction_id=123,
            id_tag_info={"status": "Accepted"}
        )

    @on(Action.stop_transaction)
    async def on_stop(self, transaction_id, meter_stop, timestamp, **kwargs):
        logging.info(f"[CSMS] StopTransaction → CP={self.id}")

        emit_event(
            cp_id=self.id,
            message_type="StopTransaction",
            session_active=False,
            source="CP"
        )

        return result.StopTransaction()

    @on(Action.meter_values)
    async def on_meter(self, connector_id, meter_value, **kwargs):
        try:
            kwh = float(meter_value[0]["sampledValue"][0]["value"])
        except:
            kwh = 0.0

        logging.info(f"[CSMS] MeterValues → CP={self.id}, kWh={kwh}")

        emit_event(
            cp_id=self.id,
            message_type="MeterValues",
            meter_kWh=kwh,
            source="CP"
        )

        return result.MeterValues()
    
    @on(Action.authorize)
    async def on_authorize(self, id_tag, **kwargs):
        logging.info(f"[CSMS] Authorize → CP={self.id}, idTag={id_tag}")

        event = {
            "cp_id": self.id,
            "message_type": "Authorize",
            "idTag": id_tag,
            "timestamp": time.time(),
        }

        self.anomaly_engine.process(event)

        return result.Authorize(id_tag_info={"status": "Accepted"})



async def on_connect(connection):
    try:
        path = getattr(connection, "path", None) or connection.request.path

    except:
        path = "/unknown"

    cp_id = path.strip("/") or "unknown"
    logging.info(f"[CSMS] Yeni CP bağlantısı → {cp_id}")

    cp = CoreCSMS(cp_id, connection)
    await cp.start()


async def main():
    logging.info("[CSMS] Server başlıyor → ws://0.0.0.0:9000")

    server = await websockets.serve(
        on_connect,
        "0.0.0.0",
        9000,
        subprotocols=["ocpp1.6"]
    )

    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
