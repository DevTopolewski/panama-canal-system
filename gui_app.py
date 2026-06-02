import os
import tkinter as tk
from tkinter import messagebox
# Importujemy Twoje funkcje z pliku vessel_logic.py
from vessel_logic import check_vessel_status, calculate_vessel_fee

# Ustawiamy katalog bazowy projektu
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- FUNKCJA OBLICZAJĄCA (MÓZG PRZYCISKU) ---
def process_ship():
    # Pobieramy tekst wpisany przez użytkownika
    name = name_entry.get()
    dwt_raw = dwt_entry.get()
    
    # Walidacja pustych pól
    if not name or not dwt_raw:
        messagebox.showwarning("Brak danych", "Wypełnij oba pola, Pedro!")
        return
        
    try:
        dwt = int(dwt_raw) # Zamiana tekstu na liczbę
        
        # Wywołanie Twojej logiki
        status = check_vessel_status(dwt)
        fee = calculate_vessel_fee(dwt, status)
        
        # Ustawiamy bezpieczne, ciemne kolory dla wyników (wysoki kontrast)
        if "REJECTED" in status or "ERROR" in status:
            result_color = "#cc0000" # Ciemnoczerwony
        else:
            result_color = "#006600" # Ciemnozielony
        
        # Wyświetlamy wynik na ekranie
        result_label.config(
            text=f"STATEK: {name}\nSTATUS: {status}\nOPŁATA: ${fee:,}", 
            fg=result_color
        )
        
    except ValueError:
        # Poprawione na showerror (wcześniej był błąd w nazwie funkcji)
        messagebox.showerror("Błąd wagi", "DWT musi być liczbą całkowitą!")

# --- TWORZENIE GŁÓWNEGO OKNA ---
root = tk.Tk()
root.title("Panama Canal Calculator v2.0")
root.geometry("400x400")

# --- WYMUSZENIE WYSOKIEGO KONTRASTU (Niezależnie od Dark Mode na Macu) ---
BG_COLOR = "#FFFFFF"   # Wymuszamy czyste białe tło dla okna i etykiet
TEXT_COLOR = "#000000" # Wymuszamy głęboką czerń dla napisów

root.configure(bg=BG_COLOR)

# --- ELEMENTY INTERFEJSU ---

# 1. Tytuł główny
title = tk.Label(root, text="Kalkulator Kanału Panamskiego", font=("Arial", 16, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
title.pack(pady=15)

# 2. Pole: Nazwa statku
name_label = tk.Label(root, text="Nazwa statku:", font=("Arial", 11, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
name_label.pack(pady=2)
name_entry = tk.Entry(root, width=25, font=("Arial", 12), bg="#F0F0F0", fg="#000000", insertbackground="black")
name_entry.pack(pady=5)

# 3. Pole: Waga (DWT)
dwt_label = tk.Label(root, text="Waga statku (DWT):", font=("Arial", 11, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
dwt_label.pack(pady=2)
dwt_entry = tk.Entry(root, width=25, font=("Arial", 12), bg="#F0F0F0", fg="#000000", insertbackground="black")
dwt_entry.pack(pady=5)

# 4. Przycisk "Odpraw statek"
# Używamy highlightbackground, żeby zmusić macOS do poprawnego wyświetlenia przycisku na białym tle
calc_button = tk.Button(
    root, 
    text="Odpraw statek 🚢", 
    font=("Arial", 12, "bold"), 
    command=process_ship,
    fg="#000000",
    highlightbackground=BG_COLOR
)
calc_button.pack(pady=20)

# 5. Miejsce na wynik (początkowy komunikat)
result_label = tk.Label(
    root, 
    text="Wpisz dane i kliknij przycisk powyżej.", 
    font=("Courier", 12, "bold"), 
    bg=BG_COLOR, 
    fg="#555555", # Czytelny, ciemnoszary kolor startowy
    justify="left"
)
result_label.pack(pady=15)

# Uruchomienie pętli programu
root.mainloop()