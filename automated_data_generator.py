import subprocess
import time
import sys

# Tüm senaryoların listesi
SCENARIOS = [
    "ahmet_thermal_manipulation",
    "berat_time_desync",
    "emin_auth_bypass",
    "hasan_session_hijacking",
    "kadir_can_injection",
    # "mahmut_attack_automation", # Mahmut bazen takılıyor, sona saklayalım veya active edelim
    "melik_replay_attack",
    "merve_phantom_current",
    "omer_zero_energy_flood",
    "semih_yetim_seans"
]

ITERATIONS = 3 # Her senaryo 3 kez çalışacak (Veri hacmi için)

def run_cmd(cmd):
    try:
        print(f"🚀 Running: {' '.join(cmd)}")
        # Timeout ile kilitlenmeleri önle
        subprocess.run(cmd, check=True, timeout=90)
    except subprocess.TimeoutExpired:
        print(f"⚠️ TIMEOUT: {cmd}")
    except Exception as e:
        print(f"❌ ERROR: {cmd} -> {e}")

def main():
    print("==========================================")
    print("      AUTOMATED DATA GENERATOR v1.0       ")
    print("==========================================")
    print(f"Scenarios: {len(SCENARIOS)}")
    print(f"Iterations: {ITERATIONS}")
    print("------------------------------------------")

    for i in range(ITERATIONS):
        print(f"\n🌀 === ITERATION {i+1} / {ITERATIONS} === 🌀\n")
        
        for scenario in SCENARIOS:
            print(f"\n🔹 Scenario: {scenario}")
            
            # 1. ATTACK DATA
            print("   ↳ Mode: ATTACK")
            run_cmd(["python", "run_all.py", "--scenario", scenario, "--mode", "attack"])
            
            # Bekleme (Sistem nefes alsın)
            time.sleep(2)
            
            # 2. NORMAL DATA (Eğer destekliyorsa)
            # Bazı senaryolar normal modu desteklemiyor olabilir, loglardan göreceğiz.
            # Normal veriye de ihtiyacımız var.
            print("   ↳ Mode: NORMAL")
            run_cmd(["python", "run_all.py", "--scenario", scenario, "--mode", "normal"])
            
            time.sleep(2)
            
    print("\n✅ DATA GENERATION COMPLETE.")

if __name__ == "__main__":
    main()
