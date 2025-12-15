# EVSE Güvenlik Lab: Enerji Ölçüm Verisi Manipülasyonu

Bu senaryo, şarj noktası simülatörünün (Charge Point), merkezi sisteme (CSMS) gönderdiği MeterValues ve StopTransaction mesajlarındaki enerji tüketim verilerini kasten düşük raporlamasını simüle eder.

Bu durum, CPO (Charge Point Operator) için **enerji hırsızlığına bağlı gelir kaybına** yol açar.

## 1. Normal Akış (Detection Baseline)

| Mesaj | Açıklama |
| :--- | :--- |
| **StartTransaction** | Şarj başlar. |
| **MeterValues** | Sayaç değeri her adımda **0.1 kWh** artar. |
| **StopTransaction** | Sayaç, toplam **0.5 kWh** değeriyle durur. |

## 2. Anomali Akışı (Saldırı)

Bu akış, normal akışın üzerine eklenir.

| Mesaj | Açıklama | Anomali Tespiti |
| :--- | :--- | :--- |
| **StartTransaction** | Şarj başlar. | - |
| **MeterValues** | Gerçekte **0.5 kWh** enerji harcanırken, raporlanan sayaç değeri her adımda sadece **0.1 kWh** artar. | [cite_start]**Beklenenden düşük kWh raporu** (Dashbord Kuralı: Kural-1 ihlali) [cite: 249] |
| **StopTransaction** | Şarj işlemi **0.5 kWh** değeriyle sonlandırılır, oysa gerçek tüketim **2.5 kWh**'dir. | CSMS tarafından beklenen tüketim/süre oranı ihlali. |
