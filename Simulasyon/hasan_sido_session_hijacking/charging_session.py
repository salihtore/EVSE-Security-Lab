"""
Şarj Oturumu Yönetimi
Normal şarj oturumlarını yöneten modül
"""

import asyncio
import random
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class SessionState(Enum):
    """Oturum durumları"""
    IDLE = "idle"
    AUTHORIZING = "authorizing"
    STARTING = "starting"
    CHARGING = "charging"
    STOPPING = "stopping"
    COMPLETED = "completed"
    HIJACKED = "hijacked"


@dataclass
class ChargingSession:
    """Şarj oturumu veri modeli"""
    session_id: str
    transaction_id: Optional[int] = None
    id_tag: str = ""
    connector_id: int = 1
    meter_start: int = 0
    meter_current: int = 0
    meter_stop: int = 0
    state: SessionState = SessionState.IDLE
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    client_ip: Optional[str] = None
    charging_power: int = 7400  # Watt (örnek: 7.4kW)
    metadata: Dict[str, Any] = field(default_factory=dict)
    message_count: int = 0
    last_meter_value_time: Optional[datetime] = None
    
    def calculate_energy(self, seconds: float) -> int:
        """Tüketilen enerjiyi hesaplar (Wh)"""
        hours = seconds / 3600
        energy_wh = int(self.charging_power * hours)
        return energy_wh
    
    def get_current_meter(self) -> int:
        """Güncel sayaç değerini döndürür"""
        if self.state == SessionState.CHARGING and self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            return self.meter_start + self.calculate_energy(elapsed)
        return self.meter_current
    
    def to_dict(self) -> Dict[str, Any]:
        """Oturumu dictionary'ye çevirir"""
        return {
            "session_id": self.session_id,
            "transaction_id": self.transaction_id,
            "id_tag": self.id_tag,
            "connector_id": self.connector_id,
            "meter_start": self.meter_start,
            "meter_current": self.get_current_meter(),
            "meter_stop": self.meter_stop,
            "state": self.state.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "client_ip": self.client_ip,
            "charging_power": self.charging_power,
            "message_count": self.message_count,
            "metadata": self.metadata
        }


class SessionManager:
    """Şarj oturumlarını yöneten sınıf"""
    
    def __init__(self):
        self.sessions: Dict[int, ChargingSession] = {}  # transaction_id -> session
        self.active_sessions: Dict[str, ChargingSession] = {}  # id_tag -> session
        self.session_history: list = []
        self._next_transaction_id = 1000
        self._lock = asyncio.Lock()
    
    def get_next_transaction_id(self) -> int:
        """Yeni transaction ID üretir"""
        tid = self._next_transaction_id
        self._next_transaction_id += 1
        return tid
    
    async def create_session(self, id_tag: str, connector_id: int = 1, 
                            client_ip: str = None) -> ChargingSession:
        """Yeni şarj oturumu oluşturur"""
        async with self._lock:
            if id_tag in self.active_sessions:
                raise ValueError(f"Active session already exists for {id_tag}")
            
            import uuid
            session = ChargingSession(
                session_id=str(uuid.uuid4()),
                id_tag=id_tag,
                connector_id=connector_id,
                client_ip=client_ip,
                state=SessionState.AUTHORIZING
            )
            
            self.active_sessions[id_tag] = session
            return session
    
    async def start_transaction(self, session: ChargingSession, meter_start: int = None) -> int:
        """Transaction başlatır"""
        async with self._lock:
            if meter_start is None:
                meter_start = random.randint(10000, 50000)
            
            transaction_id = self.get_next_transaction_id()
            session.transaction_id = transaction_id
            session.meter_start = meter_start
            session.meter_current = meter_start
            session.state = SessionState.CHARGING
            session.start_time = datetime.now()
            
            self.sessions[transaction_id] = session
            return transaction_id
    
    async def update_meter_value(self, transaction_id: int, meter_value: int = None):
        """Sayaç değerini günceller"""
        async with self._lock:
            if transaction_id not in self.sessions:
                raise ValueError(f"Transaction {transaction_id} not found")
            
            session = self.sessions[transaction_id]
            
            if meter_value is not None:
                session.meter_current = meter_value
            else:
                session.meter_current = session.get_current_meter()
            
            session.last_meter_value_time = datetime.now()
            session.message_count += 1
    
    async def stop_transaction(self, transaction_id: int, meter_stop: int = None) -> ChargingSession:
        """Transaction durdurur"""
        async with self._lock:
            if transaction_id not in self.sessions:
                raise ValueError(f"Transaction {transaction_id} not found")
            
            session = self.sessions[transaction_id]
            
            if meter_stop is None:
                meter_stop = session.get_current_meter()
            
            session.meter_stop = meter_stop
            session.meter_current = meter_stop
            session.state = SessionState.COMPLETED
            session.end_time = datetime.now()
            
            # Aktif oturumlardan kaldır
            if session.id_tag in self.active_sessions:
                del self.active_sessions[session.id_tag]
            
            # Geçmişe ekle
            self.session_history.append(session.to_dict())
            
            return session
    
    def get_session_by_transaction(self, transaction_id: int) -> Optional[ChargingSession]:
        """Transaction ID ile oturum getirir"""
        return self.sessions.get(transaction_id)
    
    def get_session_by_id_tag(self, id_tag: str) -> Optional[ChargingSession]:
        """ID tag ile aktif oturum getirir"""
        return self.active_sessions.get(id_tag)
    
    def get_all_active_sessions(self) -> list:
        """Tüm aktif oturumları döndürür"""
        return [s.to_dict() for s in self.sessions.values() if s.state == SessionState.CHARGING]
    
    def get_session_history(self) -> list:
        """Oturum geçmişini döndürür"""
        return self.session_history.copy()
    
    async def mark_session_hijacked(self, transaction_id: int):
        """Oturumu ele geçirilmiş olarak işaretler"""
        async with self._lock:
            if transaction_id in self.sessions:
                session = self.sessions[transaction_id]
                session.state = SessionState.HIJACKED
                session.metadata["hijacked_at"] = datetime.now().isoformat()
