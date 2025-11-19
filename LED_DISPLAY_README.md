# LED Display Driver - Dokumentacja

## Status Projektu

### ✅ DZIAŁA
- **Wyświetlanie nazw** - komenda `name` (hardcoded "Tymon")
- **Test pakietów** - komenda `test` (4 różne pakiety)
- **Wyświetlanie czasu** - komenda `time:` z CRC16 (**NAPRAWIONE!**)
- **Stoper** - komenda `stopwatch` (**NAPRAWIONE!**)
- **Informacje o torach** - komendy `lane:1`, `lane:2`
- **Czyszczenie linii 2** - automatyczne po wyświetleniu czasu
- **Czyszczenie tablicy** - komenda `clear`

### ⚠️ W ROZWOJU
- **Własne nazwy zawodników** - wymaga implementacji CRC16 dla pakietów nazw
- **Więcej torów** - obecnie tylko TOR 1 i TOR 2

---

## Najważniejsza Zmiana

### Problem (Stary Kod)
```python
# Stary kod NIE przeliczał checksumy CRC16!
def _replace_text_in_packet(self, base_packet_name, new_text_bytes, start_pos):
    packet = bytearray(self.PACKETS[base_packet_name])
    # Tylko zamieniał tekst - CHECKSUM SIĘ NIE ZGADZAŁ!
    for i, byte in enumerate(new_text_bytes):
        packet[start_pos + i] = byte
    return bytes(packet)
```

❌ **Skutek**: Pakiety `time:` i `stopwatch` nie działały, bo checksum był nieprawidłowy!

### Rozwiązanie (Nowy Kod)
```python
# Nowy kod OBLICZA CRC16 dla każdego pakietu!
def _calculate_crc16(self, data):
    """CRC16-IBM/ANSI (wielomian 0x8005)"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc

def _build_time_packet(self, seconds, lane_name=None):
    # 1. Buduje pakiet z nowym tekstem
    # 2. OBLICZA CRC16
    # 3. Wstawia CRC do pakietu (bajty 4-5)
    # 4. Pakiet działa! ✅
```

✅ **Skutek**: Teraz `time:` i `stopwatch` **DZIAŁAJĄ POPRAWNIE!**

---

## Czyszczenie Linii 2

### Problem
Kiedy wyświetla się tekst w linii 1, linia 2 pozostaje ze starymi danymi lub danymi producenta.

### Rozwiązanie
```python
def show_time(self, seconds, lane_name=None, clear_line2=True):
    # Wyświetl czas
    self.ser.write(packet)

    # AUTOMATYCZNE czyszczenie linii 2!
    if clear_line2:
        time.sleep(0.2)
        self._send_raw('clear_line2')  # Wysyła pakiet z samymi spacjami
```

✅ **Domyślnie** - linia 2 jest czyszczona po każdym `show_time()`

---

## Instalacja

### Wymagania
```bash
pip install pyserial
```

### Uruchomienie
```bash
python led_display_driver.py
```

---

## Użycie

### Tryb Interaktywny
```
Port (Enter = COM5): [ENTER]
✅ Połączono: COM5

📋 KOMENDY:
  test         - test 4 pakietów (Tymon, czasy)
  stopwatch    - dynamiczny stoper
  time:7.5     - pokaż czas (sekundy)
  time:1:22.52 - pokaż czas (MM:SS.mmm)
  lane:1       - info TOR 1
  lane:2       - info TOR 2
  name         - pokaż 'Tymon'
  clear        - wyczyść tablicę
  debug        - włącz/wyłącz debug
  quit         - wyjście

> time:7.5
✅ Wysłano: 7.5s

> stopwatch
⏱️  STOPER - aktualizuje co 1.0 sek
   Ctrl+C aby przerwać

⏱️  5.234s
```

