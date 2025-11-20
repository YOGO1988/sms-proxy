# LED Display - Kompletna Dokumentacja

## Przegląd

Moduł `led_display_complete.py` zapewnia pełną obsługę tablicy LED z następującymi funkcjami:

### ✅ Funkcje zaimplementowane

1. **Kontrola jasności** - ustawianie jasności 0-100%
2. **Wygaszanie/włączanie** - `turn_off()` / `turn_on()`
3. **Tryb 2-torowy** - wyświetlanie wyników dla 2 zawodników (TOR 1, TOR 2)
4. **Tryb rankingowy** - wyświetlanie wyników dla 3+ zawodników (pary: 1-2, 3-4, 5-6...)
5. **Wyświetlanie tekstów** - proste teksty na linii 1 i 2
6. **Czyszczenie wyświetlacza**

---

## Szybki start

### 1. Instalacja

```bash
# Moduł wymaga tylko pyserial
pip install pyserial
```

### 2. Podstawowe użycie

```python
from led_display_complete import LEDDisplayManager

# Inicjalizacja
manager = LEDDisplayManager(port='COM5', baudrate=9600)

if manager.initialize():
    # Ustaw jasność
    manager.set_brightness(75)  # 75%

    # Wyświetl wyniki
    manager.update_race_results({
        'race_number': 1,
        'lanes': 2,
        'results': [
            {'lane': 1, 'time': '00:07.787', 'place': 1},
            {'lane': 2, 'time': '00:10.362', 'place': 2}
        ]
    })

    # Wyłącz
    manager.shutdown()
```

---

## API Reference

### LEDDisplayManager

#### Inicjalizacja

```python
manager = LEDDisplayManager(port='COM5', baudrate=9600)
success = manager.initialize()
```

#### Kontrola jasności

```python
# Ustaw jasność 0-100%
manager.set_brightness(50)  # 50%

# Wygaś tablicę (brightness=0)
manager.turn_off()

# Włącz tablicę z określoną jasnością
manager.turn_on(100)  # 100%
```

#### Wyświetlanie wyników

**Tryb 2-torowy** (lanes=2):
```python
manager.update_race_results({
    'race_number': 1,
    'lanes': 2,  # TRYB 2-TOROWY
    'results': [
        {'lane': 1, 'time': '00:07.787', 'place': 1},
        {'lane': 2, 'time': '00:10.362', 'place': 2}
    ]
})
```

**Tryb rankingowy** (lanes>2 lub więcej niż 2 wyniki):
```python
manager.update_race_results({
    'race_number': 1,
    'lanes': 4,  # TRYB RANKINGOWY
    'results': [
        {'lane': 1, 'time': '00:07.787', 'place': 1},
        {'lane': 2, 'time': '00:10.362', 'place': 2},
        {'lane': 3, 'time': '00:11.234', 'place': 3},
        {'lane': 4, 'time': '00:12.456', 'place': 4}
    ]
})
```

W trybie rankingowym wyniki rotują co 3 sekundy:
- Najpierw miejsca 1-2 (3 sek)
- Potem miejsca 3-4 (3 sek)
- Potem miejsca 5-6 (3 sek)
- Itd., potem powrót do początku

#### Zatrzymanie rotacji

```python
manager.stop_rotation()
```

#### Czyszczenie wyświetlacza

```python
manager.clear_display()
```

#### Wyłączenie

```python
manager.shutdown()  # Wyłącza tablicę i rozłącza
```

---

## Przykłady użycia

### Przykład 1: Prosta prezentacja wyniku

```python
from led_display_complete import LEDDisplayManager
import time

manager = LEDDisplayManager('COM5', 9600)

if manager.initialize():
    # Wyświetl wynik na TOR 1
    manager.update_race_results({
        'race_number': 1,
        'lanes': 2,
        'results': [
            {'lane': 1, 'time': '00:07.787', 'place': 1}
        ]
    })

    time.sleep(10)
    manager.shutdown()
```

### Przykład 2: Zawody z wieloma zawodnikami

```python
from led_display_complete import LEDDisplayManager
import time

manager = LEDDisplayManager('COM5', 9600)

if manager.initialize():
    # Zawody z 6 zawodnikami
    manager.update_race_results({
        'race_number': 1,
        'lanes': 6,
        'results': [
            {'lane': 1, 'time': '00:07.787', 'place': 1},
            {'lane': 2, 'time': '00:08.362', 'place': 2},
            {'lane': 3, 'time': '00:09.234', 'place': 3},
            {'lane': 4, 'time': '00:10.456', 'place': 4},
            {'lane': 5, 'time': '00:11.123', 'place': 5},
            {'lane': 6, 'time': '00:12.789', 'place': 6}
        ]
    })

    # Rotacja przez 30 sekund
    time.sleep(30)

    manager.shutdown()
```

