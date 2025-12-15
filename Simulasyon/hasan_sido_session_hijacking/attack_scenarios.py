"""
Saldırı Senaryoları
Session Hijacking ve diğer saldırı simülasyonları
"""

import asyncio
import random
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum

from ocpp_messages import MeterValues, StopTransaction, RemoteStopTransaction
from charging_session import ChargingSession, SessionState


class AttackType(Enum):
    """Saldırı tipleri"""
    SESSION_HIJACK_IP = "session_hijack_ip"
    SESSION_HIJACK_ID_SPOOFING = "session_hijack_id_spoofing"
    REPLAY_ATTACK = "replay_attack"
    CONNECTOR_SPOOFING = "connector_spoofing"
    METER_MANIPULATION = "meter_manipulation"
    PREMATURE_STOP = "premature_stop"


class AttackScenario:
    """Saldırı senaryosu temel sınıfı"""
    
    def __init__(self, attack_type: AttackType, description: str):
        self.attack_type = attack_type
        self.description = description
        self.executed = False
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.actions_log: List[Dict] = []
    
    def log_action(self, action: str, details: Dict[str, Any]):
        """Saldırı eylemini loglar"""
        self.actions_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details
        })
    
    async def execute(self, session: ChargingSession, **kwargs) -> Dict[str, Any]:
        """Saldırıyı çalıştırır"""
        raise NotImplementedError


class IPChangeHijackScenario(AttackScenario):
    """IP değiştirerek oturum ele geçirme senaryosu"""
    
    def __init__(self):
        super().__init__(
            attack_type=AttackType.SESSION_HIJACK_IP,
            description="Attacker takes over session from different IP address"
        )
    
    async def execute(self, session: ChargingSession, 
                     attacker_ip: str = "192.168.1.100", **kwargs) -> Dict[str, Any]:
        """Farklı IP'den oturuma müdahale eder"""
        self.start_time = datetime.now()
        self.executed = True
        
        if not session.transaction_id:
            return {"success": False, "error": "No active transaction"}
        
        # 1. Saldırgan meter values gönderir
        self.log_action("send_meter_values", {
            "transaction_id": session.transaction_id,
            "attacker_ip": attacker_ip,
            "original_ip": session.client_ip,
            "meter_value": session.get_current_meter()
        })
        
        meter_msg = MeterValues.create(
            connector_id=session.connector_id,
            transaction_id=session.transaction_id,
            meter_value=session.get_current_meter()
        )
        
        # 2. Birkaç saniye bekle, sonra stop transaction gönder
        await asyncio.sleep(2)
        
        self.log_action("send_stop_transaction", {
            "transaction_id": session.transaction_id,
            "attacker_ip": attacker_ip,
            "reason": "Hijacked by attacker"
        })
        
        stop_msg = StopTransaction.create(
            transaction_id=session.transaction_id,
            id_tag=session.id_tag,  # Gerçek kullanıcının ID'si
            meter_stop=session.get_current_meter(),
            reason="Remote"
        )
        
        self.end_time = datetime.now()
        
        return {
            "success": True,
            "attack_type": self.attack_type.value,
            "description": self.description,
            "messages_sent": [meter_msg, stop_msg],
            "attacker_ip": attacker_ip,
            "original_ip": session.client_ip,
            "transaction_id": session.transaction_id,
            "actions": self.actions_log
        }


class IDSpoofingHijackScenario(AttackScenario):
    """ID Tag spoofing ile oturum ele geçirme"""
    
    def __init__(self):
        super().__init__(
            attack_type=AttackType.SESSION_HIJACK_ID_SPOOFING,
            description="Attacker spoofs ID tag to hijack session"
        )
    
    async def execute(self, session: ChargingSession,
                     fake_id_tag: str = "ATTACKER_001", **kwargs) -> Dict[str, Any]:
        """Sahte ID tag ile oturuma müdahale eder"""
        self.start_time = datetime.now()
        self.executed = True
        
        if not session.transaction_id:
            return {"success": False, "error": "No active transaction"}
        
        # 1. Sahte ID ile meter values gönder
        self.log_action("send_meter_values_fake_id", {
            "transaction_id": session.transaction_id,
            "fake_id_tag": fake_id_tag,
            "original_id_tag": session.id_tag
        })
        
        meter_msg = MeterValues.create(
            connector_id=session.connector_id,
            transaction_id=session.transaction_id,
            meter_value=session.get_current_meter()
        )
        
        await asyncio.sleep(1)
        
        # 2. Sahte ID ile stop transaction
        self.log_action("send_stop_transaction_fake_id", {
            "transaction_id": session.transaction_id,
            "fake_id_tag": fake_id_tag,
            "original_id_tag": session.id_tag
        })
        
        stop_msg = StopTransaction.create(
            transaction_id=session.transaction_id,
            id_tag=fake_id_tag,  # SAHTE ID
            meter_stop=session.get_current_meter(),
            reason="Local"
        )
        
        self.end_time = datetime.now()
        
        return {
            "success": True,
            "attack_type": self.attack_type.value,
            "description": self.description,
            "messages_sent": [meter_msg, stop_msg],
            "fake_id_tag": fake_id_tag,
            "original_id_tag": session.id_tag,
            "transaction_id": session.transaction_id,
            "actions": self.actions_log
        }


