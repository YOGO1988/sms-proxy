# Analiza Protokołu Tablicy LED

**Oparty na faktycznych danych z oryginalnego programu chronometru**

---

## 🔍 Odkryty Protokół

### Komenda inicjalizacyjna (Set9600)
```
1B 09 0A 00 A4 EB 00 00 0D 0A
```

**Dekompozycja:**
- `1B 09` - nagłówek komendy inicjalizacji
- `0A 00` - długość danych?
- `A4 EB` - checksum/kontrolne
- `00 00` - wypełnienie
- `0D 0A` - końcówka (CRLF)

**Kiedy używana:**
- Na początku komunikacji z tablicą
- Wysyłana 3x pod rząd w oryginalnym programie

---

### Komenda wyświetlenia czasu

**Przykład 1: Czas bez oznaczenia toru**
```
1B 07 3A 00 65 48 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00
30 30 27 30 32 22 2E 30 34 33 20 20 2D 20 [więcej spacj] 0D 0A
```

**Dekompozycja:**
- `1B 07` - nagłówek komendy wyświetlenia
- `3A 00` - typ/długość
- `65 48 00 00` - checksum/timestamp?
- `01 00 00 00 00 00 00 00 00 00` - bajty kontrolne
- `00 00` - numer linii (0x00 = linia 1)
- `0A 00` - separator
- `30 30 27 30 32 22 2E 30 34 33 20 20 2D 20` - **"00'02".043  -"** (TEKST ASCII!)
- Reszta to spacje (0x20) jako wypełnienie
- `0D 0A` - końcówka (CRLF)

**Przykład 2: Czas z oznaczeniem toru**
```
1B 07 3E 00 79 98 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00
30 30 27 30 37 22 2E 38 33 35 20 54 4F 52 20 31 20 [spacje] 0D 0A
```

**Część ASCII:**
- `30 30 27 30 37 22 2E 38 33 35 20 54 4F 52 20 31` = **"00'07".835 TOR 1"**

**Przykład 3: Druga linia**
```
1B 07 3E 00 58 B5 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00
30 30 27 31 30 22 2E 31 39 37 20 54 4F 52 20 32 20 [spacje] 0D 0A
```

**Uwaga:** Bajt na pozycji 18 to `10` zamiast `00` → **LINIA 2!**

**Część ASCII:**
- `30 30 27 31 30 22 2E 31 39 37 20 54 4F 52 20 32` = **"00'10".197 TOR 2"**

---

### Komenda ustawienia linii (czyszczenie/inicjalizacja toru)

**Przykład: Ustawienie TOR 1**
```
1B 08 E8 00 E8 71 00 00 01 00 00 00 00 00 00 00 01 00 0A 00 00 00 00 00 00 00 00 00 5B 00
54 4F 52 20 31 20 20 20 30 29 [długa seria zer] 0D 0A
```

**Część ASCII:**
- `54 4F 52 20 31 20 20 20 30 29` = **"TOR 1    0)"**

**Przykład: Ustawienie TOR 2**
```
1B 08 E8 00 F8 77 00 00 01 00 00 00 00 00 00 00 02 00 0A 00 00 00 10 00 00 00 00 00 38 00
54 4F 52 20 32 20 20 20 30 29 [długa seria zer] 0D 0A
```

**Uwaga:**
- Bajt 16: `02` → TOR 2
- Bajt 22: `10` → LINIA 2

**Część ASCII:**
- `54 4F 52 20 32 20 20 20 30 29` = **"TOR 2    0)"**

---

### Komenda czyszczenia

Prawdopodobnie komenda `1B 08` z samymi zerami w sekcji danych.

---

## 📊 Struktura ogólna

```
[1B] [KOD] [TYP] [00] [KONTROLNE] [LINIA] [00] [0A] [00] [DANE_ASCII] [WYPEŁNIENIE] [0D 0A]
```

**Pola:**
- `1B` - ESC (zawsze)
- `KOD`:
  - `07` - wyświetl dane
  - `08` - ustaw linię/tor
  - `09` - inicjalizacja
- `TYP` - rodzaj komendy (`3A`, `3E`, `E8`, etc.)
- `KONTROLNE` - bajty kontrolne, checksum, timestamp
- `LINIA`:
  - `00 00` = linia 1
  - `10 00` = linia 2
