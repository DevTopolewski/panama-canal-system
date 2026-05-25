import json
import os
CONFIG_FILE = "/Users/pedro/Desktop/config.json"

class Vessel:
    def __init__(self, name: str, dwt: int):
        if dwt <= 0:
            raise ValueError("DWT must be a positive number!")
        self.name = name
        self.dwt = dwt
        self.category = self._assign_category()

    def _assign_category(self) -> str:
        if self.dwt > 150000:
            return "NEO-PANAMAX"
        elif self.dwt > 50000:
            return "PREMIUM"
        else:
            return "STANDARD"
        
    def get_fee(self) -> int:
        from vessel_logic import prices
        return prices.get(self.category, 0)
    
    def __str__(self):
        """Definiuje, jak statek ma wyglądać po wpisaniu print(ship)"""
        return f"🚢 [SHIP CARD] Name: {self.name} | DWT: {self.dwt}t | Cat: {self.category}"

# --- CENNIK ---
prices = {
    "STANDARD": 5000,
    "PREMIUM": 12000,
    "NEO-PANAMAX": 25000
}

# --- FUNKCJA 1: LOGIKA KATEGORYZACJI ---
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

# --- FUNKCJA 2: LOGIKA FINANSOWA ---
def calculate_vessel_fee(dwt: int, category: str) -> int:
    # Opłata bazowa zależna od kategorii
    if category in ["REJECTED", "REJECTED_OVERSIZE", "ERROR_INVALID_VALUE"]:
        return 0
    return prices.get(category, 0)

# --- FUNKCJA 3: AKTUALIZACJA CENY ---

def update_price(category: str, new_price: int) -> bool:
    category = category.upper()
    if category in prices and new_price > 0:
        prices[category] = new_price
        save_prices()
        return True
    return False

def save_prices():
    with open(CONFIG_FILE, "w")as f: json.dump(prices, f)

def load_prices():
    global prices
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            prices = json.load(f)

load_prices()