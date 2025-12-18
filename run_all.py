import argparse
import importlib
import sys
import os

def list_scenarios():
    """
    Simulasyon/ klasöründeki mevcut senaryoları otomatik listeler.
    core/ klasörü ve __pycache__ filtrelenir.
    """
    base_dir = os.path.join(os.path.dirname(__file__), "Simulasyon")
    scenarios = []

    for item in os.listdir(base_dir):
        full_path = os.path.join(base_dir, item)
        if os.path.isdir(full_path) and item not in ["core", "__pycache__"]:
            scenarios.append(item)

    return scenarios


def main():
    parser = argparse.ArgumentParser(
        description="EVSE Security Lab – Senaryo Koşucu"
    )

    parser.add_argument(
        "--scenario",
        required=True,
        help="Çalıştırılacak senaryonun klasör adı (örn: semih_yetim_seans)"
    )

    parser.add_argument(
        "--mode",
        default="normal",
        choices=["normal", "attack"],
        help="Senaryo modu: normal / attack"
    )

    args = parser.parse_args()

    # Mevcut senaryoları otomatik al
    available_scenarios = list_scenarios()

    if args.scenario not in available_scenarios:
        print("\n❌ HATA: Böyle bir senaryo bulunamadı:", args.scenario)
        print("\n📌 Mevcut senaryolar:")
        for s in available_scenarios:
            print("  -", s)
        print("\nSenaryo klasörünü 'Simulasyon/<senaryo_adı>/' şeklinde eklemeniz gerekir.")
        sys.exit(1)

    # Senaryonun scenario.py dosyasını import et
    module_path = f"Simulasyon.{args.scenario}.scenario"

    try:
        scenario_module = importlib.import_module(module_path)
    except Exception as e:
        print("\n❌ Senaryo import edilirken hata oluştu!")
        print("Modül yolu:", module_path)
        print("Hata:", e)
        sys.exit(1)

    # Çalıştırılacak fonksiyon mevcut mu?
    if not hasattr(scenario_module, "run_scenario"):
        print(f"\n❌ HATA: {args.scenario}/scenario.py içinde 'run_scenario' fonksiyonu bulunamadı!")
        print("Lütfen dosyada aşağıdaki fonksiyon tanımlı olsun:")
        print("\n   def run_scenario(mode):\n")
        sys.exit(1)

    print("\n🚀 Senaryo başlatılıyor...")
    print(f"👉 Senaryo: {args.scenario}")
    print(f"👉 Mod: {args.mode}\n")

    # Senaryoyu çalıştır
    try:
        scenario_module.run_scenario(args.mode)
    except Exception as e:
        print("\n❌ Senaryo çalıştırılırken hata oluştu!")
        print("Hata:", e)
        sys.exit(1)


if __name__ == "__main__":
    main()