### Przykład 3: Kontrola jasności w zależności od pory dnia

```python
from led_display_complete import LEDDisplayManager
from datetime import datetime

manager = LEDDisplayManager('COM5', 9600)

if manager.initialize():
    hour = datetime.now().hour

    if 6 <= hour < 20:
        # Dzień - pełna jasność
        manager.set_brightness(100)
    else:
        # Noc - przyciemnione
        manager.set_brightness(30)

    # ... wyświetl wyniki ...

    manager.shutdown()
```

---

## Testowanie

### Test wszystkich funkcji

```bash
python test_led_complete.py COM5
```

### Test interaktywny

```bash
python led_display_complete.py
```

Dostępne komendy:
- `bright <0-100>` - Ustaw jasność
- `off` - Wygaś tablicę
- `on` - Włącz tablicę
- `clear` - Wyczyść tablicę
- `2lane` - Test trybu 2-torowego
- `ranking` - Test trybu rankingowego
- `quit` - Wyjście

### Test tylko jasności

```bash
python led_display_complete.py test-brightness
```

---

## Integracja z chronometrem

### Krok 1: Import

```python
from led_display_complete import LEDDisplayManager
```

### Krok 2: Inicjalizacja w programie głównym

```python
# W setup/initialization
led_manager = LEDDisplayManager('COM5', 9600)
if not led_manager.initialize():
    print("⚠️ Tablica LED niedostępna")
    led_manager = None
```

### Krok 3: Aktualizacja po zakończeniu biegu

```python
# Po zakończeniu biegu
if led_manager:
    led_manager.update_race_results({
        'race_number': current_race,
        'lanes': num_lanes,
        'results': race_results  # Lista wyników z time i place
    })
```

### Krok 4: Przycisk wygaszania

```python
# Handler dla przycisku "Wygaś tablicę"
def on_dim_button_click():
    if led_manager:
        led_manager.turn_off()

# Handler dla przycisku "Włącz tablicę"
def on_brighten_button_click():
    if led_manager:
        led_manager.turn_on(100)
```

---

## Ograniczenia i TODO

### Aktualne ograniczenia

1. **Wyświetlanie czasów**: Obecnie używa przykładowych pakietów (~7s, ~10s)
   - Aby wyświetlać rzeczywiste czasy, potrzeba:
     - Nagrać więcej pakietów z różnymi czasami
     - LUB odtworzyć algorytm obliczania checksumu dla pakietów czasowych

2. **Wyświetlanie tekstów**: Funkcja `show_text()` jest placeholder
   - Potrzeba nagrać pakiety z różnymi tekstami
   - Albo odtworzyć algorytm tworzenia pakietów tekstowych

### TODO

- [ ] Dodać funkcję generowania pakietów czasowych z dowolnym czasem
- [ ] Dodać funkcję generowania pakietów tekstowych z dowolnym tekstem
- [ ] Dodać obsługę GPIO dla sprzętowego przycisku wygaszania
- [ ] Dodać konfigurację kolorów (jeśli tablica obsługuje)
- [ ] Dodać więcej efektów przejść (fade, slide, etc.)

---

## Rozwiązywanie problemów

### Tablica się nie łączy

```
❌ Błąd połączenia: [SerialException] ...
```

**Rozwiązanie:**
1. Sprawdź czy port jest poprawny (`COM5`, `COM3`, etc.)
2. Sprawdź czy tablica jest włączona
3. Sprawdź czy kabel jest podłączony
4. Sprawdź czy inny program nie używa portu

### Tablica nie reaguje na komendy

**Rozwiązanie:**
1. Sprawdź baudrate (domyślnie 9600)
2. Spróbuj zrestartować tablicę
3. Sprawdź czy pakiety są poprawne (porównaj z logami)

### Rotacja nie działa

**Rozwiązanie:**
1. Sprawdź czy podałeś `lanes > 2` lub więcej niż 2 wyniki
2. Sprawdź czy wątek rotacji został zatrzymany (`manager.stop_rotation()`)
3. Sprawdź logi - powinno być "Tryb rankingowy"

---

## Kontakt

W razie problemów lub pytań:
- Sprawdź logi programu
- Uruchom testy: `python test_led_complete.py`
- Sprawdź przykłady w tym dokumencie

---

**Ostatnia aktualizacja:** 2025-11-20
**Wersja:** 1.0.0
