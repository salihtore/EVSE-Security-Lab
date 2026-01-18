from typing import Dict

from src.utils.logger import logger


class PolicyEngine:
    """
    Saldırı Tespit Sistemi'nden (IDS) Saldırı Önleme Sistemi'ne (IPS) geçiş katmanı.
    Tespit edilen anomalilere otomatik müdahale aksiyonları atar.
    """

    def handle_alarm(self, alarm: Dict) -> Dict:
        anomaly_type = alarm.get("anomaly_type")
        severity = str(alarm.get("severity", "LOW")).upper()
        cp_id = alarm.get("cp_id", "unknown")

        # 🧠 ML (AI) Onay Mekanizması
        ml_data = alarm.get("ml", {})
        try:
            ml_confidence = float(ml_data.get("confidence")) if isinstance(ml_data, dict) and ml_data.get("confidence") is not None else None
        except (ValueError, TypeError):
            ml_confidence = None
            
        # Kritiklik ve Tip Kontrolü (Senaryo Bazlı Özelleştirilmiş IPS)
        if severity == "HIGH":
            # Hedef aksiyonu belirle
            target_action = "EMERGENCY_STOP"
            if anomaly_type == "THERMAL_MANIPULATION":
                target_action = "THERMAL_LOCKDOWN"
            elif anomaly_type == "AUTH_BYPASS":
                target_action = "CREDENTIAL_REJECT"
            elif anomaly_type == "REPLAY":
                target_action = "SESSION_INVALIDATE"
            elif anomaly_type == "PHANTOM_CURRENT":
                target_action = "POWER_TRIP_STOP"
            elif anomaly_type == "ORPHAN_SESSION":
                target_action = "SESSION_CLEANUP"
            elif anomaly_type == "ZERO_ENERGY_FLOOD":
                target_action = "QUEUE_RATE_LIMIT"
            elif anomaly_type == "TIME_DESYNC":
                target_action = "CLOCK_RE_SYNC"

            # ⚖️ HİBRİT KARAR: AI Onayı Kontrolü
            # Eğer AI skoru orta/düşükse (< 0.7), ağır aksiyonu "ASKIYA AL"
            # Bu, sistemin sadece %70+ güven durumunda fiziksel müdahale yapmasını sağlar.
            if ml_confidence is not None and ml_confidence < 0.7:
                logger.warning(f"⚖️ [HYBRID IPS] Kural ihlali var ama AI güveni düşük ({ml_confidence:.2f} < 0.70). Aksiyon ASKIYA ALINDI.")
                action = "AI_VETTING_PENDING" # UI Tag: Yapay Zeka İncelemesinde
            else:
                action = target_action
                
        elif severity == "MEDIUM":
            # Orta risklerde AI skoru çok düşükse izlemeye al
            if ml_confidence is not None and ml_confidence < 0.3:
                action = "OBSERVE_ONLY"
            else:
                action = "ENHANCED_AUDIT"

        # Müdahale verisini alarm objesine işle
        mitigation = {
            "action": action,
            "status": "EXECUTED" if action != "MONITOR_ONLY" else "LOGGED",
            "timestamp": alarm.get("timestamp")
        }
        
        alarm["mitigation"] = mitigation

        if action != "MONITOR_ONLY":
            logger.warning(f"🛡️ [IPS] MÜDAHALE: {cp_id} üzerinde {action} aksiyonu uygulandı! (Sebep: {anomaly_type})")
        
        return alarm
