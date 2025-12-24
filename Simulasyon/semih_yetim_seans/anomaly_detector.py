# anomaly_detector.py

import time

class AnomalyDetector:
    """
    Yetim Seans Tespit Kurallarını (Kural-1, Kural-2, Kural-3) uygulayan sınıf.
    """
    def __init__(self, timeout_sec=30):
        # Kural-1 için zaman eşiği (SMART Hedef #4'e göre optimize edilebilir, şimdilik 30 sn)
        self.TIMEOUT_SEC = timeout_sec 
        # Bağlantı bazlı oturum verilerini tutar: {connector_id: {'plug_state': bool, 'plug_false_time': float, 'status': str, ...}}
        self.session_states = {} 

    def update_state(self, connector_id, **kwargs):
        """Bir şarj noktasından gelen güncel durumu kaydeder."""
        if connector_id not in self.session_states:
            self.session_states[connector_id] = {
                'plug_state': True, 
                'plug_false_time': None, 
                'status': 'Available', 
                'session_active': False, 
                'meter_total_kwh': 0.0
            }
        
        current_state = self.session_states[connector_id]
        
        # plug_state değişimi kontrolü (Kural-1 için kritik)
        if 'plug_state' in kwargs and kwargs['plug_state'] == False and current_state['plug_state'] == True:
            current_state['plug_false_time'] = time.time()
        elif 'plug_state' in kwargs and kwargs['plug_state'] == True:
            current_state['plug_false_time'] = None # Tekrar takıldıysa sıfırla

        # Diğer durumları güncelle
        current_state.update(kwargs)

    # devre dışı bırakıldı, aynı mantık src/core/detectors/orphan_session_detector.py içinde uygulanıyor
    
    # def check_for_anomaly(self, connector_id):
    #     """Yetim Seans kurallarını kontrol eder ve ALARM üretir."""
    #     state = self.session_states.get(connector_id)
    #     if not state:
    #         return None # Durum yoksa kontrol etme

    #     # Kural-1: plug_state=false olduktan sonra 30 sn içinde StopTx gelmezse ALARM [cite: 116]
    #     if state['plug_state'] == False and state['session_active'] == True and state['plug_false_time'] is not None:
    #         if (time.time() - state['plug_false_time']) > self.TIMEOUT_SEC:
    #             # Normal bir StopTx gelmediği varsayılıyor. (StopTx CSMS tarafından alınırsa session_active=False olmalıdır)
    #             return f"ALARM (Kural-1): Fiş çekili ({self.TIMEOUT_SEC}sn geçti) ama seans ({connector_id}) hâlâ aktif!"
        
    #     # Kural-2: plug_state=false iken status=Charging ise ALARM [cite: 117]
    #     if state['plug_state'] == False and state['status'] == 'Charging':
    #         return f"ALARM (Kural-2): Fiş çekili ama durum ({connector_id}) 'Charging'!"
        
    #     # Kural-3: plug_state=false & session_active=true iken meter_total_kWh artmaya devam ederse ALARM [cite: 118]
    #     # (Bu kuralı simülasyonda tam olarak uygulamak zor, şimdilik sadece status/session_active'i kontrol edelim)
        
    #     return None # Anomali yok