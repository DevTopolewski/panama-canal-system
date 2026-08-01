import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import urllib.request
import matplotlib.pyplot as plt
import json
# Importujemy wszystkie potrzebne narzędzia z naszego modułu bazy danych
from database import init_db, add_vessel, get_vessel_stats, search_vessels, get_all_vessels, delete_all_vessels, db_load_prices, db_update_price, export_to_csv, delete_last_entry, get_stats_by_status

# Ładujemy ceny z bazy danych
init_db()
prices = db_load_prices()

# --- FUNKCJA LOGIKA KATEGORYZACJI ---
def check_vessel_status(dwt: int) -> str:
    if dwt <= 0:
        return "ERROR_INVALID_VALUE"
    if dwt > 250000:
        return "REJECTED_OVERSIZE"
    if dwt > 60000:
        return "NEO-PANAMAX"
    elif dwt > 40000:
        return "PREMIUM"
    elif dwt > 10000:
        return "STANDARD"
    else:
        return "REJECTED"

# --- FUNKCJA LOGIKA FINANSOWA ---
def calculate_vessel_fee(dwt: int, category: str) -> int:
    # Opłata bazowa zależna od kategorii
    if category in ["REJECTED", "REJECTED_OVERSIZE", "ERROR_INVALID_VALUE"]:
        return 0
    return prices.get(category, 0)

# --- FUNKCJA GENERUJĄCA WYKRES STATYSTYK
def show_analytics_chart():
    # Pobieramy zagregowane dane z bazy
    stats = get_stats_by_status()
    
    if not stats:
        messagebox.showwarning("Brak danych", "Baza danych jest pusta! Dodaj najpierw jakieś statki.")
        return

    # Rozdzielamy wyniki na dwie osobne listy: statusy i sumy opłat
    statuses = [row[0] for row in stats]
    fees = [row[1] for row in stats]

    # Tworzymy nowe okno wykresu
    plt.figure(figsize=(7, 5))
    
    # Rysujemy wykres słupkowy z ładnymi kolorami
    colors = ['#2ecc71', '#3498db', '#e74c3c', '#f1c40f']
    bars = plt.bar(statuses, fees, color=colors[:len(statuses)])
    
    # Tytuł i opisy osi
    plt.title("Łączne przychody wg statusu statku ($)", fontsize=12, fontweight='bold')
    plt.xlabel("Status statku", fontsize=10)
    plt.ylabel("Suma opłat ($)", fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.5) # Delikatna siatka pomocnicza

    # Dodajemy wartości nad każdym słupkiem
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval, f"${yval:,}", ha='center', va='bottom', fontweight='bold')

    # Wyświetlamy okno z wykresem
    plt.tight_layout()
    plt.show()

# --- FUNKCJA AKTUALIZACJI DASHBOARDU (SQL VERSION) ---
def update_dashboard():
    # Pobieramy gotowe obliczenia prosto z silnika bazy danych
    total_ships, total_earnings = get_vessel_stats()
    stats_label.config(text=f"Obsłużone statki: {total_ships}   |   Zarobek: ${total_earnings:,}")


# --- FUNKCJA WYSZUKIWANIA W LOGACH (SQL VERSION) ---
def search_vessel():
    query = search_entry.get().strip()
    if not query:
        messagebox.showwarning("Brak frazy", "Wpisz nazwę statku do wyszukania!")
        return
    
    # Czyszczenie okna wyników
    search_results_box.config(state="normal")
    search_results_box.delete("1.0", tk.END)
    
    # Pobieramy wyniki wyszukiwania z bazy danych
    rows = search_vessels(query)
                
    if rows:
        for row in rows:
            timestamp, name, dwt, status, fee = row
            # Formatujemy tekst dokładnie tak profesjonalnie, jak chciałeś wcześniej!
            entry_text = f"[{timestamp}] | Vessel: {name:<10} | DWT: {dwt:<7} | Status: {status:<19} | Fee: ${fee:>10,}\n\n"
            search_results_box.insert(tk.END, entry_text)
    else:
        search_results_box.insert(tk.END, f"Nie znaleziono statku o nazwie: '{query}'")
        
    search_results_box.config(state="disabled")

# --- FUNKCJA OBLICZAJĄCA ---
def process_ship():
    name = name_entry.get()
    dwt_raw = dwt_entry.get()
    
    if not name or not dwt_raw:
        messagebox.showwarning("Brak danych", "Wypełnij oba pola!")
        return
        
    try:
        dwt = int(dwt_raw)
        if dwt <= 0:
            messagebox.showerror("Błąd danych", "Waga statku musi być liczbą większą niż 0!")
            return
        status = check_vessel_status(dwt)
        fee = calculate_vessel_fee(dwt, status)
        
        if "REJECTED" in status or "ERROR" in status:
            result_color = "#cc0000"
        else:
            result_color = "#006600"
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            add_vessel(now_str, name, dwt, status, fee)
            # Odświeżamy licznik na dole ekranu automatycznie po dodaniu statku!
            update_dashboard()
            # Czyszczenie pól po udanym zapisie!
            name_entry.delete(0, tk.END)
            dwt_entry.delete(0, tk.END)
        
        result_label.config(
            text=f"STATEK: {name}\nSTATUS: {status}\nOPŁATA: ${fee:,}", 
            fg=result_color
        )
        
    except ValueError:
        messagebox.showerror("Błąd wagi", "DWT musi być liczbą całkowitą!")

# --- USUNIĘCIE OSTATNIO DODANEJ JENOSTKI ---

def undo_last_ship():
    # Pytamy użytkownika, czy na pewno chce usunąć dane (ochrona przed przypadkowym kliknięciem)
    confirm = messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz usunąć OSTATNIO dodany statek z bazy?")
    
    if confirm:
        # Zakładam, że masz zaimportowany moduł bazy jako 'database'
        success = delete_last_entry()
        
        if success:
            # Jeśli usunięto, odświeżamy czarny pasek na górze!
            update_dashboard()
            messagebox.showinfo("Sukces", "Ostatni statek został pomyślnie usunięty z systemu.")
        else:
            messagebox.showwarning("Brak danych", "Baza jest pusta, nie ma czego usunąć!")

# --- WYŚWIETLANIE CAŁEJ HISTORII ---
def show_all_vessels():
    search_results_box.config(state="normal")
    search_results_box.delete("1.0", tk.END)

    rows = get_all_vessels()

    if rows:
        for row in rows:
            timestamp, name, dwt, status, fee = row
            entry_text = f"[{timestamp}] | Vessel: {name:<10} | DWT: {dwt:<7} | Status: {status:<19} | Fee: ${fee:>10,}\n\n"
            search_results_box.insert(tk.END, entry_text)
    else:
        search_results_box.insert(tk.END, "Baza danych jest pusta. Dodaj jakieś statki!")

    search_results_box.config(state="disabled")

# --- RESETOWANIE BAZY Z POTWIERDZENIEM ---
def reset_database():
    # Wyskakujące okienko z pytaniem Tak/Nie (True/False)
    confirm = messagebox.askyesno("⚠️ POTWIERDZENIE", "Czy na pewno chcesz BEZPOWROTNIE usunąć całą historię statków?")

    if confirm: # Jeśli użytkownik kliknął TAK
        delete_all_vessels()     # Czyścimy bazę SQL
        update_dashboard()       # Wyzerują nam się statystyki na dole

        # Czyszczenie i zablokowanie okna wyszukiwarki
        search_results_box.config(state="normal")
        search_results_box.delete("1.0", tk.END)
        search_results_box.insert(tk.END, "Baza danych została zresetowana.")
        search_results_box.config(state="disabled")

        messagebox.showinfo("Sukces", "Baza danych została pomyślnie wyczyszczona!")

def handle_save_rates():
    global prices
    try:
        new_standard = int(rate_standard_entry.get())
        new_premium = int(rate_premium_entry.get())
        new_neo = int(rate_neo_entry.get())
        
        if new_standard <= 0 or new_premium <= 0 or new_neo <= 0:
            messagebox.showerror("Błąd", "Ceny muszą być większe od 0!")
            return
            
        # Zapisujemy wartości bezpośrednio do SQLite
        db_update_price("STANDARD", new_standard)
        db_update_price("PREMIUM", new_premium)
        db_update_price("NEO-PANAMAX", new_neo)
        
        # Przeładowujemy słownik w locie z bazy danych
        prices = db_load_prices()
        
        messagebox.showinfo("Sukces", "Cennik został zaktualizowany w bazie SQL!")
    except ValueError:
        messagebox.showerror("Błąd", "Wprowadź poprawne liczby całkowite!")

def update_clock():
    # Pobieramy aktualną datę i czas w ładnym formacie RRRR-MM-DD HH:MM:SS
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Aktualizujemy tekst w naszym labelu
    time_label.config(text=f"{current_time}")
    # 🔥 MAGIA: prosimy Tkintera, żeby odpalił tę funkcję ponownie za 1 sekundę
    root.after(1000, update_clock)

def download_rate_usd():
    url = "http://api.nbp.pl/api/exchangerates/rates/a/usd/?format=json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data['rates'][0]['mid']
    except Exception:
        return None

def trigger_export():
    try:
        report_file = export_to_csv()
        messagebox.showinfo(
            "Raport Wygenerowany", 
            f"🚀 Sukces!\n\nStatystyki Kanału zostały zapisane do pliku Excel/CSV.\n\nLokalizacja:\n{report_file}"
        )
    except Exception as e:
        # W razie jakiegokolwiek problemu program nie skraszuje, tylko pokaże błąd
        messagebox.showerror("Błąd Eksportu", f"Coś poszło nie tak podczas zapisu pliku:\n{e}")

# --- TWORZENIE GŁÓWNEGO OKNA ---
root = tk.Tk()
root.title("Panama Canal System v2.4 (SQL)")
root.geometry("400x850")

BG_COLOR = "#003366"   
TEXT_COLOR = "#FFFFFF" 
root.configure(bg=BG_COLOR)

# --- 🔥 NOWOŚĆ: KONFIGURACJA STYLU PRZYCISKÓW ---
style = ttk.Style()
style.theme_use('clam')  # Wymuszamy posłuszny motyw 'clam'

# Tworzymy niestandardowy styl dla naszych przycisków
style.configure(
    "Custom.TButton",
    background="#005588",      # Morski kolor przycisku
    foreground="#FFFFFF",      # Biały tekst
    font=("Arial", 11, "bold"),
    borderwidth=0,
    focuscolor="none"          # To zabija białe mruganie na Macu
)

# Definiujemy, co ma się stać, gdy najedziemy myszką (hover)
style.map("Custom.TButton",
    background=[("active", "#004477")]  # Ciemniejszy niebieski po najechaniu
)

# --- SEKCJA 1: CZARNY PASEK STATYSTYK (DASHBOARD) ---
stats_frame = tk.Frame(root, bg="#000000", height=40)
stats_frame.pack(fill="x", side="top")

stats_label = tk.Label(stats_frame, text="Ładowanie...", font=("Arial", 11, "bold"), bg="#000000", fg="#FFFFFF")
stats_label.pack(pady=10)

# --- SEKCJA 2: DYNAMICZNY ZEGAR SYSTEMOWY ---
# Tworzymy małą ramkę pod czarnym paskiem
time_frame = tk.Frame(root, bg=BG_COLOR)
# side="top" sprawi, że wskoczy idealnie pod czarny pasek statystyk
time_frame.pack(fill="x", side="top", pady=5)

time_label = tk.Label(time_frame, text="", font=("Arial", 10, "bold"), bg=BG_COLOR, fg="#555555")
time_label.pack()

# 2. NOWOŚĆ: Napis z kursem USD z API NBP
usd_label = tk.Label(time_frame, text="💵 Pobieranie kursu USD...", font=("Arial", 9, "italic"), bg=BG_COLOR, fg="#2980b9")
usd_label.pack(pady=(2, 0))

# Odpalamy pierwsze odświeżenie zegara
update_clock()

# 🚀 POBRANIE KURSU Z API PRZY STARCIE:
aktualny_kurs = download_rate_usd()
if aktualny_kurs:
    usd_label.config(text=f"💵 Kurs USD (NBP): {aktualny_kurs} PLN", font=("Arial", 9, "bold"), fg="#27ae60")
else:
    usd_label.config(text="💵 Kurs USD: Brak połączenia z siecią", fg="#c0392b")

