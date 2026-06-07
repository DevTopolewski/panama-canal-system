import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
# Importujemy Twoje funkcje z pliku vessel_logic.py
from vessel_logic import check_vessel_status, calculate_vessel_fee

# Ustawiamy katalog bazowy projektu i globalną ścieżkę do logów
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE_PATH = os.path.join(BASE_DIR, "canal_log.txt")

# --- FUNKCJA ZAPISU DO PLIKU TEKSTOWEGO ---
def save_to_log(name: str, dwt: int, status: str, fee: int):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as file:
        file.write(f"[{now}] | Vessel: {name:<10} | DWT: {dwt:<7} | Status: {status:<19} | Fee: ${fee:>10,}\n")


# --- FUNKCJA WYSZUKIWANIA W LOGACH ---
def search_vessel():
    query = search_entry.get().strip() # Pobieramy szukaną frazę
    
    if not query:
        messagebox.showwarning("Brak frazy", "Wpisz nazwę statku do wyszukania, Pedro!")
        return
    
    # Czyszczenie pola tekstowego z poprzednich wyników
    search_results_box.config(state="normal")
    search_results_box.delete("1.0", tk.END)
    
    if not os.path.exists(LOG_FILE_PATH):
        search_results_box.insert(tk.END, "Brak pliku logów. Najpierw dodaj jakiś statek.")
        search_results_box.config(state="disabled")
        return

    found_entries = []
    
    # Przeszukiwanie pliku linia po linii
    with open(LOG_FILE_PATH, "r", encoding="utf-8") as file:
        for line in file:
            # Szukamy bez względu na małe/duże litery
            if query.lower() in line.lower():
                found_entries.append(line.strip())
                
    # Wyświetlanie wyników w oknie
    if found_entries:
        for entry in found_entries:
            search_results_box.insert(tk.END, entry + "\n\n")
    else:
        search_results_box.insert(tk.END, f"Nie znaleziono statku o nazwie: '{query}'")
        
    search_results_box.config(state="disabled") # Blokujemy edycję pola przez użytkownika


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
            save_to_log(name, dwt, status, fee)
        
        result_label.config(
            text=f"STATEK: {name}\nSTATUS: {status}\nOPŁATA: ${fee:,}", 
            fg=result_color
        )
        
    except ValueError:
        messagebox.showerror("Błąd wagi", "DWT musi być liczbą całkowitą!")

# --- TWORZENIE GŁÓWNEGO OKNA ---
root = tk.Tk()
root.title("Panama Canal Calculator v2.2")
root.geometry("400x650") # Zwiększone okno z 400x400 na 400x650, żeby zmieścić wyszukiwarkę

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

calc_button = tk.Button(
    root, 
    text="Odpraw statek 🚢", 
    font=("Arial", 12, "bold"), 
    command=process_ship,
    fg="#000000",
    highlightbackground=BG_COLOR
)
calc_button.pack(pady=15)

result_label = tk.Label(
    root, 
    text="Wpisz dane i kliknij przycisk powyżej.", 
    font=("Courier", 11, "bold"), 
    bg=BG_COLOR, 
    fg="#555555", 
    justify="left"
)
result_label.pack(pady=10)

# --- LINIA PODZIAŁU SYSTEMU (WIZUALNA) ---
separator = tk.Frame(root, height=2, bd=1, relief="sunken", bg="#CCCCCC")
separator.pack(fill="x", padx=20, pady=15)

# --- SEKCJA 2: WYSZUKIWARKA LOGÓW ---
search_title = tk.Label(root, text="Wyszukiwarka Logów", font=("Arial", 12, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
search_title.pack(pady=5)

search_entry = tk.Entry(root, width=25, font=("Arial", 12), bg="#F0F0F0", fg="#000000", insertbackground="black")
search_entry.pack(pady=5)

search_button = tk.Button(
    root, 
    text="Szukaj w logach 🔍", 
    font=("Arial", 12, "bold"), 
    command=search_vessel, 
    fg="#000000", 
    highlightbackground=BG_COLOR
)
search_button.pack(pady=5)

# Okno tekstowe na wyniki wyszukiwania
search_results_box = tk.Text(root, width=45, height=6, font=("Courier", 10), bg="#F9F9F9", fg="#000000", state="disabled")
search_results_box.pack(pady=10, padx=15)

# Uruchomienie pętli programu
root.mainloop()