import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from vessel_logic import check_vessel_status, calculate_vessel_fee
# Importujemy wszystkie potrzebne narzędzia z naszego modułu bazy danych
from database import add_vessel, get_vessel_stats, search_vessels, get_all_vessels, delete_all_vessels

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
        
        result_label.config(
            text=f"STATEK: {name}\nSTATUS: {status}\nOPŁATA: ${fee:,}", 
            fg=result_color
        )
        
    except ValueError:
        messagebox.showerror("Błąd wagi", "DWT musi być liczbą całkowitą!")

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

# --- TWORZENIE GŁÓWNEGO OKNA ---
root = tk.Tk()
root.title("Panama Canal System v2.4 (SQL)")
root.geometry("400x700")

BG_COLOR = "#FFFFFF"   
TEXT_COLOR = "#000000" 
root.configure(bg=BG_COLOR)

# --- SEKCJA 1: ODPRAWA STATKÓW ---
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

calc_button = tk.Button(root, text="Odpraw statek 🚢", font=("Arial", 12, "bold"), command=process_ship, fg="#000000", highlightbackground=BG_COLOR)
calc_button.pack(pady=15)

result_label = tk.Label(root, text="Wpisz dane i kliknij przycisk powyżej.", font=("Courier", 11, "bold"), bg=BG_COLOR, fg="#555555", justify="left")
result_label.pack(pady=10)

# --- LINIA PODZIAŁU SYSTEMU ---
separator = tk.Frame(root, height=2, bd=1, relief="sunken", bg="#CCCCCC")
separator.pack(fill="x", padx=20, pady=10)

# --- SEKCJA 2: WYSZUKIWARKA LOGÓW ---
search_title = tk.Label(root, text="Wyszukiwarka Logów SQL", font=("Arial", 12, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
search_title.pack(pady=5)

search_entry = tk.Entry(root, width=25, font=("Arial", 12), bg="#F0F0F0", fg="#000000", insertbackground="black")
search_entry.pack(pady=5)

search_button = tk.Button(root, text="Szukaj w bazie 🔍", font=("Arial", 12, "bold"), command=search_vessel, fg="#000000", highlightbackground=BG_COLOR)
search_button.pack(pady=5)

show_all_button = tk.Button(root, text="Pokaż całą historię 📜", font=("Arial", 12, "bold"), command=show_all_vessels, fg="#000000", highlightbackground=BG_COLOR)
show_all_button.pack(pady=2)

search_results_box = tk.Text(root, width=45, height=5, font=("Courier", 10), bg="#F9F9F9", fg="#000000", state="disabled")
search_results_box.pack(pady=10, padx=15)

# 🔥 TUTAJ WCISKASZ CZERWONY PRZYCISK RESETU:
reset_button = tk.Button(root, text="Resetuj bazę danych ⚠️", font=("Arial", 11, "bold"), command=reset_database, fg="#cc0000", highlightbackground=BG_COLOR)
reset_button.pack(pady=10)

# --- SEKCJA 3: CZARNY PASEK STATYSTYK (DASHBOARD) ---
stats_frame = tk.Frame(root, bg="#000000", height=40)
stats_frame.pack(fill="x", side="bottom")

stats_label = tk.Label(stats_frame, text="Ładowanie...", font=("Arial", 11, "bold"), bg="#000000", fg="#FFFFFF")
stats_label.pack(pady=10)

# Odpalamy pierwsze wyliczenie statystyk z bazy danych na starcie!
update_dashboard()

root.mainloop()