# Instrukcja uruchomienia Chronometru LED na Windows

## Metoda 1: URUCHOM_CHRONOMETR.vbs (ZALECANA ✅)

**Kliknij dwukrotnie na plik: `URUCHOM_CHRONOMETR.vbs`**

- ✅ Brak ostrzeżeń o nieznanym wydawcy
- ✅ Automatyczna instalacja wymagań
- ✅ Najprostsza metoda

---

## Metoda 2: uruchom_chronometr.bat

**Kliknij dwukrotnie na plik: `uruchom_chronometr.bat`**

### Jeśli pojawi się ostrzeżenie "Nieznany wydawca":
1. Kliknij **"Więcej informacji"** lub **"More info"**
2. Kliknij **"Uruchom mimo to"** lub **"Run anyway"**

![Instrukcja Windows Defender](https://i.imgur.com/ZvB9fQx.png)

---

## Metoda 3: Ręczne uruchomienie

1. Otwórz **Wiersz polecenia** (CMD) w folderze z programem:
   - Shift + Prawy przycisk myszy w folderze
   - Wybierz "Otwórz okno poleceń tutaj" lub "Otwórz w terminalu"

2. Wpisz:
   ```
   python chronometr_v5_LED.py
   ```

---

## Wymagania

### Python
Program wymaga zainstalowanego **Python 3.7+**

**Sprawdź czy masz Pythona:**
```
python --version
```

**Jeśli Python nie jest zainstalowany:**
1. Pobierz z: https://www.python.org/downloads/
2. **WAŻNE:** Podczas instalacji zaznacz ✅ **"Add Python to PATH"**

### Biblioteki (instalują się automatycznie)
- `pyserial` - komunikacja z chronometrem i tablicą LED

---

## Rozwiązywanie problemów

### ❌ "Python nie jest zainstalowany"
- Zainstaluj Python (zobacz powyżej)
- Podczas instalacji KONIECZNIE zaznacz "Add Python to PATH"

### ❌ "Nie znaleziono pliku chronometr_v5_LED.py"
- Upewnij się, że pliki `.bat` / `.vbs` są w tym samym folderze co `chronometr_v5_LED.py`

### ❌ Terminal otwiera się i od razu zamyka
- Użyj pliku `URUCHOM_CHRONOMETR.vbs` zamiast `.bat`
- Lub uruchom `.bat` prawym przyciskiem → "Uruchom jako administrator"

### ❌ Ostrzeżenie Windows Defender / SmartScreen
- To normalne dla skryptów `.bat`
- Kliknij "Więcej informacji" → "Uruchom mimo to"
- LUB użyj pliku `.vbs` (nie wywołuje ostrzeżenia)

---

## Struktura plików

```
chronometr/
├── chronometr_v5_LED.py          # Główny program
├── URUCHOM_CHRONOMETR.vbs        # ⭐ Uruchomienie (ZALECANE)
├── uruchom_chronometr.bat        # Uruchomienie (z diagnostyką)
└── requirements.txt               # Zależności Python
```

---

## Pomoc

Jeśli nadal masz problemy:
1. Skopiuj komunikat błędu z terminala
2. Zgłoś problem w repozytorium GitHub

---

**YO&GO Events - 2025**
