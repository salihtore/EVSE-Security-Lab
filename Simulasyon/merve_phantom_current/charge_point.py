
import time
import asyncio
from ocpp.v16 import ChargePoint as Cp
from ocpp.v16 import call
from ocpp.v16.enums import ChargePointStatus

class SimulatedChargePoint(Cp):
    def __init__(self, charge_point_id, connection):
        super().__init__(charge_point_id, connection)
        self.connector_id = 1
        self.session_active = False
        self.transaction_id = None
        self.meter_value = 0.0

    async def send_boot_notification(self):
        # DÜZELTME: 'BootNotificationPayload' yerine 'BootNotification'
        req = call.BootNotification(
            charge_point_model="CP-HAYALET",
            charge_point_vendor="Grup1"
        )
        await self.call(req)

    async def send_status_notification(self, status):
        # DÜZELTME: Payload eki kaldırıldı
        req = call.StatusNotification(
            connector_id=self.connector_id,
            error_code="NoError",
            status=status
        )
        await self.call(req)

    async def start_charging(self):
        self.transaction_id = int(time.time())
        # DÜZELTME: Payload eki kaldırıldı
        req = call.StartTransaction(
            connector_id=self.connector_id,
            id_tag="USER1",
            meter_start=int(self.meter_value * 1000),
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S") + "Z"
        )
        await self.call(req)
        self.session_active = True
        await self.send_status_notification(ChargePointStatus.charging)

    async def simulate_meter_values(self, step_kwh=0.1, phantom_mode=False):
        if self.session_active or phantom_mode:
            self.meter_value += step_kwh
            if phantom_mode:
                print(f"[SALDIRGAN] !!! HAYALET VERİ GÖNDERİLİYOR !!! Sayaç: {self.meter_value:.2f}")
            else:
                print(f"[NORMAL] Normal Şarj: {self.meter_value:.2f}")

            # DÜZELTME: Payload eki kaldırıldı
            req = call.MeterValues(
                connector_id=self.connector_id,
                transaction_id=self.transaction_id,
                meter_value=[{
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S") + "Z",
                    "sampledValue": [{"value": str(self.meter_value), "unit": "kWh"}]
                }]
            )
            await self.call(req)

    async def stop_charging(self):
        print("[SİSTEM] Şarj Durduruluyor (StopTransaction)...")
        # DÜZELTME: Payload eki kaldırıldı
        req = call.StopTransaction(
            transaction_id=self.transaction_id,
            meter_stop=int(self.meter_value * 1000),
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S") + "Z"
        )
        await self.call(req)
        self.session_active = False
        await self.send_status_notification(ChargePointStatus.available)
