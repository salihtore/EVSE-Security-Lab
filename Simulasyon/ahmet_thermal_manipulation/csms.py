import asyncio
import logging
import websockets
from datetime import datetime
from ocpp.routing import on
from ocpp.v16 import ChargePoint as Cp
from ocpp.v16.enums import Action, RegistrationStatus
from ocpp.v16 import call_result

logging.basicConfig(level=logging.INFO)

class ChargePoint(Cp):
    # Action isimleri kucuk harf (snake_case) olmalidir
    @on(Action.boot_notification)
    def on_boot_notification(self, charge_point_vendor, charge_point_model, **kwargs):
        logging.info(f"BootNotification: {charge_point_vendor} - {charge_point_model}")
        # DÜZELTME: BootNotificationPayload -> BootNotification
        return call_result.BootNotification(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status=RegistrationStatus.accepted
        )

    @on(Action.status_notification)
    def on_status_notification(self, connector_id, error_code, status, **kwargs):
        logging.info(f"Status: {status}")
        return call_result.StatusNotification()

    @on(Action.authorize)
    def on_authorize(self, id_tag, **kwargs):
        logging.info(f"Auth: {id_tag}")
        return call_result.Authorize(
            id_tag_info={"status": "Accepted"}
        )

    @on(Action.start_transaction)
    def on_start_transaction(self, connector_id, id_tag, meter_start, timestamp, **kwargs):
        logging.info(f"StartTx: {id_tag}")
        return call_result.StartTransaction(
            transaction_id=1,
            id_tag_info={"status": "Accepted"}
        )

    @on(Action.meter_values)
    def on_meter_values(self, connector_id, meter_value, transaction_id, **kwargs):
        logging.info(f"MeterValues alındı (Tx: {transaction_id})")
        return call_result.MeterValues()

    @on(Action.stop_transaction)
    def on_stop_transaction(self, meter_stop, timestamp, transaction_id, **kwargs):
        logging.info(f"StopTx: {meter_stop}")
        return call_result.StopTransaction(
            id_tag_info={"status": "Accepted"}
        )

async def on_connect(websocket):
    try:
        requested_protocols = websocket.request_headers.get('Sec-WebSocket-Protocol')
        logging.info(f"Baglanti istegi protokol: {requested_protocols}")
    except:
        pass
        
    logging.info("Yeni istasyon bağlandı.")
    cp = ChargePoint("CP_GENERIC", websocket)
    await cp.start()

async def main():
    # websockets.serve parametreleri guncel kutuphaneye gore duzenlendi
    async with websockets.serve(on_connect, '0.0.0.0', 9000, subprotocols=['ocpp1.6']):
        logging.info("CSMS Sunucusu Calisiyor (Port: 9000)...")
        await asyncio.Future()  # Sonsuz dongu

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass