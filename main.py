import json
from vessel_logic import check_vessel_status, calculate_vessel_fee, update_price, Vessel
from data_manager import save_to_log, process_batch, generate_report, generate_final_report

# Counters 
session_total_revenue = 0
session_ships_count = 0
active_fleet = []

# --- FUNKCJA 6: MENU GŁÓWNE ---

def main_menu():
    
    global session_total_revenue, session_ships_count, active_fleet_count, active_fleet
    night_vessels = []

    while True:
        
        print("\n--- PANAMA CANAL MANAGMENT SYSTEM v2.0 ---\n")
        print(f"STATYSTYKI SESJI: Statki: {session_ships_count} | Kasa: ${session_total_revenue:,}")
        print("-" * 42)
        print("1. Przetwórz paczkę statków (JSON)")
        print("2. Dodaj statek ręcznie (MANUAL)")
        print("3. Wyświetl raport z ostatniego JSONa")
        print("4. Wyświetl liste statków dodanych manualnie")
        print("5. Zamknij system")
        print("6. Aktualizaja stawek")
        print("7. Usuń statek dodany ręcznie z listy.")
        print("8. Save final daily report in the file.")

        choice = input("\nWybierz opcję (1-8): ")

        if choice == "1":
            json_path = "/Users/pedro/Desktop/ships.json"
            try:
                with open(json_path, "r", encoding="utf-8") as file:
                    night_vessels = json.load(file)
                    rev, count = process_batch(night_vessels)
                    session_total_revenue += rev
                    session_ships_count += count
            except FileNotFoundError:
                print("Błąd: Nie znaleziono pliku ships.json!")

        elif choice == "2":

            while True:
                v_name = input("\nEnter vessel name (or 'exit'): ")

                if v_name.lower() == 'exit':
                    break # To kończy pętlę

                user_input = input(f"Enter DWT for {v_name}: ")

                try:
                    dwt = int(user_input)
                    ship = Vessel(v_name, dwt)
                    active_fleet.append(ship)
                    print(f"Successfully added: {ship}")
                    fee = ship.get_fee()
                    session_total_revenue += fee
                    session_ships_count += 1
                    print(f"Fee calculated: ${fee:,}")
                    save_to_log(ship.name, ship.dwt, ship.category, fee)
                    print("Log saved to canal_log.txt")

                except ValueError as e:
                    # To się wykona, jeśli użytkownik wpisze litery zamiast cyfr
                    print(f"\n[ENTRY ERROR]: {e}")

        elif choice == "3":
            generate_report(night_vessels)

        elif choice == "4":
            print("\n--- FLEET VIEW OPTIONS ---")
            print("1. Show all vessels")
            print("2. Filter by category (STANDARD/PREMIUM/NEO-PANAMAX)")
            sub_choice = input("Select choice: ")
            if sub_choice == "1":
                print("\n--- CURRENT SESSION FLEET ---")
                if not active_fleet:
                    print("Fleet is empty.")
                else:
                    for s in active_fleet:
                        print(s)
                    print(f"Total ships in fleet: {len(active_fleet)}")
                print("-" * 29)
            elif sub_choice == "2":
                 target_cat = input("Enter category to filter: ").upper()
                 filtered_list = [s for s in active_fleet if s.category == target_cat]
                 print(f"\n--- {target_cat} VESSELS ---")
                 if not filtered_list:
                     print(f"No vessels found in category: {target_cat}")
                 else:
                     for s in filtered_list:
                         print(s)
                     print(f"Total found: {len(filtered_list)}")
                 print("-" * 29)
        
        elif choice == "5":
            print(f"\nZamykanie systemu. Dzisiejszy utarg: ${session_total_revenue}. Do widzenia!")
            break

        elif choice == "6":
            cat = input("\nEnter category: (STANDARD/PREMIUM/NEO-PANAMAX): ")
            try:
                new_val = int(input("Enter new price: "))
                if update_price(cat, new_val):
                    print("\nPrice-list updated!")
                else:
                    print("\nError: Wrong category or price!")
            except ValueError:
                print("\nBłąd: Price must be a numer!")

        elif choice == "7":
            name_to_remove = input("\nEnter the name of the vessel to remove: ")
            initial_count = len(active_fleet)
            active_fleet = [s for s in active_fleet if s.name.lower() != name_to_remove.lower()]
            if len(active_fleet) < initial_count:
                print(f"\nSUCCESS: Vesel '{name_to_remove}' has been removed.")
            else:
                print(f"\nERROR: Vessel '{name_to_remove}' not found in current fleet.")

        elif choice == "8":
            generate_final_report(active_fleet)
                
        else:
            print("\nBłąd! Select an option (1-5).")

if __name__ == "__main__":
    main_menu()