- `DANE_ASCII` - właściwy tekst do wyświetlenia (format: `"00'07".835 TOR 1"`)
- `WYPEŁNIENIE` - spacje (0x20) do stałej długości
- `0D 0A` - CRLF (koniec komendy)

---

## 🎯 Format czasów

Tablica oczekuje czasów w formacie:
```
MM'SS".mmm
```

**Przykłady:**
- `00'02".043` - 2.043 sekundy
- `00'07".835` - 7.835 sekundy
- `01'23".456` - 1 minuta 23.456 sekundy

**Z oznaczeniem toru:**
```
MM'SS".mmm TOR X
```

**Przykłady:**
- `00'07".835 TOR 1`
- `00'10".197 TOR 2`

---

## 🔧 Implementacja

### Sekwencja inicjalizacji
1. Otwórz port COM @ 9600 baud
2. Wyślij komendę `Set9600` (3x dla pewności)
3. Czekaj 0.5s
4. Tablica gotowa do komunikacji

### Wyświetlenie pojedynczego czasu
1. Sformatuj czas: `"00'02".043 TOR 1"`
2. Zbuduj komendę `1B 07` z danymi ASCII
3. Ustaw linię na `00 00` (linia 1)
4. Wyślij

### Wyświetlenie dwóch czasów
1. Sformatuj pierwszy czas: `"00'07".835 TOR 1"`
2. Zbuduj komendę z linią `00 00` (linia 1)
3. Wyślij
4. Czekaj 0.1s
5. Sformatuj drugi czas: `"00'10".197 TOR 2"`
6. Zbuduj komendę z linią `10 00` (linia 2)
7. Wyślij

### Czyszczenie tablicy
1. Zbuduj komendę `1B 08` z samymi zerami
2. Wyślij 3x dla pewności

---

## 💾 Dane z oryginalnego programu

### Sekwencja startowa (inicjalizacja)
```
Set9600: 1B 09 0A 00 A4 EB 00 00 0D 0A
Set9600: 1B 09 0A 00 A4 EB 00 00 0D 0A
Set9600: 1B 09 0A 00 A4 EB 00 00 0D 0A
```

### Wyświetlenie "TOR 1    0)" i "TOR 2    0)"
```
1B 08 E8 00 ... 54 4F 52 20 31 20 20 20 30 29 ... 0D 0A
1B 08 E8 00 ... 54 4F 52 20 32 20 20 20 30 29 ... 0D 0A
```

### Sekwencja czasów z biegu
```
1B 07 3A 00 ... 30 30 27 30 32 22 2E 30 34 33 20 20 2D ... 0D 0A  (00'02".043)
1B 07 3A 00 ... 30 30 27 30 32 22 2E 34 39 35 20 20 2D ... 0D 0A  (00'02".495)
...
1B 07 3E 00 ... 30 30 27 30 37 22 2E 38 33 35 20 54 4F 52 20 31 ... 0D 0A  (00'07".835 TOR 1)
1B 07 3E 00 ... 30 30 27 31 30 22 2E 31 39 37 20 54 4F 52 20 32 ... 0D 0A  (00'10".197 TOR 2)
```

---

## 🧪 Testowanie

### Test podstawowy
```python
from led_display_fixed import LEDDisplayManager

led = LEDDisplayManager(port='COM5', baudrate=9600)
led.initialize()

# Wyświetl pojedynczy czas
led.update_race_results({
    'race_number': 1,
    'lanes': 1,
    'results': [{'lane': 1, 'time': '00:02.043'}]
})
```

### Test dwóch czasów
```python
led.update_race_results({
    'race_number': 2,
    'lanes': 2,
    'results': [
        {'lane': 1, 'time': '00:07.835'},
        {'lane': 2, 'time': '00:10.197'}
    ]
})
```

---

## ✅ Następne kroki

1. **Przetestuj `test_fixed_protocol.py`**
   ```bash
   python test_fixed_protocol.py
   ```

2. **Jeśli działa** → możesz używać `led_display_fixed.py` w swoim programie

3. **Jeśli nie działa** → prześlij mi:
   - Co tablica pokazała?
   - Komunikaty błędów z konsoli
   - Czy wszystkie testy zawiodły czy tylko niektóre?

---

**Autor:** Analiza na podstawie danych z oryginalnego programu chronometru
**Data:** 2025
**Status:** Protokół zidentyfikowany, gotowy do testów