# --- SEKCJA 3: ODPRAWA STATKÓW ---
title = tk.Label(root, text="Kalkulator Kanału Panamskiego", font=("Arial", 14, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
title.pack(pady=15)

name_label = tk.Label(root, text="Nazwa statku:", font=("Arial", 11, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
name_label.pack(pady=2)
name_entry = tk.Entry(root, width=25, font=("Arial", 12), bg="#F0F0F0", fg="#000000", insertbackground="black")
name_entry.pack(pady=5)

dwt_label = tk.Label(root, text="Waga statku (DWT):", font=("Arial", 11, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
dwt_label.pack(pady=2)
dwt_entry = tk.Entry(root, width=25, font=("Arial", 12), bg="#F0F0F0", fg="#000000", insertbackground="black")
dwt_entry.pack(pady=5)

calc_button = ttk.Button(root, text="Odpraw statek 🚢", command=process_ship, style="Custom.TButton")
calc_button.pack(pady=15)

result_label = tk.Label(root, text="Wpisz dane i kliknij przycisk powyżej.", font=("Courier", 11, "bold"), bg=BG_COLOR, fg="#000000", justify="left")
result_label.pack(pady=10)

action_buttons_frame = tk.Frame(root, bg=BG_COLOR)
action_buttons_frame.pack(pady=15)

undo_button = ttk.Button(
    action_buttons_frame, 
    text="Cofnij Ostatnio Dodany Statek ↩️", 
    command=undo_last_ship, 
    style="Custom.TButton"
)
undo_button.pack(side="left", padx=10) 

chart_button = ttk.Button(
    action_buttons_frame, 
    text="Generuj Wykres Analityczny 📊", 
    command=show_analytics_chart, 
    style="Custom.TButton"
)
chart_button.pack(side="left", padx=10)

# --- LINIA PODZIAŁU SYSTEMU ---
separator = tk.Frame(root, height=2, bd=1, relief="sunken", bg="#000000")
separator.pack(fill="x", padx=20, pady=10)

# --- SEKCJA 4: WYSZUKIWARKA LOGÓW ---
search_title = tk.Label(root, text="Wyszukiwarka Logów SQL", font=("Arial", 12, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
search_title.pack(pady=5)

search_entry = tk.Entry(root, width=25, font=("Arial", 12), bg="#F0F0F0", fg="#000000", insertbackground="black")
search_entry.pack(pady=5)

search_button = ttk.Button(root, text="Szukaj w bazie 🔍", command=search_vessel, style="Custom.TButton")
search_button.pack(pady=5)

show_all_button = ttk.Button(root, text="Pokaż całą historię 📜", command=show_all_vessels, style="Custom.TButton")
show_all_button.pack(pady=2)

search_results_box = tk.Text(root, width=45, height=5, font=("Courier", 10), bg="#F0F0F0", fg="#000000", state="disabled")
search_results_box.pack(pady=10, padx=15)

reset_button = ttk.Button(root, text="Resetuj bazę danych ⚠️", command=reset_database, style="Custom.TButton")
reset_button.pack(pady=10)

# --- SEKCJA: EKSPORT RAPORTÓW BIZNESOWYCH ---
export_button = ttk.Button(root, text="Generuj Raport Operacyjny (CSV) 📥", command=trigger_export, style="Custom.TButton")
export_button.pack(pady=10)

# --- LINIA PODZIAŁU SYSTEMU ---
separator = tk.Frame(root, height=2, bd=1, relief="sunken", bg="#000000")
separator.pack(fill="x", padx=20, pady=10)

# --- SEKCJA 4: KONFIGURACJA STAWEK ---
rates_label = tk.Label(root, text="Konfiguracja stawek SQL ($)", font=("Arial", 11, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
rates_label.pack(pady=5)

rates_frame = tk.Frame(root, bg=BG_COLOR)
rates_frame.pack(pady=5)

# Pole STANDARD
tk.Label(rates_frame, text="Std:", bg=BG_COLOR, fg=TEXT_COLOR, font=("Arial", 10, "bold")).grid(row=0, column=0, padx=2)
rate_standard_entry = tk.Entry(rates_frame, width=6, font=("Arial", 10))
rate_standard_entry.insert(0, str(prices.get("STANDARD", 5000)))
rate_standard_entry.grid(row=0, column=1, padx=4)

# Pole PREMIUM
tk.Label(rates_frame, text="Prem:", bg=BG_COLOR, fg=TEXT_COLOR, font=("Arial", 10, "bold")).grid(row=0, column=2, padx=2)
rate_premium_entry = tk.Entry(rates_frame, width=6, font=("Arial", 10))
rate_premium_entry.insert(0, str(prices.get("PREMIUM", 12000)))
rate_premium_entry.grid(row=0, column=3, padx=4)

# Pole NEO-PANAMAX
tk.Label(rates_frame, text="Neo:", bg=BG_COLOR, fg=TEXT_COLOR, font=("Arial", 10, "bold")).grid(row=0, column=4, padx=2)
rate_neo_entry = tk.Entry(rates_frame, width=6, font=("Arial", 10))
rate_neo_entry.insert(0, str(prices.get("NEO-PANAMAX", 25000)))
rate_neo_entry.grid(row=0, column=5, padx=4)

# Przycisk zapisu (ttk)
save_rates_button = ttk.Button(root, text="Zapisz stawki w SQL 💾", command=handle_save_rates, style="Custom.TButton")
save_rates_button.pack(pady=5)

# Odpalamy pierwsze wyliczenie statystyk z bazy danych na starcie!
update_dashboard()

root.mainloop()