class ReplayAttackScenario(AttackScenario):
    """Replay saldırısı senaryosu"""
    
    def __init__(self):
        super().__init__(
            attack_type=AttackType.REPLAY_ATTACK,
            description="Attacker replays captured OCPP messages"
        )
        self.captured_messages: List[Dict] = []
    
    def capture_message(self, message: Dict[str, Any]):
        """Mesajı yakalar"""
        self.captured_messages.append({
            "captured_at": datetime.now().isoformat(),
            "message": message.copy()
        })
    
    async def execute(self, session: ChargingSession, **kwargs) -> Dict[str, Any]:
        """Yakalanan mesajları tekrar gönderir"""
        self.start_time = datetime.now()
        self.executed = True
        
        if not self.captured_messages:
            return {"success": False, "error": "No captured messages"}
        
        replayed = []
        
        for captured in self.captured_messages[:3]:  # İlk 3 mesajı replay et
            self.log_action("replay_message", {
                "original_time": captured["captured_at"],
                "replay_time": datetime.now().isoformat(),
                "message_type": captured["message"].get("messageType")
            })
            
            replayed.append(captured["message"])
            await asyncio.sleep(0.5)
        
        self.end_time = datetime.now()
        
        return {
            "success": True,
            "attack_type": self.attack_type.value,
            "description": self.description,
            "messages_replayed": replayed,
            "replay_count": len(replayed),
            "actions": self.actions_log
        }


class ConnectorSpoofingScenario(AttackScenario):
    """Connector ID değiştirme senaryosu"""
    
    def __init__(self):
        super().__init__(
            attack_type=AttackType.CONNECTOR_SPOOFING,
            description="Attacker sends messages with different connector ID"
        )
    
    async def execute(self, session: ChargingSession,
                     fake_connector_id: int = 99, **kwargs) -> Dict[str, Any]:
        """Farklı connector ID ile mesaj gönderir"""
        self.start_time = datetime.now()
        self.executed = True
        
        if not session.transaction_id:
            return {"success": False, "error": "No active transaction"}
        
        self.log_action("send_meter_values_fake_connector", {
            "transaction_id": session.transaction_id,
            "fake_connector_id": fake_connector_id,
            "original_connector_id": session.connector_id
        })
        
        # Farklı connector ID ile meter values
        meter_msg = MeterValues.create(
            connector_id=fake_connector_id,  # SAHTE CONNECTOR
            transaction_id=session.transaction_id,
            meter_value=session.get_current_meter()
        )
        
        self.end_time = datetime.now()
        
        return {
            "success": True,
            "attack_type": self.attack_type.value,
            "description": self.description,
            "messages_sent": [meter_msg],
            "fake_connector_id": fake_connector_id,
            "original_connector_id": session.connector_id,
            "transaction_id": session.transaction_id,
            "actions": self.actions_log
        }


