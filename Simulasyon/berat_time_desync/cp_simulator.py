# EVSE-Security-Lab/core/cp_simulator.py

import time
from core.ocpp_sender import send_message
from core.utils.logger import log_info, log_attack, log_alarm

class CPSimulator:
    def __init__(self, cp_id, mode, anomaly_payload_generator=None):
        self.cp_id = cp_id
        self.mode = mode
        self.anomaly_payload_generator = anomaly_payload_generator

    def start_transaction(self):
        """
        Normal mod: Temiz StartTransaction gönder (alarm tetiklemez)
        Attack mod: Kimlik atlama saldırısına uygun manipüle mesaj gönderir (alarm tetikler)
        """
        if self.mode == "attack":
            log_attack(f"{self.cp_id} saldırılı StartTransaction gönderiyor...")

            message = {
                "timestamp": time.time(),
                "senaryo": "TimeDesync",
                "cp_id": self.cp_id,
                "message_type": "StartTransaction",
                "transaction_id": 999,     # saldırı için özel ID
                "source": "CP"
            }

            send_message(message)
            return message

        else:
            log_info(f"{self.cp_id} temiz StartTransaction gönderiyor...")

            # Normal akışta sahte transaction_id kullanılmayacak
            message = {
                "timestamp": time.time(),
                "senaryo": "TimeDesync",
                "cp_id": self.cp_id,
                "message_type": "StartTransaction",
                "transaction_id": 1,       # normal bir değer
                "source": "CP"
            }

            send_message(message)
            return message

    def send_meter_values(self, count=3):
        """
        Normal mod: ölçüm değerlerini olduğu gibi gönderir.
        Attack mod: anomaly_payload_generator üzerinden kaydırılmış değer üretir.
        """

        for i in range(count):
            if self.mode == "attack" and self.anomaly_payload_generator:
                anomalous_payload = self.anomaly_payload_generator.generate()
                log_attack(f"{self.cp_id} anomalili MeterValue gönderildi ({i+1}/{count}).")
                send_message(anomalous_payload)

            else:
                normal_payload = {
                    "timestamp": time.time(),
                    "cp_id": self.cp_id,
                    "senaryo": "TimeDesync",
                    "message_type": "MeterValues",
                    "value": 50.0,  # normal enerji okuması
                    "source": "CP"
                }
                log_info(f"[{self.cp_id}] 🟢 Normal MeterValue gönderildi ({i+1}/{count}).")
                send_message(normal_payload)

            time.sleep(0.3)

        log_info(f"{self.cp_id} ✓ Senaryo Akışı Tamamlandı.")
