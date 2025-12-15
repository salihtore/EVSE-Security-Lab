"""
Anomali Tespit Sistemi
Session Hijacking ve diğer anomalileri tespit eder
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import json


class AlertLevel:
    """Alarm seviyeleri"""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertType:
    """Alarm tipleri"""
    SESSION_HIJACK = "SESSION_HIJACK"
    ID_TAG_MISMATCH = "ID_TAG_MISMATCH"
    IP_CHANGE = "IP_CHANGE"
    CONNECTOR_MISMATCH = "CONNECTOR_MISMATCH"
    REPLAY_ATTACK = "REPLAY_ATTACK"
    ABNORMAL_METER_VALUE = "ABNORMAL_METER_VALUE"
    SUSPICIOUS_SEQUENCE = "SUSPICIOUS_SEQUENCE"
    RAPID_TRANSACTION = "RAPID_TRANSACTION"


@dataclass
class Alert:
    """Alarm veri modeli"""
    alert_id: str
    alert_type: str
    level: str
    timestamp: datetime
    transaction_id: Optional[int] = None
    id_tag: Optional[str] = None
    description: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    mitigated: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "alert_type": self.alert_type,
            "level": self.level,
            "timestamp": self.timestamp.isoformat(),
            "transaction_id": self.transaction_id,
            "id_tag": self.id_tag,
            "description": self.description,
            "details": self.details,
            "mitigated": self.mitigated
        }


class AnomalyDetector:
    """Anomali tespit sistemi"""
    
    def __init__(self):
        self.alerts: List[Alert] = []
        self.message_history: List[Dict] = []
        self.session_profiles: Dict[str, Dict] = {}  # id_tag -> profile
        self.ip_tracking: Dict[int, str] = {}  # transaction_id -> ip
        self.connector_tracking: Dict[int, int] = {}  # transaction_id -> connector_id
        self.message_hashes: Dict[str, List[datetime]] = defaultdict(list)  # hash -> timestamps
        self.transaction_start_times: Dict[int, datetime] = {}
        self._alert_counter = 1
    
    def _generate_alert_id(self) -> str:
        """Alarm ID üretir"""
        alert_id = f"ALERT-{self._alert_counter:06d}"
        self._alert_counter += 1
        return alert_id
    
    def _create_alert(self, alert_type: str, level: str, description: str,
                     transaction_id: int = None, id_tag: str = None,
                     details: Dict = None) -> Alert:
        """Yeni alarm oluşturur"""
        alert = Alert(
            alert_id=self._generate_alert_id(),
            alert_type=alert_type,
            level=level,
            timestamp=datetime.now(),
            transaction_id=transaction_id,
            id_tag=id_tag,
            description=description,
            details=details or {}
        )
        self.alerts.append(alert)
        return alert
    
    def track_message(self, message: Dict[str, Any], client_ip: str = None):
        """Mesajı kaydeder ve analiz eder"""
        message_copy = message.copy()
        message_copy["_timestamp"] = datetime.now().isoformat()
        message_copy["_client_ip"] = client_ip
        self.message_history.append(message_copy)
        
        # Son 1000 mesajı tut
        if len(self.message_history) > 1000:
            self.message_history = self.message_history[-1000:]
    
    def check_ip_change(self, transaction_id: int, current_ip: str, 
                       message_type: str) -> Optional[Alert]:
        """IP değişikliğini kontrol eder"""
        if transaction_id in self.ip_tracking:
            previous_ip = self.ip_tracking[transaction_id]
            if previous_ip != current_ip:
                return self._create_alert(
                    alert_type=AlertType.IP_CHANGE,
                    level=AlertLevel.CRITICAL,
                    description=f"IP address change detected for transaction {transaction_id}",
                    transaction_id=transaction_id,
                    details={
                        "previous_ip": previous_ip,
                        "current_ip": current_ip,
                        "message_type": message_type
                    }
                )
        else:
            self.ip_tracking[transaction_id] = current_ip
        
        return None
    
    def check_connector_change(self, transaction_id: int, current_connector: int) -> Optional[Alert]:
        """Connector değişikliğini kontrol eder"""
        if transaction_id in self.connector_tracking:
            previous_connector = self.connector_tracking[transaction_id]
            if previous_connector != current_connector:
                return self._create_alert(
                    alert_type=AlertType.CONNECTOR_MISMATCH,
                    level=AlertLevel.CRITICAL,
                    description=f"Connector mismatch for transaction {transaction_id}",
                    transaction_id=transaction_id,
                    details={
                        "previous_connector": previous_connector,
                        "current_connector": current_connector
                    }
                )
        else:
            self.connector_tracking[transaction_id] = current_connector
        
        return None
    
    def check_id_tag_mismatch(self, transaction_id: int, expected_id_tag: str, 
                             received_id_tag: str, message_type: str) -> Optional[Alert]:
        """ID tag uyumsuzluğunu kontrol eder"""
        if expected_id_tag != received_id_tag:
            return self._create_alert(
                alert_type=AlertType.ID_TAG_MISMATCH,
                level=AlertLevel.CRITICAL,
                description=f"ID tag mismatch in {message_type} for transaction {transaction_id}",
                transaction_id=transaction_id,
                id_tag=received_id_tag,
                details={
                    "expected_id_tag": expected_id_tag,
                    "received_id_tag": received_id_tag,
                    "message_type": message_type
                }
            )
        return None
    
    def check_replay_attack(self, message: Dict[str, Any]) -> Optional[Alert]:
        """Replay saldırısını kontrol eder"""
        # Mesaj hash'ini oluştur
        message_str = json.dumps(message, sort_keys=True)
        import hashlib
        message_hash = hashlib.md5(message_str.encode()).hexdigest()
        
        now = datetime.now()
        
        # Son 60 saniyede aynı mesaj var mı?
        recent_occurrences = [
            ts for ts in self.message_hashes[message_hash]
            if (now - ts).total_seconds() < 60
        ]
        
        self.message_hashes[message_hash].append(now)
        
        if len(recent_occurrences) > 0:
            return self._create_alert(
                alert_type=AlertType.REPLAY_ATTACK,
                level=AlertLevel.WARNING,
                description="Potential replay attack detected - duplicate message",
                transaction_id=message.get("transactionId"),
                details={
                    "message_type": message.get("messageType"),
                    "occurrences": len(recent_occurrences) + 1,
                    "time_window_seconds": 60
                }
            )
        
        return None
    
    def check_abnormal_meter_value(self, transaction_id: int, meter_value: int,
                                   previous_value: int = None) -> Optional[Alert]:
        """Anormal sayaç değerini kontrol eder"""
        if previous_value is not None:
            # Geriye gitme kontrolü
            if meter_value < previous_value:
                return self._create_alert(
                    alert_type=AlertType.ABNORMAL_METER_VALUE,
                    level=AlertLevel.WARNING,
                    description=f"Meter value decreased for transaction {transaction_id}",
                    transaction_id=transaction_id,
                    details={
                        "previous_value": previous_value,
                        "current_value": meter_value,
                        "difference": meter_value - previous_value
                    }
                )
            
            # Aşırı artış kontrolü (1 saat içinde 50kWh'den fazla)
            diff = meter_value - previous_value
            if diff > 50000:  # 50 kWh
                return self._create_alert(
                    alert_type=AlertType.ABNORMAL_METER_VALUE,
                    level=AlertLevel.WARNING,
                    description=f"Abnormally high meter value increase for transaction {transaction_id}",
                    transaction_id=transaction_id,
                    details={
                        "previous_value": previous_value,
                        "current_value": meter_value,
                        "difference": diff
                    }
                )
        
        return None
    
    def check_rapid_transactions(self, id_tag: str, transaction_id: int) -> Optional[Alert]:
        """Hızlı ardışık transaction'ları kontrol eder"""
        if transaction_id in self.transaction_start_times:
            return None
        
        self.transaction_start_times[transaction_id] = datetime.now()
        
        # Son 5 dakikada aynı id_tag için kaç transaction var?
        now = datetime.now()
        recent_transactions = [
            tid for tid, ts in self.transaction_start_times.items()
            if (now - ts).total_seconds() < 300  # 5 dakika
        ]
        
        if len(recent_transactions) > 3:
            return self._create_alert(
                alert_type=AlertType.RAPID_TRANSACTION,
                level=AlertLevel.WARNING,
                description=f"Rapid successive transactions detected for {id_tag}",
                transaction_id=transaction_id,
                id_tag=id_tag,
                details={
                    "transaction_count": len(recent_transactions),
                    "time_window_seconds": 300
                }
            )
        
        return None
    
    def analyze_session_hijack(self, transaction_id: int, session_data: Dict,
                              message: Dict, client_ip: str) -> List[Alert]:
        """Oturum çalma analizi yapar"""
        alerts = []
        
        # IP değişikliği kontrolü
        ip_alert = self.check_ip_change(transaction_id, client_ip, 
                                        message.get("messageType", "Unknown"))
        if ip_alert:
            alerts.append(ip_alert)
        
        # Connector değişikliği kontrolü
        if "connectorId" in message:
            connector_alert = self.check_connector_change(
                transaction_id, message["connectorId"]
            )
            if connector_alert:
                alerts.append(connector_alert)
        
        # ID tag kontrolü
        if "idTag" in message and session_data.get("id_tag"):
            id_tag_alert = self.check_id_tag_mismatch(
                transaction_id,
                session_data["id_tag"],
                message["idTag"],
                message.get("messageType", "Unknown")
            )
            if id_tag_alert:
                alerts.append(id_tag_alert)
        
        # Replay kontrolü
        replay_alert = self.check_replay_attack(message)
        if replay_alert:
            alerts.append(replay_alert)
        
        # Eğer birden fazla kritik alarm varsa, session hijacking alarm
        critical_alerts = [a for a in alerts if a.level == AlertLevel.CRITICAL]
        if len(critical_alerts) >= 2:
            hijack_alert = self._create_alert(
                alert_type=AlertType.SESSION_HIJACK,
                level=AlertLevel.CRITICAL,
                description=f"POSSIBLE SESSION HIJACKING DETECTED for transaction {transaction_id}",
                transaction_id=transaction_id,
                id_tag=session_data.get("id_tag"),
                details={
                    "indicators": len(critical_alerts),
                    "alert_types": [a.alert_type for a in critical_alerts]
                }
            )
            alerts.append(hijack_alert)
        
        return alerts
    
    def get_alerts(self, level: str = None, alert_type: str = None, 
                   limit: int = None) -> List[Dict]:
        """Alarm listesini filtreler ve döndürür"""
        filtered = self.alerts
        
        if level:
            filtered = [a for a in filtered if a.level == level]
        
        if alert_type:
            filtered = [a for a in filtered if a.alert_type == alert_type]
        
        if limit:
            filtered = filtered[-limit:]
        
        return [a.to_dict() for a in filtered]
    
    def get_critical_alerts(self) -> List[Dict]:
        """Kritik alarmları döndürür"""
        return self.get_alerts(level=AlertLevel.CRITICAL)
    
    def clear_old_alerts(self, hours: int = 24):
        """Eski alarmları temizler"""
        cutoff = datetime.now() - timedelta(hours=hours)
        self.alerts = [a for a in self.alerts if a.timestamp > cutoff]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Alarm istatistiklerini döndürür"""
        return {
            "total_alerts": len(self.alerts),
            "critical": len([a for a in self.alerts if a.level == AlertLevel.CRITICAL]),
            "warning": len([a for a in self.alerts if a.level == AlertLevel.WARNING]),
            "info": len([a for a in self.alerts if a.level == AlertLevel.INFO]),
            "by_type": {
                alert_type: len([a for a in self.alerts if a.alert_type == alert_type])
                for alert_type in [
                    AlertType.SESSION_HIJACK,
                    AlertType.ID_TAG_MISMATCH,
                    AlertType.IP_CHANGE,
                    AlertType.CONNECTOR_MISMATCH,
                    AlertType.REPLAY_ATTACK,
                    AlertType.ABNORMAL_METER_VALUE
                ]
            }
        }
