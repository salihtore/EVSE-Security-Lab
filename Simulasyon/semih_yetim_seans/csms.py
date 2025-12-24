# csms.py
import asyncio
import logging
import time
from datetime import datetime, timezone

import websockets
from ocpp.routing import on
from ocpp.v16 import ChargePoint as Cp
from ocpp.v16.enums import Action, RegistrationStatus, ChargePointStatus
from ocpp.v16 import call_result as cr_module

from .anomaly_detector import AnomalyDetector
#  ANA MOTOR ALARM ENTEGRASYONU
from src.core.scenario_adapter import ScenarioAdapter
from src.core.event_pipeline import event_pipeline



logging.basicConfig(level=logging.INFO)

# -----------------------------
#  OCPP SÜRÜM UYUMLULUK KATMANI
# -----------------------------
def _resolve_res(name):
    """
    ocpp.v16.call_result içinde hem Eski (BootNotification),
    hem Yeni (BootNotificationPayload) isimlerini deneyip
    hangisi varsa onu döndürür.
    """
    cls = getattr(cr_module, f"{name}Payload", None)
    if cls is not None:
        return cls

    cls = getattr(cr_module, name, None)
    if cls is not None:
        return cls

    raise ImportError(
        f"ocpp.v16.call_result içinde ne '{name}Payload' ne de '{name}' sınıfı yok. "
        "Lütfen 'pip show ocpp' ile sürümü kontrol et."
    )


BootNotificationConf = _resolve_res("BootNotification")
StatusNotificationConf = _resolve_res("StatusNotification")
StartTransactionConf = _resolve_res("StartTransaction")
MeterValuesConf = _resolve_res("MeterValues")
StopTransactionConf = _resolve_res("StopTransaction")

# Global Anomaly Detector instance
detector = AnomalyDetector(timeout_sec=30)  # Kural-1 için 30 saniye eşiği


