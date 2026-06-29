import sqlite3
import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "canal_management.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Tabela historii statków:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS canal_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            vessel_name TEXT NOT NULL,
            dwt INTEGER NOT NULL,
            status TEXT NOT NULL,
            fee INTEGER NOT NULL
        )
    ''')

    # 2. Tabela cennika:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vessel_rates (
            category TEXT PRIMARY KEY,
            price INTEGER NOT NULL
        )
    """)
    
    # 3. Domyślne stawki, jeśli tabela jest nowa/pusta:
    cursor.execute("SELECT COUNT(*) FROM vessel_rates")
    if cursor.fetchone()[0] == 0:
        default_rates = [
            ("STANDARD", 5000),
            ("PREMIUM", 12000),
            ("NEO-PANAMAX", 25000)
        ]
        cursor.executemany("INSERT INTO vessel_rates (category, price) VALUES (?, ?)", default_rates)
    
    conn.commit()
    conn.close()

# --- DODAWANIE STATKU DO BAZY ---
def add_vessel(timestamp: str, name: str, dwt: int, status: str, fee: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Używamy komendy SQL: INSERT INTO (Wstaw do tabeli)
    # Znak zapytania (?) to bezpieczne "szufladki" na Twoje zmienne
    cursor.execute('''
        INSERT INTO canal_logs (timestamp, vessel_name, dwt, status, fee)
        VALUES (?, ?, ?, ?, ?)
    ''', (timestamp, name, dwt, status, fee))
    
    conn.commit()
    conn.close()
    print(f"Baza danych: Pomyślnie zapisano statek {name}!")

# --- WYCIĄGANIE STATYSTYK Z BAZY ---
def get_vessel_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # COUNT(*) liczy wiersze, SUM(fee) sumuje opłaty
    cursor.execute("SELECT COUNT(*), SUM(fee) FROM canal_logs")
    result = cursor.fetchone()
    conn.close()
    
    total_ships = result[0] if result[0] else 0
    total_earnings = result[1] if result[1] else 0
    return total_ships, total_earnings

# --- WYSZUKIWANIE W BAZIE ---
def search_vessels(query: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # LIKE i znaki % pozwalają na szukanie fragmentu tekstu (np. "posej" znajdzie "Posejdon")
    cursor.execute('''
        SELECT timestamp, vessel_name, dwt, status, fee 
        FROM canal_logs 
        WHERE vessel_name LIKE ?
    ''', (f"%{query}%",))
    
    results = cursor.fetchall()
    conn.close()
    return results

# --- POBIERANIE WSZYSTKICH STATKÓW Z BAZY ---
def get_all_vessels():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # ORDER BY id DESC sprawia, że najnowsze statki będą na samej górze listy
    cursor.execute('''
        SELECT timestamp, vessel_name, dwt, status, fee 
        FROM canal_logs 
        ORDER BY id DESC
    ''')
    
    results = cursor.fetchall()
    conn.close()
    return results

# --- CZYSZCZENIE CAŁEJ BAZY ---
def delete_all_vessels():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Komenda SQL, która czyści całą tabelę, ale zostawia jej strukturę
    cursor.execute("DELETE FROM canal_logs")
    
    conn.commit()
    conn.close()
    print("Baza danych: Wszystkie rekordy zostały usunięte!")

# --- FUNKCJE DO OBSŁUGI CENNIKA W BAZIE ---

def db_load_prices():
    """Pobiera wszystkie stawki z bazy i zwraca je jako słownik."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT category, price FROM vessel_rates")
    rows = cursor.fetchall()
    conn.close()
    
    # Zamieniamy listę z bazy na słownik, np. {"STANDARD": 5000, ...}
    return {row[0]: row[1] for row in rows}

def db_update_price(category, new_price):
    """Aktualizuje cenę dla konkretnej kategorii w bazie danych."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE vessel_rates SET price = ? WHERE category = ?", (new_price, category))
    conn.commit()
    conn.close()

# --- EXPORT HISTORII Z BAZY DANYCH DO PLIKU CSV ---

def export_to_csv():
    """Pobiera wszystkie dane z tabeli canal_logs i zapisuje je do pliku raportu CSV."""
    # Definiujemy ścieżkę do pliku raportu – powstanie w tym samym folderze co baza
    report_path = os.path.join(BASE_DIR, "canal_report.csv")
    
    # 1. Łączymy się z bazą danych
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 2. Wyciągamy WSZYSTKIE kolumny z tabeli historii, sortując od najnowszych
    cursor.execute("SELECT id, timestamp, vessel_name, dwt, status, fee FROM canal_logs ORDER BY id DESC")
    rows = cursor.fetchall()
    
    # 3. Otwieramy plik CSV do zapisu (w trybie 'w' - write, z kodowaniem utf-8)
    # newline='' zapobiega powstawaniu pustych linii między wierszami w niektórych systemach
    with open(report_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # 4. Zapisujemy pierwszy wiersz – nagłówki kolumn (będą widoczne w Excelu)
        writer.writerow(["ID Odprawy", "Data i Czas", "Nazwa Statku", "Waga (DWT)", "Status", "Opłata ($)"])
        
        # 5. Zapisujemy wszystkie wyciągnięte z bazy wiersze
        writer.writerows(rows)
    
    # 6. Zamykamy połączenie z bazą
    conn.close()
    
    # Zwracamy ścieżkę do pliku, żeby GUI mogło wyświetlić użytkownikowi komunikat sukcesu
    return report_path

if __name__ == "__main__":
    init_db()