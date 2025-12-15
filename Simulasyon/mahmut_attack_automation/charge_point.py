# Geliştirme Yönergesi: ocpp.v16 kütüphanesi kullanılmalı
from ocpp.v16 import ChargePoint as Cp
from ocpp.v16 import call as call_module
from ocpp.v16.enums import ChargePointStatus
import time
import asyncio

# OCPP isteği (request) sınıflarını çözmek için yardımcı fonksiyon
def _resolve_req(name):
    # Hem Xyz hem XyzPayload ismini deneyerek çöz.
    cls = getattr(call_module, f"{name}Payload", None)
    if cls is not None:
        return cls
    cls = getattr(call_module, name, None)
    if cls is not None:
        return cls
    raise ImportError(f"{name} için uygun OCPP sınıfı bulunamadı.")

# [cite_start]Gerekli OCPP istek sınıflarının tanımlanması [cite: 119-122]
BootNotificationReq = _resolve_req("BootNotification")
StartTransactionReq = _resolve_req("StartTransaction")
StatusNotificationReq = _resolve_req("StatusNotification")
MeterValuesReq = _resolve_req("MeterValues")
StopTransactionReq = _resolve_req("StopTransaction")

class SimulatedChargePoint(Cp):
    def __init__(self, charge_point_id, connection):
        super().__init__(charge_point_id, connection)
        self.connector_id = 1
        self.current_status = ChargePointStatus.available
        self.session_active = False
        self.transaction_id = None
        self.meter_value = 0.0 # kWh gibi düşünebilirsin

    async def send_boot_notification(self):
        # Hata düzeltmesi: BootNotificationReq çağrısı doğru parantez kullanımıyla yapıldı.
        req = BootNotificationReq(
            charge_point_model="CP-V1",
            charge_point_vendor="TeamX",
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

    async def start_charging(self):
        if self.session_active:
            return
        self.transaction_id = int(time.time())
        
        # StartTransactionReq çağrısı doğru yapıldı.
        req = StartTransactionReq(
            connector_id=self.connector_id,
            id_tag="ID_USER1",
            meter_start=int(self.meter_value * 100),
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S") + "Z",
        )
        await self.call(req)
        self.session_active = True
        await self.send_status_notification(ChargePointStatus.charging)
    
    # --- ENERJİ MANİPÜLASYON KODLARI BURADA BAŞLAR ---

    async def simulate_meter_values_normal(self, step_kwh: float = 0.1):
        """ Normal akış: Raporlanan değer = Gerçek değer. """
        if self.session_active and self.current_status == ChargePointStatus.charging:
            self.meter_value += step_kwh
            
            # MeterValuesReq çağrısı doğru yapıldı.
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

    async def simulate_meter_values_attack(self, real_step_kwh: float = 0.5, reported_step_kwh: float = 0.1):
        """ Saldırı akışı: Raporlanan değer (reported_step_kwh) < Gerçek değer (real_step_kwh). """
        if self.session_active and self.current_status == ChargePointStatus.charging:
            
            # İç sayaçta sadece manipüle edilmiş düşük artışı tutuyoruz.
            self.meter_value += reported_step_kwh 
            
            # MeterValuesReq çağrısı doğru yapıldı.
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
        
        # StopTransactionReq çağrısı doğru yapıldı.
        req = StopTransactionReq(
            transaction_id=self.transaction_id,
            meter_stop=int(self.meter_value * 100),
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S") + "Z",
        )
        await self.call(req)
        self.session_active = False
        await self.send_status_notification(ChargePointStatus.finishing)
        await self.send_status_notification(ChargePointStatus.available)
