# charge_point.py

import asyncio
import logging
import time

import websockets
from ocpp.v16 import ChargePoint as Cp
from ocpp.v16 import call as call_module
from ocpp.v16.enums import ChargePointStatus

logging.basicConfig(level=logging.INFO)

# -----------------------------
#  OCPP SÜRÜM UYUMLULUK KATMANI
# -----------------------------
def _resolve_req(name):
    """
    ocpp.v16.call içinde hem Eski (BootNotification),
    hem Yeni (BootNotificationPayload) isimlerini deneyip
    hangisi varsa onu döndürür.
    """
    # Yeni isim: XyzPayload
    cls = getattr(call_module, f"{name}Payload", None)
    if cls is not None:
        return cls

    # Eski isim: Xyz
    cls = getattr(call_module, name, None)
    if cls is not None:
        return cls

    raise ImportError(
        f"ocpp.v16.call içinde ne '{name}Payload' ne de '{name}' sınıfı bulunamadı. "
        "Lütfen `pip show ocpp` ile sürümü kontrol et."
    )


BootNotificationReq = _resolve_req("BootNotification")
StatusNotificationReq = _resolve_req("StatusNotification")
StartTransactionReq = _resolve_req("StartTransaction")
MeterValuesReq = _resolve_req("MeterValues")
StopTransactionReq = _resolve_req("StopTransaction")


