# Integracja Tablicy LED z Systemem Zawodów

**YO&GO Events - 2025**

## 📋 Spis treści

1. [Przegląd](#przegląd)
2. [Wymagania](#wymagania)
3. [Instalacja](#instalacja)
4. [Konfiguracja](#konfiguracja)
5. [Integracja z istniejącym programem](#integracja-z-istniejącym-programem)
6. [API Modułu](#api-modułu)
7. [Przykłady użycia](#przykłady-użycia)
8. [Rozwiązywanie problemów](#rozwiązywanie-problemów)

---

## 🎯 Przegląd

Ten pakiet zawiera moduły do obsługi tablicy LED przez port COM (RS232/USB).

**Funkcje:**
- ✅ Wyświetlanie czasów w biegach (1 tor, 2 tory, wiele torów)
- ✅ Automatyczna rotacja czasów dla więcej niż 2 zawodników
- ✅ Czyszczenie tablicy przy rozpoczęciu nowego biegu
- ✅ Wyświetlanie nazwy wydarzenia
- ✅ Auto-detekcja portu COM i baudrate

**Pliki:**
- `led_autotest.py` - Narzędzie do testowania połączenia z tablicą
- `led_display.py` - Główny moduł obsługi tablicy LED
- `led_demo.py` - Program demonstracyjny
- `LED_INTEGRATION.md` - Ta instrukcja

---

## 📦 Wymagania

### Sprzęt
- Konwerter USB-RS232 (jeśli komputer nie ma portu COM)
- Kabel RS232 do połączenia z tablicą LED
- Tablica LED z obsługą portu COM

### Oprogramowanie
- Python 3.7 lub nowszy
- Biblioteka `pyserial`

---

## 🔧 Instalacja

### Krok 1: Zainstaluj Python
Jeśli nie masz Pythona, pobierz go z [python.org](https://www.python.org/downloads/)

### Krok 2: Zainstaluj wymagane biblioteki
```bash
pip install pyserial
```

### Krok 3: Skopiuj pliki modułu
Umieść pliki w folderze swojego programu:
```
twoj_program/
├── led_display.py      # <- Skopiuj ten plik
├── led_autotest.py     # <- Opcjonalnie (do testów)
├── led_demo.py         # <- Opcjonalnie (przykład)
└── twoj_program.py     # Twój główny program
```

---

## ⚙️ Konfiguracja

### Krok 1: Znajdź port COM

**Windows:**
- Otwórz Menedżer urządzeń
- Rozwiń "Porty (COM i LPT)"
- Zobacz który port to Twoja tablica (np. COM3, COM4)

**Linux/Mac:**
- Uruchom: `ls /dev/tty*`
- Szukaj `/dev/ttyUSB0` lub podobnych

### Krok 2: Określ baudrate tablicy

Uruchom narzędzie testowe:
```bash
python led_autotest.py
```

Program przetestuje wszystkie popularne baudrate (9600, 19200, 38400, 57600, 115200) i pomoże znaleźć właściwy.

### Krok 3: Sprawdź protokół komunikacji

Podczas testów sprawdź które komendy działają:
- ASCII (tekst z końcówką linii)
- HEX (bajty binarne)
- STX/ETX (protokół z kontrolnymi bajtami)

Zanotuj który protokół działa!

---

## 🔌 Integracja z istniejącym programem

### Scenariusz 1: Prosty program (procedural)

```python
from led_display import LEDDisplayManager

# 1. Inicjalizacja (na początku programu)
led_manager = LEDDisplayManager(port='COM3', baudrate=9600)
if not led_manager.initialize():
    print("Uwaga: Tablica LED nie jest dostępna")
    # Program może działać dalej bez tablicy

# 2. Opcjonalnie: Wyświetl nazwę wydarzenia
led_manager.show_event_name("MISTRZOSTWA 2025", duration=5)

# 3. Po zakończeniu biegu - wyświetl wyniki
def on_race_finished(race_data):
    """Wywoływane gdy bieg się kończy"""

    # Wyświetl wyniki na tablicy
    led_manager.update_race_results({
        'race_number': race_data['number'],
        'lanes': race_data['lanes'],
        'results': [
            {'lane': 1, 'time': '01:23.456'},
            {'lane': 2, 'time': '01:24.789'},
            # ... więcej wyników
        ]
    })

# 4. Przy rozpoczęciu nowego biegu - wyczyść tablicę
def on_new_race_started():
    """Wywoływane gdy rozpoczyna się nowy bieg"""
    led_manager.clear_display()  # Tablica się wyłączy = sygnał że działa

# 5. Na zakończenie programu
def on_program_exit():
    """Wywoływane przy zamykaniu programu"""
    led_manager.shutdown()
```

### Scenariusz 2: Program z GUI (tkinter, PyQt, etc.)

```python
import tkinter as tk
from led_display import LEDDisplayManager

class RaceApplication:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("System Zawodów")

        # Inicjalizuj LED display
        self.led_manager = LEDDisplayManager(port='COM3', baudrate=9600)
        self.led_connected = self.led_manager.initialize()

        if self.led_connected:
            print("✅ Tablica LED podłączona")
        else:
            print("⚠️ Tablica LED niedostępna")

        self.setup_ui()

    def setup_ui(self):
        # ... twój kod UI ...

        # Przycisk "Kolejny bieg"
        btn_next = tk.Button(
            self.root,
            text="Kolejny bieg",
            command=self.next_race
        )
        btn_next.pack()

        # Przycisk "Zakończ bieg"
        btn_finish = tk.Button(
            self.root,
            text="Zakończ bieg",
            command=self.finish_race
        )
        btn_finish.pack()

    def next_race(self):
        """Przycisk: Kolejny bieg"""
        # Wyczyść tablicę - sygnał że system działa
        if self.led_connected:
            self.led_manager.clear_display()

        # ... reszta logiki ...

    def finish_race(self):
        """Przycisk: Zakończ bieg i pokaż wyniki"""
        # Pobierz wyniki z twojego systemu
        results = self.get_race_results()

        # Wyświetl na tablicy
        if self.led_connected:
            self.led_manager.update_race_results({
                'race_number': self.current_race,
                'lanes': len(results),
                'results': results
            })

    def get_race_results(self):
        """Pobierz wyniki z twojego systemu"""
        # Przykład - dostosuj do swojego kodu
        return [
            {'lane': 1, 'time': '01:23.456'},
            {'lane': 2, 'time': '01:24.789'},
        ]

    def on_closing(self):
        """Zamknięcie aplikacji"""
        if self.led_connected:
            self.led_manager.shutdown()
        self.root.destroy()

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

# Uruchom aplikację
if __name__ == "__main__":
    app = RaceApplication()
    app.run()
```

### Scenariusz 3: Program webowy (Flask, FastAPI)

```python
from flask import Flask, jsonify, request
from led_display import LEDDisplayManager

app = Flask(__name__)

# Globalna instancja managera
led_manager = None

@app.before_first_request
def initialize():
    """Inicjalizacja przy pierwszym requestcie"""
    global led_manager
    led_manager = LEDDisplayManager(port='COM3', baudrate=9600)
    led_manager.initialize()

@app.route('/api/race/start', methods=['POST'])
def start_race():
    """Rozpoczęcie nowego biegu"""
    if led_manager and led_manager.is_active:
        led_manager.clear_display()

    return jsonify({'status': 'ok', 'message': 'Bieg rozpoczęty'})

@app.route('/api/race/results', methods=['POST'])
def show_results():
    """Wyświetlenie wyników"""
    data = request.json

    if led_manager and led_manager.is_active:
        led_manager.update_race_results(data)

    return jsonify({'status': 'ok', 'message': 'Wyniki wyświetlone'})

@app.route('/api/event/name', methods=['POST'])
def show_event_name():
    """Wyświetlenie nazwy wydarzenia"""
    data = request.json
    event_name = data.get('name', '')

    if led_manager and led_manager.is_active:
        led_manager.show_event_name(event_name, duration=5)

    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True)
```

---

## 📖 API Modułu

### Klasa `LEDDisplayManager`

#### `__init__(port=None, baudrate=9600)`
Tworzy nową instancję managera.

**Parametry:**
- `port` (str, optional): Port COM (np. 'COM3' lub '/dev/ttyUSB0'). Jeśli None, zostanie wykryty automatycznie
- `baudrate` (int): Prędkość transmisji (domyślnie 9600)

#### `initialize() -> bool`
Inicjalizuje połączenie z tablicą.

**Zwraca:** `True` jeśli połączono pomyślnie

#### `show_event_name(event_name: str, duration: float = 5.0)`
Wyświetla nazwę wydarzenia.

**Parametry:**
- `event_name`: Nazwa wydarzenia do wyświetlenia
- `duration`: Czas wyświetlania w sekundach

#### `update_race_results(race_data: dict)`
Aktualizuje wyniki biegu na tablicy.

**Parametry:**
- `race_data`: Słownik z danymi biegu:
  ```python
  {
      'race_number': 1,           # Numer biegu
      'lanes': 2,                 # Liczba torów
      'results': [
          {'lane': 1, 'time': '01:23.456'},
          {'lane': 2, 'time': '01:24.789'},
          # ... więcej wyników
      ]
  }
  ```

**Automatyczne działanie:**
- 1 wynik → wyświetlenie w jednej linii
- 2 wyniki → wyświetlenie w dwóch liniach
- Więcej niż 2 → automatyczna rotacja (po 2 naraz, co 3 sekundy)

#### `clear_display()`
Czyści tablicę (wyłącza wyświetlacz).

**Użycie:** Wywołaj przy rozpoczęciu nowego biegu jako sygnał że system działa.

#### `shutdown()`
Wyłącza tablicę i zamyka połączenie.

**Użycie:** Wywołaj przy zamykaniu programu.

---

## 💡 Przykłady użycia

### Przykład 1: Minimalny kod

```python
from led_display import LEDDisplayManager

# Inicjalizacja
led = LEDDisplayManager()
led.initialize()

# Wyświetl wyniki
led.update_race_results({
    'race_number': 1,
    'lanes': 2,
    'results': [
        {'lane': 1, 'time': '01:23.456'},
        {'lane': 2, 'time': '01:24.789'}
    ]
})

# Zakończenie
led.shutdown()
```

### Przykład 2: Z obsługą błędów

```python
from led_display import LEDDisplayManager

led = LEDDisplayManager(port='COM3', baudrate=9600)

try:
    if led.initialize():
        print("✅ Tablica podłączona")

        # Wyświetl nazwę
        led.show_event_name("ZAWODY 2025", duration=3)

        # Czekaj na wyniki...
        input("Naciśnij Enter gdy bieg się zakończy...")

        # Wyświetl wyniki
        led.update_race_results({
            'race_number': 1,
            'lanes': 1,
            'results': [{'lane': 1, 'time': '01:23.456'}]
        })

    else:
        print("⚠️ Nie można połączyć z tablicą")

except Exception as e:
    print(f"❌ Błąd: {e}")

finally:
    led.shutdown()
```

### Przykład 3: Rotacja dla wielu zawodników

```python
from led_display import LEDDisplayManager
import time

led = LEDDisplayManager()
led.initialize()

# 6 zawodników - automatyczna rotacja
led.update_race_results({
    'race_number': 1,
    'lanes': 6,
    'results': [
        {'lane': 1, 'time': '01:23.456'},
        {'lane': 2, 'time': '01:24.789'},
        {'lane': 3, 'time': '01:25.123'},
        {'lane': 4, 'time': '01:26.456'},
        {'lane': 5, 'time': '01:27.890'},
        {'lane': 6, 'time': '01:28.234'},
    ]
})

# Wyświetla się:
# [0-3s]  TOR 1: 01:23.456 | TOR 2: 01:24.789
# [3-6s]  TOR 3: 01:25.123 | TOR 4: 01:26.456
# [6-9s]  TOR 5: 01:27.890 | TOR 6: 01:28.234
# [9-12s] TOR 1: 01:23.456 | TOR 2: 01:24.789  (powrót)
# ... i tak dalej

time.sleep(15)  # Obserwuj rotację
led.shutdown()
```

---

## 🔧 Rozwiązywanie problemów

### Problem: "Nie znaleziono portów COM"

**Rozwiązanie:**
1. Sprawdź czy konwerter USB-RS232 jest podłączony
2. Windows: Sprawdź Menedżer urządzeń
3. Linux: Sprawdź `ls /dev/tty*`
4. Zainstaluj sterowniki dla konwertera USB-RS232

### Problem: "Tablica nie wyświetla niczego"

**Możliwe przyczyny:**

1. **Zły baudrate** - Uruchom `led_autotest.py` aby znaleźć właściwy
2. **Zły port** - Sprawdź w Menedżerze urządzeń
3. **Zły protokół** - Spróbuj zmienić w kodzie:
   ```python
   # W pliku led_display.py, linia ~27:
   display = LEDDisplay(
       port=port,
       baudrate=baudrate,
       protocol="ascii"  # Zmień na: "hex" lub "stx_etx"
   )
   ```
4. **Zła końcówka linii** - Spróbuj zmienić:
   ```python
   display = LEDDisplay(
       port=port,
       baudrate=baudrate,
       line_ending="\r\n"  # Zmień na: "\n", "\r" lub ""
   )
   ```

### Problem: "Permission denied na Linux"

**Rozwiązanie:**
```bash
# Dodaj użytkownika do grupy dialout
sudo usermod -a -G dialout $USER

# Wyloguj się i zaloguj ponownie
# LUB nadaj uprawnienia bezpośrednio
sudo chmod 666 /dev/ttyUSB0
```

### Problem: "Tablica pokazuje krzaki zamiast tekstu"

**Rozwiązanie:**
- Zmień encoding w `led_display.py` z `utf-8` na `ascii` lub `latin-1`

### Problem: "Rotacja nie działa / pokazuje tylko pierwszą parę"

**Rozwiązanie:**
1. Sprawdź czy przekazujesz więcej niż 2 wyniki
2. Upewnij się że program nie kończy się od razu po wywołaniu `update_race_results()`
3. Rotacja działa w osobnym wątku - upewnij się że główny program czeka

---

## 📞 Potrzebujesz pomocy?

1. **Uruchom narzędzie testowe:**
   ```bash
   python led_autotest.py
   ```
   Zapisz wyniki do pliku i prześlij mi logi.

2. **Uruchom demo:**
   ```bash
   python led_demo.py
   ```
   Sprawdź czy demo działa poprawnie.

3. **Sprawdź logi:**
   - Program tworzy pliki logów w formacie `LED_AutoTest_*.txt`
   - Prześlij mi te pliki

---

## 📝 Notatki dodatkowe

### Formatowanie czasu

Program akceptuje różne formaty czasu:
- `MM.SS` - np. "01.23"
- `MM:SS` - np. "01:23"
- `MM:SS.mmm` - np. "01:23.456"
- `H.MM.SS` - np. "1.23.45"

Możesz użyć funkcji pomocniczej:
```python
from led_display import format_time

# Konwertuj sekundy na format MM:SS.mmm
time_str = format_time(83.456)  # -> "01:23.456"
```

### Wydajność

- Moduł działa asynchronicznie (osobny wątek dla rotacji)
- Nie blokuje głównego programu
- Bezpieczny dla GUI i aplikacji webowych

### Bezpieczeństwo

- Wszystkie błędy są obsługiwane (program nie zawiesi się)
- Program może działać bez tablicy (funkcje będą pomijane)
- Automatyczne zamykanie połączenia przy wyjściu

---

**YO&GO Events - 2025**
Powodzenia z integracją! 🎉