### Użycie w Kodzie
```python
from led_display_driver import LEDDisplay

# Połącz
led = LEDDisplay('COM5', 9600)
led.connect()

# Wyświetl czas zawodnika
led.show_time(7.467)  # 00'07".467  -

# Wyświetl czas z torem
led.show_time(10.362, "TOR 2")  # 00'10".362 TOR 2

# Wyświetl nazwę (hardcoded)
led.show_name("Tymon")  # TYMON  --

# Info o torze
led.show_lane_info(1)  # TOR 1   0)

# Wyczyść tablicę
led.clear_display()

# Rozłącz
led.disconnect()
```

---

## Struktura Pakietu

```
Offset  | Bajty  | Opis
--------|--------|---------------------------
0       | 1B     | Start byte
1       | 07     | Command (07 = time/name, 08 = lane)
2-3     | XX XX  | Length (little endian)
4-5     | XX XX  | CRC16 (little endian) ⚠️ OBLICZANE!
6-21    | ...    | Header (16 bajtów)
22+     | ASCII  | Text data (czas, nazwa, tor)
-2      | 0D 0A  | End bytes (CRLF)
```

### Przykład - Pakiet Czasu
```
1B 07 3A 00 51 8B 00 00 01 00 00 00 00 00 00 00
^^    ^^    ^^^^
|     |     CRC16 = 0x8B51
|     Length = 0x003A (58 bajtów)
Start

...Header...

30 30 27 30 37 22 2E 34 36 37 20 20 2D 20 ...
|                                            |
|   "00'07".467  - "                         |
Text (ASCII) - od bajtu 22

0D 0A
End
```

---

## TODO - Następne Kroki

### 1. Własne nazwy zawodników
```python
def show_name(self, name):
    """
    TODO: Implementacja
    - Zbuduj pakiet nazwy (jak w _build_time_packet)
    - Dopełnij spacjami do 64 znaków
    - Oblicz CRC16
    - Wyślij
    """
    pass
```

### 2. Więcej torów
```python
# Dodaj pakiety dla TOR 3, TOR 4...
PACKETS = {
    'lane3': bytes.fromhex('...'),
    'lane4': bytes.fromhex('...'),
}
```

### 3. Wyświetlanie wyniku
```python
def show_result(self, place, name, time_seconds):
    """
    Wyświetl: "1. TYMON  00'07".467"
    """
    pass
```

### 4. Sekwencje animacji
```python
def countdown(self, from_seconds=3):
    """Odliczanie: 3... 2... 1... START!"""
    pass
```

---

## Debug Mode

```python
led = LEDDisplay('COM5', 9600)
led.debug = True  # Włącz debug
led.connect()

led.show_time(7.5)
# 📤 Wysyłam pakiet czasu: 1b 07 3a 00 51 8b 00 00 ...
```

---

## Znane Problemy

### ✅ ROZWIĄZANE
- ~~Pakiety czasu nie działały~~ → **NAPRAWIONE** (CRC16)
- ~~Stoper nie działał~~ → **NAPRAWIONE** (CRC16)
- ~~Linia 2 nie była czyszczona~~ → **NAPRAWIONE** (clear_line2)

### ⚠️ AKTYWNE
- Własne nazwy zawodników wymagają implementacji CRC16
- Długie opóźnienia między pakietami (0.3s-0.5s)

---

## Kontakt / Projekt

Projekt: **YO&GO Events - Wyświetlanie Czasów Zawodników**
Tablica: **Color-LED Display**
Port: **COM5** (RS-232)
Baudrate: **9600**

---

## Historia Zmian

### v1.0 - 2025-11-19 ✅
- ✅ Implementacja CRC16 dla pakietów czasu
- ✅ Naprawa `show_time()` - działa poprawnie
- ✅ Naprawa `stopwatch` - działa poprawnie
- ✅ Automatyczne czyszczenie linii 2
- ✅ Dodano `clear_display()`
- ✅ Debug mode

### v0.1 - Poprzednia wersja ❌
- ✅ Test pakietów działał
- ✅ Nazwa "Tymon" działała
- ❌ Pakiety czasu NIE działały (brak CRC16)