class SimulatedChargePoint(Cp):
    def __init__(self, charge_point_id, connection):
        super().__init__(charge_point_id, connection)
        self.connector_id = 1
        self.current_status = ChargePointStatus.available
        self.session_active = False
        self.transaction_id = None
        self.meter_value = 0.0  # Wh gibi düşün

    async def send_boot_notification(self):
        """BootNotification gönderimi"""
        request = BootNotificationReq(
            charge_point_model="CP-V1",
            charge_point_vendor="SimuTech",
        )
        conf = await self.call(request)
        logging.info(f"🔌 BootNotification gönderildi, cevap: {conf}")

    async def send_status_notification(self, status: ChargePointStatus):
        """Durum bildirimi gönderimi"""
        request = StatusNotificationReq(
            connector_id=self.connector_id,
            error_code="NoError",
            status=status,
        )
        await self.call(request)
        self.current_status = status
        logging.info(f"🔌 StatusNotification gönderildi: {status}")

    async def start_charging(self):
        """Şarj başlangıcı simülasyonu"""
        if not self.session_active:
            self.transaction_id = int(time.time())
            request = StartTransactionReq(
                connector_id=self.connector_id,
                id_tag="ID_USER1",
                meter_start=int(self.meter_value * 100),
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%S") + "Z",
            )
            conf = await self.call(request)
            # CSMS transaction_id'yi override edebilir
            self.transaction_id = getattr(conf, "transaction_id", self.transaction_id)
            self.session_active = True
            await self.send_status_notification(ChargePointStatus.charging)
            logging.info("✅ StartTransaction gönderildi. Şarj başladı.")

    async def simulate_meter_values(self):
        """Sayaç değeri gönderimi (şarj aktifse)"""
        if self.session_active and self.current_status == ChargePointStatus.charging:
            # Sayaç değerini artır (Kural-3 için kritik)
            self.meter_value += 0.05
            request = MeterValuesReq(
                connector_id=self.connector_id,
                meter_value=[
                    {
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S") + "Z",
                        "sampledValue": [
                            {
                                "value": str(self.meter_value),
                                "unit": "Wh",
                            }
                        ],
                    }
                ],
            )
            await self.call(request)
            logging.info(f"📈 MeterValues gönderildi: {self.meter_value:.2f} Wh")

    async def stop_charging(self):
        """Şarj sonlandırma simülasyonu (StopTx)"""
        if self.session_active:
            request = StopTransactionReq(
                transaction_id=self.transaction_id,
                meter_stop=int(self.meter_value * 100),
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%S") + "Z",
                # reason alanı opsiyonel → enum karmaşası yaşamayalım diye göndermiyoruz
            )
            await self.call(request)
            self.session_active = False
            # Normal akışta, Status önce finishing, sonra available olmalı.
            await self.send_status_notification(ChargePointStatus.finishing)
            await self.send_status_notification(ChargePointStatus.available)
            logging.info("🛑 StopTransaction gönderildi. Şarj bitti.")

    # --- Yetim Seans Simülasyon Senaryoları ---

    async def run_scenario_s1_orphan(self):
        """
        S1 - Yetim Seans (Kural-1):
        Fiş çekiliyor (status finishing/available),
        ama StopTransaction GEÇ GELECEK.
        CSMS tarafında 30 sn sonra alarm bekliyoruz.
        """
        logging.warning("\n--- S1: Yetim Seans (StopTx Gecikmesi) Başlatılıyor ---")

        # 1. Normal Şarj Başlat
        await self.start_charging()
        await asyncio.sleep(5)

        # 2. Fiş Çekildi (StatusNotification.finishing/available)
        logging.info("1. Fiş Çekildi: StatusNotification.finishing/available gönderiliyor.")
        await self.send_status_notification(ChargePointStatus.finishing)
        await self.send_status_notification(ChargePointStatus.available)

        # 3. StopTx GÖNDERİLMİYOR (ağ kesintisi gibi düşün)
        logging.warning("2. StopTransaction BİLEREK GÖNDERİLMİYOR (ağ kesintisi simülasyonu).")

        # 4. 35 saniye bekle (Detector timeout 30 sn)
        await asyncio.sleep(35)
        logging.info("3. 35 saniye geçti. CSMS tarafında ALARM bekleniyor (Kural-1).")

        # 5. Seansı temizle (lokal olarak)
        self.session_active = False
        await self.send_status_notification(ChargePointStatus.available)

    async def run_scenario_s2_status_lock(self):
        """
        S2 - Durum Kilitlenmesi (Kural-2):
        Fiş çekilmiş ve StopTx gönderilmiş olmasına rağmen
        istasyon hâlâ 'charging' status bildiriyor.
        """
        logging.warning("\n--- S2: Durum Kilitlenmesi (Charging Status Lock) Başlatılıyor ---")

        # 1. Normal Şarj Başlat
        await self.start_charging()
        await asyncio.sleep(5)

        # 2. Fiş çekildi ve StopTx gönderildi (normal bitiş)
        logging.info("1. Fiş çekildi ve StopTransaction gönderildi (normal bitiş).")
        await self.stop_charging()

        # 3. Hata simülasyonu: hâlâ charging bildiriyor
        logging.error(
            "2. KİLİTLENME HATASI: Seans bittiği halde 'charging' StatusNotification gönderiliyor!"
        )
        await self.send_status_notification(ChargePointStatus.charging)

        # Kural-2: plug_state=false & status=charging olduğu için CSMS hemen alarm vermeli
        await asyncio.sleep(5)
        logging.info("3. 5 saniye bekleme. CSMS tarafında ALARM bekleniyor (Kural-2).")

        # Hata temizliği
        await self.send_status_notification(ChargePointStatus.available)

    async def run_all(self):
        """Tüm senaryoları sırayla çalıştır"""
        # 0. Boot
        await self.send_boot_notification()

        # --- NORMAL AKIŞ ---
        logging.info("\n--- NORMAL AKIŞ BAŞLADI (Başlat-Şarj Et-Bitir) ---")
        await self.start_charging()
        for _ in range(3):
            await self.simulate_meter_values()
            await asyncio.sleep(5)
        await self.stop_charging()

        # --- S1: StopTx gecikmesi ---
        await asyncio.sleep(5)
        await self.run_scenario_s1_orphan()

        # --- S2: Charging status lock ---
        await asyncio.sleep(5)
        await self.run_scenario_s2_status_lock()

        logging.info("\n--- Tüm Senaryolar Tamamlandı. ---")


async def main():
    # CSMS endpoint'i: csms.py şu an 9000 portunda dinliyor
    uri = "ws://127.0.0.1:9000/CP12345"
    async with websockets.connect(uri, subprotocols=["ocpp1.6"]) as ws:
        cp = SimulatedChargePoint("CP12345", ws)
        # cp.start(): gelen mesajları dinler
        # cp.run_all(): senaryoları çalıştırır
        await asyncio.gather(cp.start(), cp.run_all())


if __name__ == "__main__":
    try:
        # Önce csms.py'yi başlat, sonra bu dosyayı çalıştır
        asyncio.run(main())
    except Exception as e:
        logging.error(f"CP Hata: {e}")