# LED Display Integration for Race Timing System

**YO&GO Events - 2025**

System integracji tablicy LED z systemem pomiaru czasu w zawodach sportowych.

## 🎯 Funkcje

- ✅ **Automatyczne wyświetlanie czasów** - system sam dobiera tryb wyświetlania
- ✅ **1 zawodnik** → czas w jednej linii
- ✅ **2 zawodników** → czasy w dwóch liniach
- ✅ **Więcej zawodników** → automatyczna rotacja (pokazuje po 2, potem kolejne 2, itd.)
- ✅ **Czyszczenie tablicy** - przy rozpoczęciu nowego biegu (sygnał że system działa)
- ✅ **Nazwa wydarzenia** - opcjonalne wyświetlanie nazwy zawodów
- ✅ **Auto-detekcja** - automatyczne wykrywanie portu COM i baudrate

## 📦 Co znajduje się w pakiecie?

| Plik | Opis |
|------|------|
| `led_display.py` | Główny moduł - gotowy do integracji z Twoim programem |
| `led_autotest.py` | Narzędzie testowe - znajdź właściwy port i baudrate |
| `led_demo.py` | Program demonstracyjny - zobacz jak to działa |
| `LED_INTEGRATION.md` | Szczegółowa instrukcja integracji |
| `requirements.txt` | Zależności Pythona |

## ⚡ Szybki start

### 1. Instalacja

```bash
# Zainstaluj zależności
pip install -r requirements.txt
```

### 2. Test połączenia

```bash
# Uruchom narzędzie testowe
python led_autotest.py
```

Program automatycznie:
- Znajdzie dostępne porty COM
- Przetestuje różne baudrate (9600, 19200, 38400, 57600, 115200)
- Zapisze wyniki testów do pliku

**Zanotuj który baudrate działał!**

### 3. Demo

```bash
# Uruchom program demonstracyjny
python led_demo.py

# LUB szybki test wszystkich funkcji
python led_demo.py --quick
```

### 4. Integracja z Twoim programem

**Minimalny przykład:**

```python
from led_display import LEDDisplayManager

# 1. Inicjalizacja
led = LEDDisplayManager(port='COM3', baudrate=9600)
if not led.initialize():
    print("Uwaga: Tablica niedostępna")

# 2. Wyświetl nazwę wydarzenia (opcjonalnie)
led.show_event_name("MISTRZOSTWA 2025", duration=5)

# 3. Gdy rozpoczyna się nowy bieg - wyczyść tablicę
led.clear_display()  # Tablica się wyłączy = sygnał że działa

# 4. Po zakończeniu biegu - pokaż wyniki
led.update_race_results({
    'race_number': 1,
    'lanes': 2,
    'results': [
        {'lane': 1, 'time': '01:23.456'},
        {'lane': 2, 'time': '01:24.789'}
    ]
})

# 5. Na zakończenie programu
led.shutdown()
```

**To wszystko!** System sam zadba o właściwe wyświetlanie.

## 📖 Dokumentacja

Szczegółowa instrukcja integracji: **[LED_INTEGRATION.md](LED_INTEGRATION.md)**

Zawiera:
- Pełną dokumentację API
- Przykłady integracji (GUI, web, konsola)
- Rozwiązywanie problemów
- Zaawansowane ustawienia

## 🔧 Wymagania

### Sprzęt
- Konwerter USB-RS232 (jeśli komputer nie ma portu COM)
- Tablica LED z interfejsem RS232/COM

### Oprogramowanie
- Python 3.7+
- pyserial (automatycznie instalowane z requirements.txt)

## 🚀 Jak to działa?

### Jeden zawodnik
```
┌──────────────────────┐
│  TOR 1: 01:23.456    │
└──────────────────────┘
```

### Dwóch zawodników
```
┌──────────────────────┐
│  TOR 1: 01:23.456    │
│  TOR 2: 01:24.789    │
└──────────────────────┘
```

### Czterech zawodników (rotacja co 3 sekundy)
```
[0-3s]                    [3-6s]                    [6-9s]
┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│  TOR 1: 01:23.456    │  │  TOR 3: 01:25.123    │  │  TOR 1: 01:23.456    │
│  TOR 2: 01:24.789    │  │  TOR 4: 01:26.456    │  │  TOR 2: 01:24.789    │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘
        ↓                         ↓                         ↓
    (powrót na początek po wyświetleniu wszystkich)
```

## 💡 Przykładowe zastosowania

### 1. System pomiaru czasu
```python
# Po zakończeniu pomiaru czasu
def on_finish(lane, time):
    results.append({'lane': lane, 'time': time})

    # Aktualizuj tablicę
    led.update_race_results({
        'race_number': current_race,
        'lanes': len(results),
        'results': results
    })
```

### 2. Import z pliku CSV
```python
import csv

with open('results.csv') as f:
    reader = csv.DictReader(f)
    results = [
        {'lane': int(row['lane']), 'time': row['time']}
        for row in reader
    ]

led.update_race_results({
    'race_number': 1,
    'lanes': len(results),
    'results': results
})
```

### 3. Integracja z GUI (przycisk)
```python
def on_button_click():
    # Pobierz wyniki z formularza
    results = get_form_results()

    # Wyświetl na tablicy
    led.update_race_results({
        'race_number': race_num,
        'lanes': len(results),
        'results': results
    })
```

## 🔍 Rozwiązywanie problemów

| Problem | Rozwiązanie |
|---------|-------------|
| Nie widać portów COM | Sprawdź czy konwerter USB-RS232 jest podłączony, zainstaluj sterowniki |
| Tablica nie wyświetla | Uruchom `led_autotest.py` aby znaleźć właściwy baudrate |
| "Permission denied" (Linux) | `sudo usermod -a -G dialout $USER` |
| Krzaki zamiast tekstu | Zmień encoding w kodzie |
| Rotacja nie działa | Upewnij się że przekazujesz >2 wyniki |

Więcej w [LED_INTEGRATION.md](LED_INTEGRATION.md#rozwiązywanie-problemów)

## 📋 Checklist integracji

- [ ] Zainstalować `pyserial`
- [ ] Uruchomić `led_autotest.py` i znaleźć działający baudrate
- [ ] Przetestować `led_demo.py`
- [ ] Skopiować `led_display.py` do folderu programu
- [ ] Zaimportować `LEDDisplayManager`
- [ ] Dodać inicjalizację na początku programu
- [ ] Dodać `clear_display()` przy rozpoczęciu biegu
- [ ] Dodać `update_race_results()` po zakończeniu biegu
- [ ] Dodać `shutdown()` przy zamykaniu programu
- [ ] Przetestować na żywym systemie!

## 🎓 Przykład kompletnej integracji

Zobacz plik [led_demo.py](led_demo.py) - zawiera pełny przykład programu z GUI,
obsługą błędów i wszystkimi funkcjami.

## 📞 Wsparcie

1. Przeczytaj [LED_INTEGRATION.md](LED_INTEGRATION.md)
2. Uruchom `led_autotest.py` i prześlij logi
3. Sprawdź sekcję "Rozwiązywanie problemów"

## 📄 Licencja

Kod stworzony dla YO&GO Events - 2025

---

**Powodzenia z integracją! 🎉**

Jeśli masz pytania lub problemy, uruchom testy i prześlij wyniki.
