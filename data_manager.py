import os
from datetime import datetime # Pobieramy narzędzie do obsługi dat i czasu
from vessel_logic import check_vessel_status, calculate_vessel_fee, Vessel

# --- SEKCJA KONFIGURACJI ---

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- FUNKCJA: ZAPISYWANIE DANYCH W PLIKU TEKSTOWYM ---
def save_to_log(name: str, dwt: int, status: str, fee: int):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    PATH = os.path.join(BASE_DIR, "canal_log.txt")
    with open(PATH, "a", encoding="utf-8") as file:
        file.write(f"[{now}] | Vessel: {name:<10} | DWT: {dwt:<7} | Status: {status:<19} | Fee: ${fee:>10,}\n")

# --- FUNKCJA: AUTOMATYCZNE LICZENIE Z LISTY ---

def process_batch(vessel_list):
    batch_revenue = 0
    batch_count = 0
    print("\n>>> STARTING AUTOMATIC BATCH PROCESSING...\n")
    for v_data in vessel_list:
        ship = Vessel(v_data["name"], v_data["dwt"])
        fee = ship.get_fee()

        batch_revenue += fee
        batch_count += 1

        save_to_log(ship.name, ship.dwt, ship.category, fee)
        print(f"   [AUTO] {ship.name}: {ship.category} -> {fee}$")
    return batch_revenue, batch_count

# --- FUNKCJA: ANALIZA FUNKCJI Z LISTY I RAPORT ---

def generate_report(vessel_list):
    rejected_count = 0
    processed_count = 0
    report_total_fee = 0

    if not vessel_list:
        print("\n[!] Brak danych do raportu. Najpierw wczytaj JSON (opcja 1).")
        return

    for vessel in vessel_list:
        dwt = vessel["dwt"]
        status = check_vessel_status(dwt)
        fee = calculate_vessel_fee(dwt, status)

        report_total_fee += fee
    
        if status in ["REJECTED", "REJECTED_OVERSIZE", "ERROR_INVALID_VALUE"]:
            rejected_count += 1
        else:
            processed_count += 1
    print("\n" + "="*30)
    print(" FINANCIAL SUMMARY REPORT ")
    print("="*30)
    print(f"Vessels in file: {len(vessel_list)}")
    print(f"Successfully Processed: {processed_count}")
    print(f"Rejected/Errors: {rejected_count }")
    print(f"Total Fees from JSON: ${report_total_fee:,.2f}")
    print("="*30)

# --- FUNKCJA: FINALNY RAPORT STATKÓW DODAWANYCH RĘCZNIE ---

def generate_final_report(fleet):
    FILENAME = os.path.join(BASE_DIR, "final_report.txt")
    now = datetime.now().strftime("%Y-%m-%d")
    try:
        with open(FILENAME, "w", encoding="utf-8") as f:
            f.write("--- PANAMA CANAL: FINAL DUTY REPORT ---\n")
            f.write(f"Report Generated: [{now}]\n")
            f.write("-" * 40 + "\n\n")

            total_revenue = 0

            if not fleet:
                f.write("No vessels handled during this session.\n")
            else:
                for ship in fleet:
                    fee = ship.get_fee()
                    total_revenue += fee
                    f.write(f"NAME: {ship.name:<15} | DWT: {ship.dwt:<10} | CAT: {ship.category:<12} | FEE: ${fee:,}\n")
            f.write("\n" + "-" * 40 + "\n")
            f.write(f"TOTAL VESSELS: {len(fleet)}\n")
            f.write(f"TOTAL REVENUE: ${total_revenue:,}\n")
            f.write("-" * 40 + "\n")
            f.write("End of Report.\n")
        print(f"\n[SUCCESS]: Report saved to {FILENAME}")
    except Exception as e:
        print(f"\n[ERROR]: Could not generate report: {e}")
