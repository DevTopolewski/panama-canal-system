import urllib.request
import json

def pobierz_kurs_usd():
    # URL do API NBP, który zwraca aktualny kurs dolara w formacie JSON
    url = "http://api.nbp.pl/api/exchangerates/rates/a/usd/?format=json"
    
    print("🌍 Łączę się z serwerem NBP...")
    
    try:
        # Serwery czasem blokują boty, więc dodajemy nagłówek udający zwykłą przeglądarkę
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        # Otwieramy połączenie internetowe
        with urllib.request.urlopen(req) as response:
            # Czytamy surowe dane i dekodujemy je na tekst
            raw_data = response.read().decode()
            
            # Zamieniamy tekst JSON na wygodny słownik w Pythonie
            data = json.loads(raw_data)
            
            # Wyciągamy konkretną wartość średniego kursu (mid)
            kurs_usd = data['rates'][0]['mid']
            
            print("✅ Połączenie udane!")
            return kurs_usd
            
    except Exception as e:
        print(f"❌ Błąd połączenia z siecią: {e}")
        return None

# Uruchomienie testu
if __name__ == "__main__":
    aktualny_kurs = pobierz_kurs_usd()
    if aktualny_kurs:
        print(f"💵 Aktualny kurs USD wynosi dzisiaj: {aktualny_kurs} PLN")