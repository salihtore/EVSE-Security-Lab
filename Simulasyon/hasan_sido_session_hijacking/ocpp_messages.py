"""
OCPP 1.6 Mesaj Tanımlamaları
Bu modül OCPP protokolü mesajlarını oluşturur.
"""

import json
from datetime import datetime
from typing import Dict, Any, List
import uuid


class OCPPMessage:
    """OCPP mesajları için temel sınıf"""
    
    @staticmethod
    def create_message(message_type: str, unique_id: str = None, **kwargs) -> Dict[str, Any]:
        """Genel OCPP mesajı oluşturur"""
        if unique_id is None:
            unique_id = str(uuid.uuid4())
        
        return {
            "messageType": message_type,
            "uniqueId": unique_id,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        }


class StartTransaction:
    """StartTransaction mesajları"""
    
    @staticmethod
    def create(connector_id: int, id_tag: str, meter_start: int, timestamp: str = None) -> Dict[str, Any]:
        """Şarj oturumu başlatma mesajı"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        return OCPPMessage.create_message(
            message_type="StartTransaction",
            connectorId=connector_id,
            idTag=id_tag,
            meterStart=meter_start,
            timestamp=timestamp
        )
    
    @staticmethod
    def create_response(transaction_id: int, id_tag_info: Dict[str, str] = None) -> Dict[str, Any]:
        """StartTransaction yanıtı"""
        if id_tag_info is None:
            id_tag_info = {"status": "Accepted"}
        
        return {
            "transactionId": transaction_id,
            "idTagInfo": id_tag_info
        }


class MeterValues:
    """MeterValues mesajları"""
    
    @staticmethod
    def create(connector_id: int, transaction_id: int, meter_value: int, 
               timestamp: str = None, sampled_value_unit: str = "Wh") -> Dict[str, Any]:
        """Ölçüm değerleri mesajı"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        return OCPPMessage.create_message(
            message_type="MeterValues",
            connectorId=connector_id,
            transactionId=transaction_id,
            meterValue=[{
                "timestamp": timestamp,
                "sampledValue": [{
                    "value": str(meter_value),
                    "unit": sampled_value_unit,
                    "measurand": "Energy.Active.Import.Register"
                }]
            }]
        )


class StopTransaction:
    """StopTransaction mesajları"""
    
    @staticmethod
    def create(transaction_id: int, id_tag: str, meter_stop: int, 
               timestamp: str = None, reason: str = "Local") -> Dict[str, Any]:
        """Şarj oturumu durdurma mesajı"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        return OCPPMessage.create_message(
            message_type="StopTransaction",
            transactionId=transaction_id,
            idTag=id_tag,
            meterStop=meter_stop,
            timestamp=timestamp,
            reason=reason
        )
    
    @staticmethod
    def create_response(id_tag_info: Dict[str, str] = None) -> Dict[str, Any]:
        """StopTransaction yanıtı"""
        if id_tag_info is None:
            id_tag_info = {"status": "Accepted"}
        
        return {
            "idTagInfo": id_tag_info
        }


class RemoteStopTransaction:
    """RemoteStopTransaction mesajları"""
    
    @staticmethod
    def create(transaction_id: int) -> Dict[str, Any]:
        """Uzaktan oturum durdurma mesajı"""
        return OCPPMessage.create_message(
            message_type="RemoteStopTransaction",
            transactionId=transaction_id
        )


class Authorize:
    """Authorize mesajları"""
    
    @staticmethod
    def create(id_tag: str) -> Dict[str, Any]:
        """Yetkilendirme mesajı"""
        return OCPPMessage.create_message(
            message_type="Authorize",
            idTag=id_tag
        )
    
    @staticmethod
    def create_response(status: str = "Accepted") -> Dict[str, Any]:
        """Authorize yanıtı"""
        return {
            "idTagInfo": {"status": status}
        }


class Heartbeat:
    """Heartbeat mesajları"""
    
    @staticmethod
    def create() -> Dict[str, Any]:
        """Kalp atışı mesajı"""
        return OCPPMessage.create_message(
            message_type="Heartbeat"
        )
    
    @staticmethod
    def create_response() -> Dict[str, Any]:
        """Heartbeat yanıtı"""
        return {
            "currentTime": datetime.now().isoformat()
        }


class BootNotification:
    """BootNotification mesajları"""
    
    @staticmethod
    def create(charge_point_vendor: str, charge_point_model: str) -> Dict[str, Any]:
        """Başlatma bildirim mesajı"""
        return OCPPMessage.create_message(
            message_type="BootNotification",
            chargePointVendor=charge_point_vendor,
            chargePointModel=charge_point_model
        )
    
    @staticmethod
    def create_response(status: str = "Accepted", interval: int = 300) -> Dict[str, Any]:
        """BootNotification yanıtı"""
        return {
            "status": status,
            "currentTime": datetime.now().isoformat(),
            "interval": interval
        }