class CSMSChargePoint(Cp):


    def __init__(self, charge_point_id, connection):
        super().__init__(charge_point_id, connection)
        # Bu CP için adapter oluşturuyoruz (alarmı ana motora basacak)
        self.adapter = ScenarioAdapter(
            cp_id=charge_point_id,
            scenario_name="semih_yetim_seans",
            event_pipeline=event_pipeline
        )      

    

    @on(Action.boot_notification)
    async def on_boot_notification(self, charge_point_vendor, charge_point_model, **kwargs):
        logging.info(
            f"⚡ CP Bağlandı: id={self.id}, Vendor={charge_point_vendor}, Model={charge_point_model}"
        )

        # Varsayılan olarak connector 1 için başlangıç durumu
        detector.update_state(
            connector_id=1,
            status=ChargePointStatus.available,
            plug_state=False,
            session_active=False,
        )
        self.display_panel()

        return BootNotificationConf(
            status=RegistrationStatus.accepted,
            interval=300,
            current_time=datetime.now(timezone.utc).isoformat(),
        )

    @on(Action.status_notification)
    async def on_status_notification(self, connector_id, status, **kwargs):
        # OCPP, status bilgisini genelde string gönderir; enum'a çevirmeye çalış
        try:
            cp_status = ChargePointStatus(status)
        except ValueError:
            cp_status = status  # Enum dışı bir değer geldiyse olduğu gibi tut

        detector.update_state(connector_id, status=cp_status)

        # Fiş Çekilme Mantığı:
        # Eğer durum 'finishing' veya 'available' ise fişin çekilmiş olabileceğini varsayıyoruz.
        state = detector.session_states.get(connector_id, {})
        if cp_status in (ChargePointStatus.finishing, ChargePointStatus.available) and state.get(
            "plug_state"
        ):
            detector.update_state(connector_id, plug_state=False)

        self.display_panel()

        # Anomali Kontrolü
        anomaly_alarm = detector.check_for_anomaly(connector_id)
        if anomaly_alarm:
            # ✅ Alarmı ana motora gönder
            self.adapter.raise_alarm(
            alarm_type="ORPHAN_SESSION",
            level="HIGH",
            reason=anomaly_alarm,
            evidence={
                "connector_id": connector_id,
                "source": "semih_yetim_seans",
                "where": "status_notification"
            }
        )      


        return StatusNotificationConf()

    @on(Action.start_transaction)
    async def on_start_transaction(self, connector_id, id_tag, meter_start, timestamp, **kwargs):

        transaction_id = int(time.time())
        detector.update_state(
        connector_id,
        session_active=True,
        plug_state=True
        )

        self.display_panel()

        self.adapter.emit_event(
        name="StartTransaction",
        payload={
            "cp_id": self.id,
            "connector_id": connector_id,
            "idTag": id_tag,
            "transactionId": transaction_id,
        },
        severity="INFO",
        source="semih_yetim_seans"
    )


        # ✅ RETURN EN SON
        return StartTransactionConf(
        transaction_id=transaction_id,
        id_tag_info={"status": "Accepted"},
    )


    @on(Action.meter_values)
    async def on_meter_values(self, connector_id, meter_value, **kwargs):
        # MeterValues bilgisini Anomaly Detector'a ilet (Basitlik için sadece son kWh'ı alıyoruz)
        try:
            latest_kwh = meter_value[0]["sampledValue"][0]["value"] if meter_value else 0.0
            detector.update_state(connector_id, meter_total_kwh=float(latest_kwh))
        except (IndexError, TypeError, KeyError, ValueError):
            logging.warning("MeterValues'ta beklenen formatta veri alınamadı.")

        # Kural-3 Kontrolü: Meter değerleri artarken fiş çekiliyse alarm
        anomaly_alarm = detector.check_for_anomaly(connector_id)
        if anomaly_alarm:
            self.adapter.raise_alarm(
            alarm_type="ORPHAN_SESSION",
            level="HIGH",
            reason=anomaly_alarm,
            evidence={
                "connector_id": connector_id,
                "source": "semih_yetim_seans",
                "where": "meter_values"
            }
        )

        return MeterValuesConf()

    @on(Action.stop_transaction)
    async def on_stop_transaction(self, transaction_id, meter_stop, timestamp, **kwargs):
        # Burada connector_id yok, tek connector varsayıyoruz → 1
        connector_id = 1

        # Başarılı StopTx durumunda Yetim Seans riskini azaltmak için durumu sıfırla
        detector.update_state(
            connector_id,
            session_active=False,
            plug_state=False,
            status=ChargePointStatus.available,
        )

        logging.info(f"✅ StopTx Alındı: CP={self.id}, Transaction ID={transaction_id}")
        self.display_panel()
        self.adapter.emit_event(
        name="StopTransaction",
        payload={
            "cp_id": self.id,
            "transactionId": transaction_id,
         },
        severity="INFO",
        source="semih_yetim_seans"
        )

        return StopTransactionConf()

    # Basit konsol paneli
    def display_panel(self):
        print("\n" + "=" * 50)
        print(" ⚡ Yetim Seans İzleme Paneli (CSMS) 🛡️ ".center(50, " "))
        print("=" * 50)

        if not detector.session_states:
            print("Henüz bağlı CP yok...")
            print("=" * 50)
            return

        for conn_id, state in detector.session_states.items():
            plug_status = "🔌 TAKILI" if state.get("plug_state") else "⛔ ÇEKİLİ"
            session_status = "🟢 AKTİF" if state.get("session_active") else "⚫ KAPALI"

            # Kural-1 için zaman bilgisini göster
            time_info = ""
            if state.get("plug_false_time") is not None:
                time_passed = time.time() - state["plug_false_time"]
                time_info = f" ({time_passed:.1f}s geçti / 30s limit)"

            meter_val = state.get("meter_total_kwh", 0.0)

            print(f"| Connector ID: {conn_id}")
            print(f"|   - Durum: {state.get('status')} | Oturum: {session_status}")
            print(f"|   - Fiş: {plug_status}{time_info}")
            print(f"|   - Sayaç: {meter_val:.2f} kWh")
            print("-" * 50)


async def on_connect(connection):
    """
    Her yeni bağlantı için bir CSMSChargePoint instance'ı oluştur
    ve mesajları dinlemeye başla.
    (websockets 13+ için handler tek parametre alıyor.)
    """
    # İstek yolu: örn. "/CP12345"
    try:
        path = connection.request.path
    except AttributeError:
        # Bazı sürümlerde doğrudan 'path' alanı olabilir
        path = getattr(connection, "path", "/unknown")

    charge_point_id = path.strip("/").split("/")[-1] or "unknown_cp"
    logging.info(f"Yeni Charge Point bağlantısı: id={charge_point_id}")

    cp = CSMSChargePoint(charge_point_id, connection)
    await cp.start()


async def main():
    logging.info("Güvenlik Notu: Simülasyon izole ağda yapılmalıdır.")

    server = await websockets.serve(
        on_connect,
        "0.0.0.0",
        9000,
        subprotocols=["ocpp1.6"],
    )

    logging.info("CSMS Başlatıldı: ws://0.0.0.0:9000")
    await server.wait_closed()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("CSMS Kapatılıyor.")