import can
import time
from colorama import Fore, Back, init

init(autoreset=True)

def istasyon():
    bus = can.Bus(channel='239.0.0.1', interface='udp_multicast')
    print(Fore.CYAN + "⛽ [İSTASYON] Sistem Hazır. Bekleniyor...")
    
    charging = False
    
    while True:
        msg = bus.recv()
        if msg:
            if msg.arbitration_id == 0x100:
                print(Fore.YELLOW + "🔌 [İSTASYON] Başlat komutu geldi! Röleler açılıyor...")
                charging = True
                for i in range(3):
                    print(Fore.YELLOW + f"   ⚡ Şarj Ediliyor... %{i*10+10}")
                    time.sleep(0.5)
                    # Eğer bu arada STOP gelirse döngüyü kır (basit simülasyon)
                    
            elif msg.arbitration_id == 0x200:
                print(Back.RED + Fore.WHITE + "🛑 [İSTASYON] ACİL DURDURMA EMRİ ALINDI!")
                print(Fore.RED + "   -> Enerji kesildi. Kablo kilitlendi.")
                charging = False

if __name__ == "__main__":
    istasyon()