class MeterManipulationScenario(AttackScenario):
    """Sayaç değeri manipülasyonu senaryosu"""
    
    def __init__(self):
        super().__init__(
            attack_type=AttackType.METER_MANIPULATION,
            description="Attacker manipulates meter values to charge for free"
        )
    
    async def execute(self, session: ChargingSession, **kwargs) -> Dict[str, Any]:
        """Sayaç değerini manipüle eder"""
        self.start_time = datetime.now()
        self.executed = True
        
        if not session.transaction_id:
            return {"success": False, "error": "No active transaction"}
        
        # 1. Normal meter value gönder
        current_meter = session.get_current_meter()
        
        self.log_action("send_normal_meter", {
            "meter_value": current_meter
        })
        
        # 2. Geriye giden meter value (bedava şarj için)
        fake_meter = session.meter_start + random.randint(100, 500)  # Çok düşük
        
        self.log_action("send_manipulated_meter", {
            "original_meter": current_meter,
            "manipulated_meter": fake_meter,
            "difference": current_meter - fake_meter
        })
        
        meter_msg = MeterValues.create(
            connector_id=session.connector_id,
            transaction_id=session.transaction_id,
            meter_value=fake_meter  # MANİPÜLE EDİLMİŞ DEĞER
        )
        
        await asyncio.sleep(1)
        
        # 3. Stop transaction ile düşük değer gönder
        self.log_action("send_stop_with_low_meter", {
            "meter_stop": fake_meter,
            "actual_consumption": current_meter - session.meter_start,
            "reported_consumption": fake_meter - session.meter_start
        })
        
        stop_msg = StopTransaction.create(
            transaction_id=session.transaction_id,
            id_tag=session.id_tag,
            meter_stop=fake_meter,  # DÜŞÜK DEĞER
            reason="Local"
        )
        
        self.end_time = datetime.now()
        
        return {
            "success": True,
            "attack_type": self.attack_type.value,
            "description": self.description,
            "messages_sent": [meter_msg, stop_msg],
            "original_meter": current_meter,
            "manipulated_meter": fake_meter,
            "energy_stolen_wh": current_meter - fake_meter,
            "transaction_id": session.transaction_id,
            "actions": self.actions_log
        }


class PrematureStopScenario(AttackScenario):
    """Erken sonlandırma saldırısı"""
    
    def __init__(self):
        super().__init__(
            attack_type=AttackType.PREMATURE_STOP,
            description="Attacker prematurely stops legitimate user's session"
        )
    
    async def execute(self, session: ChargingSession,
                     attacker_ip: str = "10.0.0.50", **kwargs) -> Dict[str, Any]:
        """Kullanıcının oturumunu erken sonlandırır"""
        self.start_time = datetime.now()
        self.executed = True
        
        if not session.transaction_id:
            return {"success": False, "error": "No active transaction"}
        
        self.log_action("send_premature_stop", {
            "transaction_id": session.transaction_id,
            "attacker_ip": attacker_ip,
            "original_ip": session.client_ip,
            "session_duration_seconds": (datetime.now() - session.start_time).total_seconds()
        })
        
        # Aniden stop transaction gönder
        stop_msg = StopTransaction.create(
            transaction_id=session.transaction_id,
            id_tag=session.id_tag,
            meter_stop=session.get_current_meter(),
            reason="Remote"  # Uzaktan durduruldu
        )
        
        self.end_time = datetime.now()
        
        return {
            "success": True,
            "attack_type": self.attack_type.value,
            "description": self.description,
            "messages_sent": [stop_msg],
            "attacker_ip": attacker_ip,
            "original_ip": session.client_ip,
            "transaction_id": session.transaction_id,
            "actions": self.actions_log
        }


class AttackOrchestrator:
    """Saldırıları yöneten sınıf"""
    
    def __init__(self):
        self.scenarios: Dict[AttackType, AttackScenario] = {
            AttackType.SESSION_HIJACK_IP: IPChangeHijackScenario(),
            AttackType.SESSION_HIJACK_ID_SPOOFING: IDSpoofingHijackScenario(),
            AttackType.REPLAY_ATTACK: ReplayAttackScenario(),
            AttackType.CONNECTOR_SPOOFING: ConnectorSpoofingScenario(),
            AttackType.METER_MANIPULATION: MeterManipulationScenario(),
            AttackType.PREMATURE_STOP: PrematureStopScenario()
        }
        self.attack_history: List[Dict] = []
    
    async def execute_attack(self, attack_type: AttackType, 
                           session: ChargingSession, **kwargs) -> Dict[str, Any]:
        """Belirtilen saldırıyı çalıştırır"""
        if attack_type not in self.scenarios:
            return {"success": False, "error": f"Unknown attack type: {attack_type}"}
        
        scenario = self.scenarios[attack_type]
        result = await scenario.execute(session, **kwargs)
        
        self.attack_history.append({
            "timestamp": datetime.now().isoformat(),
            "attack_type": attack_type.value,
            "result": result
        })
        
        return result
    
    def get_scenario(self, attack_type: AttackType) -> Optional[AttackScenario]:
        """Saldırı senaryosunu döndürür"""
        return self.scenarios.get(attack_type)
    
    def get_attack_history(self) -> List[Dict]:
        """Saldırı geçmişini döndürür"""
        return self.attack_history.copy()
