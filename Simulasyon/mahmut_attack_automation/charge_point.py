# Geliştirme Yönergesi: ocpp.v16 kütüphanesi kullanılmalı [cite: 100, 108]
from ocpp.v16 import ChargePoint as Cp
from ocpp.v16 import call as call_module
from ocpp.v16.enums import ChargePointStatus
import time

# OCPP isteği (request) sınıflarını çözmek için gerekli yardımcı fonksiyon [cite: 111]
def _resolve_req(name):
    cls = getattr(call_module, f"{name}Payload", None)
    if cls is not None:
        return cls
    cls = getattr(call_module, name, None)
    if cls is not None:
        return cls
    raise ImportError(f"{name} için uygun OCPP sınıfı bulunamadı.")

# Gerekli OCPP istek sınıflarının tanımlanması [cite: 119-122]
BootNotificationReq = _resolve_req("BootNotification")
StartTransactionReq = _resolve_req("StartTransaction")
StatusNotificationReq = _resolve_req("StatusNotification")
MeterValuesReq = _resolve_req("MeterValues")
StopTransactionReq = _resolve_req("StopTransaction")

class SimulatedChargePoint(Cp):
    def __init__(self, charge_point_id, connection):
        super().__init__(charge_point_id, connection)
        self.connector_id = 1 [cite: 124]
        self.current_status = ChargePointStatus.available [cite: 125]
        self.session_active = False [cite: 126]
        self.transaction_id = None [cite: 127]
        self.meter_value = 0.0 # kWh veya Wh gibi düşünebilirsin [cite: 128]

    async def send_boot_notification(self):
        req = BootNotificationReq(
            charge_point_model="CP-V1", [cite: 132]
            charge_point_vendor="TeamX", [cite: 133]
        )
        await self.call(req) [cite: 134]

    async def send_status_notification(self, status: ChargePointStatus):
        req = StatusNotificationReq(
            connector_id=self.connector_id, [cite: 137]
            error_code="NoError", [cite: 138]
            status=status, [cite: 139]
        )
        await self.call(req) [cite: 141]
        self.current_status = status [cite: 142]

    async def start_charging(self):
        if self.session_active:
            return
        self.transaction_id = int(time.time()) [cite: 147]
        req = StartTransactionReq(
            connector_id=self.connector_id, [cite: 149]
            id_tag="ID_USER1", [cite: 150]
            meter_start=int(self.meter_value * 100), [cite: 151]
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S") + "Z", [cite: 152]
        )
        await self.call(req) [cite: 154]
        self.session_active = True [cite: 155]
        await self.send_status_notification(ChargePointStatus.charging) [cite: 156]
    
    # --- ENERJİ MANİPÜLASYON KODLARI BURADA BAŞLAR ---

    async def simulate_meter_values_normal(self, step_kwh: float = 0.1):
        """ Normal akış: Raporlanan değer = Gerçek değer. """
        if self.session_active and self.current_status == ChargePointStatus.charging:
            self.meter_value += step_kwh
            
            req = MeterValuesReq(
                connector_id=self.connector_id, [cite: 161]
                meter_value=[{
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S") + "Z", [cite: 163]
                    "sampledValue": [{
                        "value": str(self.meter_value), [cite: 166]
                        "unit": "Wh", [cite: 167]
                    }],
                }],
            )
            await self.call(req) [cite: 170]

    async def simulate_meter_values_attack(self, real_step_kwh: float = 0.5, reported_step_kwh: float = 0.1):
        """ Saldırı akışı: Raporlanan değer (reported_step_kwh) < Gerçek değer (real_step_kwh). """
        if self.session_active and self.current_status == ChargePointStatus.charging:
            
            # İç sayaçta sadece manipüle edilmiş düşük artışı tutuyoruz.
            # Böylece StopTransaction'a düşük 'meter_stop' değeri gidecektir.
            self.meter_value += reported_step_kwh 
            
            req = MeterValuesReq(
                connector_id=self.connector_id,
                meter_value=[{
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S") + "Z",
                    "sampledValue": [{
                        "value": str(self.meter_value), # MANİPÜLE EDİLMİŞ DÜŞÜK DEĞERİ RAPORLA
                        "unit": "Wh",
                    }],
                }],
            )
            await self.call(req)
    
    async def stop_charging(self):
        if not self.session_active:
            return
        
        req = StopTransactionReq(
            transaction_id=self.transaction_id, [cite: 175]
            meter_stop=int(self.meter_value * 100), [cite: 176]
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S") + "Z", [cite: 177]
        )
        await self.call(req) [cite: 178]
        self.session_active = False [cite: 179]
        await self.send_status_notification(ChargePointStatus.finishing) [cite: 180]
        await self.send_status_notification(ChargePointStatus.available) [cite: 181]
