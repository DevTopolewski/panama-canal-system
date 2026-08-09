import sqlite3
import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "canal_management.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Vessel history table:
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

    # 2. Rates table:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vessel_rates (
            category TEXT PRIMARY KEY,
            price INTEGER NOT NULL
        )
    """)
    
    # 3. Default rates if the table is new/empty:
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

# --- ADDING A VESSEL TO THE DATABASE ---
def add_vessel(timestamp: str, name: str, dwt: int, status: str, fee: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Using SQL command: INSERT INTO
    # Question marks (?) are safe placeholders for your variables
    cursor.execute('''
        INSERT INTO canal_logs (timestamp, vessel_name, dwt, status, fee)
        VALUES (?, ?, ?, ?, ?)
    ''', (timestamp, name, dwt, status, fee))
    
    conn.commit()
    conn.close()
    print(f"Database: Successfully saved vessel {name}!")

# --- FETCHING STATISTICS FROM DATABASE ---
def get_vessel_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # COUNT(*) counts rows, SUM(fee) calculates total fees
    cursor.execute("SELECT COUNT(*), SUM(fee) FROM canal_logs")
    result = cursor.fetchone()
    conn.close()
    
    total_ships = result[0] if result[0] else 0
    total_earnings = result[1] if result[1] else 0
    return total_ships, total_earnings

# --- SEARCHING THE DATABASE ---
def search_vessels(query: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # LIKE and % signs allow for partial text search (e.g., "posei" finds "Poseidon")
    cursor.execute('''
        SELECT timestamp, vessel_name, dwt, status, fee 
        FROM canal_logs 
        WHERE vessel_name LIKE ?
    ''', (f"%{query}%",))
    
    results = cursor.fetchall()
    conn.close()
    return results

# --- FETCHING ALL VESSELS FROM DATABASE ---
def get_all_vessels():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # ORDER BY id DESC ensures the newest vessels are at the top of the list
    cursor.execute('''
        SELECT timestamp, vessel_name, dwt, status, fee 
        FROM canal_logs 
        ORDER BY id DESC
    ''')
    
    results = cursor.fetchall()
    conn.close()
    return results

# --- CLEARING THE ENTIRE DATABASE ---
def delete_all_vessels():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # SQL command that clears the entire table but keeps its structure
    cursor.execute("DELETE FROM canal_logs")
    
    conn.commit()
    conn.close()
    print("Database: All records have been deleted!")

# --- RATE MANAGEMENT FUNCTIONS IN DATABASE ---

def db_load_prices():
    """Fetches all rates from the database and returns them as a dictionary."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT category, price FROM vessel_rates")
    rows = cursor.fetchall()
    conn.close()
    
    # Convert the list from the database into a dictionary, e.g., {"STANDARD": 5000, ...}
    return {row[0]: row[1] for row in rows}

def db_update_price(category, new_price):
    """Updates the price for a specific category in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE vessel_rates SET price = ? WHERE category = ?", (new_price, category))
    conn.commit()
    conn.close()

# --- EXPORT DATABASE HISTORY TO CSV FILE ---

def export_to_csv():
    """Fetches all data from the canal_logs table and saves it to a CSV report file."""
    # Define the path to the report file - it will be created in the same folder as the database
    report_path = os.path.join(BASE_DIR, "canal_report.csv")
    
    # 1. Connect to the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 2. Fetch ALL columns from the history table, sorted by newest
    cursor.execute("SELECT id, timestamp, vessel_name, dwt, status, fee FROM canal_logs ORDER BY id DESC")
    rows = cursor.fetchall()
    
    # 3. Open the CSV file for writing (in 'w' mode, with utf-8 encoding)
    # newline='' prevents empty lines between rows on some systems
    with open(report_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # 4. Write the first row - column headers (visible in Excel)
        writer.writerow(["Transit ID", "Date and Time", "Vessel Name", "Displacement (DWT)", "Status", "Fee ($)"])
        
        # 5. Write all rows fetched from the database
        writer.writerows(rows)
    
    # 6. Close the database connection
    conn.close()
    
    # Return the file path so the GUI can show a success message to the user
    return report_path

# --- FUNCTION THAT ASKS DB FOR HIGHEST ID AND DELETES THAT EXACT ROW ---

def delete_last_entry():
    """Deletes the newest entry from the canal_logs table and returns True if successful."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # First, check if there is anything to delete
    cursor.execute("SELECT MAX(id) FROM canal_logs")
    last_id = cursor.fetchone()[0]
    
    if last_id is None:
        conn.close()
        return False  # Database is empty
        
    # Delete the row with the highest ID
    cursor.execute("DELETE FROM canal_logs WHERE id = ?", (last_id,))
    conn.commit()
    conn.close()
    
    return True

# --- FUNCTION SUMMING FEES FOR INDIVIDUAL STATUSES ---

def get_stats_by_status():
    """Returns total earnings broken down by individual vessel statuses."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # SQL query: Get the status and SUM of fees, grouping results by status
    cursor.execute("SELECT status, SUM(fee) FROM canal_logs GROUP BY status")
    data = cursor.fetchall() # Returns a list of tuples, e.g., [('STANDARD', 15000), ('PREMIUM', 24000)]
    
    conn.close()
    return data

if __name__ == "__main__":
    init_db()