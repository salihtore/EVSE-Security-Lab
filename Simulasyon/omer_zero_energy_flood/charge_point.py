import time
import asyncio
from ocpp.v16 import ChargePoint as Cp
from ocpp.v16 import call as call_module
from ocpp.v16.enums import ChargePointStatus, RegistrationStatus

# --- YÖNERGE MADDE 4: Request Çözümleyici ---
def _resolve_req(name):
    cls = getattr(call_module, f"{name}Payload", None)
    if cls is not None:
        return cls
    cls = getattr(call_module, name, None)
    if cls is not None:
        return cls
    raise ImportError(f"{name} için uygun OCPP sınıfı bulunamadı.")

# Gerekli Payload Sınıfları
BootNotificationReq = _resolve_req("BootNotification")
StartTransactionReq = _resolve_req("StartTransaction")
StatusNotificationReq = _resolve_req("StatusNotification")
MeterValuesReq = _resolve_req("MeterValues")
StopTransactionReq = _resolve_req("StopTransaction")
AuthorizeReq = _resolve_req("Authorize")

class SimulatedChargePoint(Cp):
    def __init__(self, charge_point_id, connection):
        super().__init__(charge_point_id, connection)
        self.connector_id = 1
        self.current_status = ChargePointStatus.available
        self.session_active = False
        self.transaction_id = None
        self.meter_value = 0.0 

    async def send_boot_notification(self):
        req = BootNotificationReq(
            charge_point_model="CP-ZeroFlood",
            charge_point_vendor="OmerSecurity",
        )
        resp = await self.call(req)
        return resp

    async def send_status_notification(self, status: ChargePointStatus):
        req = StatusNotificationReq(
            connector_id=self.connector_id,
            error_code="NoError",
            status=status,
        )
        await self.call(req)
        self.current_status = status

    async def authorize_id(self, id_tag):
        req = AuthorizeReq(id_tag=id_tag)
        return await self.call(req)

    async def start_charging(self, id_tag="TAG_NORMAL", meter_start=None):
        """
        meter_start parametresi verilirse onu kullanır, yoksa self.meter_value kullanır.
        Saldırı modunda 0 gönderebilmek için esnek yapıldı.
        """
        if self.session_active:
            return

        # Eğer dışarıdan bir sayaç değeri gelmediyse mevcut değeri kullan
        current_meter = meter_start if meter_start is not None else int(self.meter_value * 1000)

        req = StartTransactionReq(
            connector_id=self.connector_id,
            id_tag=id_tag,
            meter_start=current_meter,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S") + "Z",
        )
        resp = await self.call(req)
        self.transaction_id = resp.transaction_id
        self.session_active = True
        await self.send_status_notification(ChargePointStatus.charging)
        return self.transaction_id

    async def simulate_meter_values(self, step_kwh: float = 0.1, force_value: float = None):
        """
        force_value: Saldırı için zorla belirli bir değer (örn: 0) göndermek için.
        """
        if self.session_active and self.current_status == ChargePointStatus.charging:
            
            # Eğer force_value varsa onu kullan (Saldırı), yoksa artır (Normal)
            if force_value is not None:
                display_value = force_value
                # self.meter_value'yu artırmıyoruz çünkü saldırıda enerji akmıyor
            else:
                self.meter_value += step_kwh
                display_value = self.meter_value

            req = MeterValuesReq(
                connector_id=self.connector_id,
                transaction_id=self.transaction_id,
                meter_value=[{
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S") + "Z",
                    "sampledValue": [{
                        "value": str(display_value), # Wh cinsinden değil, doğrudan float string
                        "unit": "Wh",
                        "context": "Sample.Periodic"
                    }],
                }],
            )
            await self.call(req)

    async def stop_charging(self, reason="Local"):
        if not self.session_active:
            return
        
        req = StopTransactionReq(
            transaction_id=self.transaction_id,
            meter_stop=int(self.meter_value * 1000), # Wh çevrimi
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S") + "Z",
            reason=reason
        )
        await self.call(req)
        self.session_active = False
        await self.send_status_notification(ChargePointStatus.finishing)
        await self.send_status_notification(ChargePointStatus.available)
