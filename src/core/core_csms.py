import asyncio
import websockets
from ocpp.v16 import ChargePoint as Cp
from ocpp.v16 import call_result
from ocpp.v16.enums import Action
from ocpp.routing import on

from src.core.event_pipeline import EventPipeline
from src.core.anomaly_engine import AnomalyEngine
from src.utils.logger import logger
from src.api.services.cp_state import cp_state   # ✔ global CP state


event_pipeline = EventPipeline()
anomaly_engine = AnomalyEngine()


class CSMS(Cp):

    @on(Action.BootNotification)
    async def on_boot_notification(
        self,
        charge_point_model: str,
        charge_point_vendor: str,
        **kwargs
    ):
        cp_id = self.id

        payload = {
            "chargePointModel": charge_point_model,
            "chargePointVendor": charge_point_vendor,
        }

        event = event_pipeline.build_event(cp_id, "BootNotification", payload)
        event_pipeline.emit_event(event)
        anomaly_engine.process(event)

        logger.info(f"[CSMS] BootNotification → CP={cp_id}")

        return call_result.BootNotificationPayload(
            current_time="2025-01-01T00:00:00Z",
            interval=10,
            status="Accepted",
        )

    @on(Action.StartTransaction)
    async def on_start_transaction(self, **payload):
        cp_id = self.id

        event = event_pipeline.build_event(cp_id, "StartTransaction", payload)
        event_pipeline.emit_event(event)
        anomaly_engine.process(event)

        logger.info(f"[CSMS] StartTransaction → CP={cp_id}")

        return call_result.StartTransactionPayload(
            transaction_id=123,
            id_tag_info={"status": "Accepted"},
        )

    @on(Action.MeterValues)
    async def on_meter_values(self, **payload):
        cp_id = self.id

        event = event_pipeline.build_event(cp_id, "MeterValues", payload)
        event_pipeline.emit_event(event)
        anomaly_engine.process(event)

        return call_result.MeterValuesPayload()

    @on(Action.StopTransaction)
    async def on_stop_transaction(self, **payload):
        cp_id = self.id

        event = event_pipeline.build_event(cp_id, "StopTransaction", payload)
        event_pipeline.emit_event(event)
        anomaly_engine.process(event)

        logger.info(f"[CSMS] StopTransaction → CP={cp_id}")

        return call_result.StopTransactionPayload(
            id_tag_info={"status": "Accepted"},
        )

    # ---------------------------------------------------------
    # NEW: StatusNotification handler (CP durum güncelleme)
    # ---------------------------------------------------------
    @on(Action.StatusNotification)
    async def on_status_notification(
        self,
        connector_id: int,
        error_code: str,
        status: str,
        **kwargs
    ):
        cp_id = self.id

        payload = {
            "connectorId": connector_id,
            "errorCode": error_code,
            "status": status,
        }

        event = event_pipeline.build_event(cp_id, "StatusNotification", payload)
        event_pipeline.emit_event(event)
        anomaly_engine.process(event)

        # 🔥 CP durumu güncelle (dashboard buradan okuyor)
        cp_state.update(cp_id, status)

        logger.info(
            f"[CSMS] StatusNotification → CP={cp_id}, status={status}, error={error_code}"
        )

        return call_result.StatusNotificationPayload()


async def main():
    async def handler(connection, path):
        cp_id = path.lstrip("/") or "unknown"
        logger.info(f"[CSMS] Yeni CP bağlantısı → {cp_id}")

        cp = CSMS(cp_id, connection)
        await cp.start()

    server = await websockets.serve(
        handler,
        "0.0.0.0",
        9000,
        subprotocols=["ocpp1.6"],
    )

    logger.info("🔥 CSMS Başladı → ws://0.0.0.0:9000")
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
