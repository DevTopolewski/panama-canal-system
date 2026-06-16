import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "canal_management.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
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

if __name__ == "__main__":
    init_db()