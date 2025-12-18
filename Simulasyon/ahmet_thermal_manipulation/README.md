# ahmet - thermal_manipulation simulation module

# Otonom Araç Kamera Parlaması ve Veri Gürültüsü

Bu senaryo, otonom aracın kamerasının ani ve yoğun ışık parlamasına (glare) maruz kalması sonucu oluşan veri bozulmasını ve gürültülü (noisy) veri iletimini simüle eder.

## 📌 Senaryo Amacı
Dış kaynaklı ışık manipülasyonu veya çevresel faktörler (güneş parlaması) nedeniyle sensör verileri bozulur. Şarj istasyonuna gönderilen voltaj ve enerji verilerinde ani, gerçekçi olmayan sıçramalar (spikes) ve dalgalanmalar gözlemlenir.

## 🛠 Teknik Detaylar
* **Senaryo Adı:** `sensor_glare_noise_injection`
* **ChargePoint ID:** `CP_GLARE_01`
* **Model:** `Auto_Glare_Test`
* **Anomali Tipi:** Veri Bütünlüğü Bozulması / Gürültülü Veri (Noise Injection)

## 🔄 Akış Adımları
1.  **BootNotification:** CSMS ile bağlantı kurulur.
2.  **StartTransaction:** Şarj işlemi başlar.
3.  **MeterValues (Anomalili):**
    * Voltaj değerleri 220V standardının dışına çıkarak rastgele dalgalanır (+/- 50V).
    * Enerji verisinde ani ve mantıksız sıçramalar (Örn: 9999.9 Wh) gönderilir.
4.  **StopTransaction:** Güvenli mod gereği işlem sonlandırılır (`reason="Other"`).
5.  **StatusNotification:** Geçici bir çevresel faktör olduğu için istasyon `Faulted` yerine tekrar `Available` moduna döner.

## 🚀 Nasıl Çalıştırılır?
1.  Önce ana motorun (CSMS) çalıştığından emin olun: `python csms.py`
2.  Senaryoyu başlatın:
    ```bash
    python scenario.py
    ```

# Otonom Araç Sensör Füzyonu Tutarsızlığı (Hayalet Nesne)

Bu senaryo, otonom aracın şarj istasyonuna bağlıyken çevresel algılama sensörlerinde (Kamera ve LiDAR) meydana gelen tutarsızlık durumunu simüle eder.

## 📌 Senaryo Amacı
Araç şarj olurken kamera "engel var" verisi üretirken, Radar/LiDAR "alan boş" verisi üretmektedir. Bu "Sensör Füzyonu Tutarsızlığı" (Phantom Object), aracın güvenlik protokollerini tetikler ve şarj işlemi acil olarak durdurulur.

## 🛠 Teknik Detaylar
* **Senaryo Adı:** `sensor_fusion_mismatch_phantom_obj`
* **ChargePoint ID:** `CP_OTONOM_01`
* **Model:** `Auto_EV_Charger`
* **Anomali Tipi:** Sensör Uyuşmazlığı / Acil Duruş (EmergencyStop)

## 🔄 Akış Adımları
1.  **BootNotification:** CSMS ile bağlantı kurulur ve cihaz kendini tanıtır.
2.  **StartTransaction:** Şarj işlemi normal prosedürle başlar.
3.  **MeterValues (Normal):** İlk 3 veri paketi normal enerji akışını gösterir.
4.  **ANOMALİ TETİKLENMESİ:** Senaryo gereği "Hayalet Nesne" algılanır.
5.  **StopTransaction:** Araç `reason="EmergencyStop"` kodu ile işlemi derhal keser.
6.  **StatusNotification:** İstasyon durumu `Faulted` (Arızalı) olarak bildirilir ve `info="SensorAnomaly_PhantomObject"` detayı geçilir.

## 🚀 Nasıl Çalıştırılır?
1.  Önce ana motorun (CSMS) çalıştığından emin olun: `python csms.py`
2.  Senaryoyu başlatın:
    ```bash
    python scenario.py
    ```
