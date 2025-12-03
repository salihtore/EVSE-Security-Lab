import time
from ocpp.v16 import ChargePoint as Cp
from ocpp.v16 import call as call_module
from ocpp.v16.enums import ChargePointStatus


def _resolve_req(name: str):
    cls = getattr(call_module, f"{name}Payload", None)
    if cls is not None:
        return cls
    cls = getattr(call_module, name, None)
    if cls is not None:
        return cls
    raise ImportError(f"{name} için uygun OCPP sınıfı bulunamadı.")


BootNotificationReq = _resolve_req("BootNotification")
AuthorizeReq = _resolve_req("Authorize")
StartTransactionReq = _resolve_req("StartTransaction")
StatusNotificationReq = _resolve_req("StatusNotification")
MeterValuesReq = _resolve_req("MeterValues")
StopTransactionReq = _resolve_req("StopTransaction")


class SimulatedChargePoint(Cp):
    """
    Authentication Bypass Senaryosu:

    NORMAL:
        Boot -> Authorize -> StartTx -> MeterValues -> StopTx

    ATTACK:
        Boot -> (Authorize YOK) -> StartTx -> MeterValues -> StopTx
    """

    def __init__(self, charge_point_id: str, connection):
        super().__init__(charge_point_id, connection)
        self.connector_id = 1
        self.current_status = ChargePointStatus.available
        self.session_active = False
        self.transaction_id = None
        self.meter_value = 0.0
        self.attack_mode = False

    async def send_boot_notification(self):
        req = BootNotificationReq(
            charge_point_model="CP-V1",
            charge_point_vendor="CHARGE-SHIELD-AI",
        )
        await self.call(req)

    async def send_status_notification(self, status: ChargePointStatus):
        req = StatusNotificationReq(
            connector_id=self.connector_id,
            error_code="NoError",
            status=status,
        )
        await self.call(req)
        self.current_status = status

    async def send_authorize(self):
        if self.attack_mode:
            print("❌ SALDIRI: Authorize isteği BİLEREK gönderilmiyor!")
            return

        req = AuthorizeReq(
            id_tag="ID_USER1",
        )
        await self.call(req)

    async def start_charging(self):
        if self.session_active:
            return

        self.transaction_id = int(time.time())

        # Normalde start öncesi AUTH gelir. Attack modunda atlanır.
        await self.send_authorize()

        req = StartTransactionReq(
            connector_id=self.connector_id,
            id_tag="ID_USER1",
            meter_start=int(self.meter_value * 100),
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S") + "Z",
        )
        await self.call(req)

        self.session_active = True
        await self.send_status_notification(ChargePointStatus.charging)

    async def simulate_meter_values(self, step_kwh: float = 0.1):
        if self.session_active:
            self.meter_value += step_kwh
            req = MeterValuesReq(
                connector_id=self.connector_id,
                meter_value=[{
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S") + "Z",
                    "sampledValue": [{
                        "value": str(self.meter_value),
                        "unit": "Wh",
                    }],
                }],
            )
            await self.call(req)

    async def stop_charging(self):
        if not self.session_active:
            return

        req = StopTransactionReq(
            transaction_id=self.transaction_id,
            meter_stop=int(self.meter_value * 100),
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S") + "Z",
        )
        await self.call(req)

        self.session_active = False
        await self.send_status_notification(ChargePointStatus.finishing)
        await self.send_status_notification(ChargePointStatus.available)
