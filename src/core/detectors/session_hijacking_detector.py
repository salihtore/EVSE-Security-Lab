from typing import Dict, Optional, Any
from src.utils.logger import logger

class SessionHijackingDetector:
    """
    Session Hijacking (Oturum Çalma) tespiti.
    Aynı Transaction ID'nin, orijinal CP dışında başka bir CP tarafından kullanıldığını tespit eder.
    
    Senaryo: Hasan (Session Hijacking)
    """
    
    def __init__(self):
        # Transaction ID -> Original CP ID haritası
        # Gerçek hayatta bu Redis/Database üzerinde tutulmalı.
        self.active_sessions = {} # {tx_id: cp_id}
    
    def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        msg_type = event.get("message_type")
        cp_id = event.get("cp_id")
        payload = event.get("payload", {})
        
        if not cp_id:
            return None

        # 1. Oturum Başlangıcı (StartTransaction)
        if msg_type == "StartTransaction":
            tx_id = payload.get("transactionId")
            if tx_id:
                self.active_sessions[str(tx_id)] = cp_id
                
        # 2. Oturum İçi Mesajlar (MeterValues, StopTransaction)
        elif msg_type in ["MeterValues", "StopTransaction"]:
            tx_id = payload.get("transactionId")
            if tx_id:
                tx_id = str(tx_id)
                original_cp = self.active_sessions.get(tx_id)
                
                # Eğer bu transaction ID daha önce başka bir CP ile başladıysa ve şu anki CP farklıysa -> HIJACK!
                if original_cp and original_cp != cp_id:
                    return {
                        "cp_id": cp_id,
                        "anomaly_type": "SESSION_HIJACKING",
                        "severity": "HIGH",
                        "details": {
                            "reason": "Transaction ID usage mismatch (Hijacking)",
                            "original_cp": original_cp,
                            "attacker_cp": cp_id,
                            "transaction_id": tx_id
                        }
                    }
                    
        # Temizlik (StopTransaction gelince silmeli miyiz? Saldırı analizi için silmesek daha iyi)
        
        return None
