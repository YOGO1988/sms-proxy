#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LED Display - Quick Start Example
YO&GO Events - 2025

Najprostszy możliwy przykład integracji tablicy LED
"""

from led_display import LEDDisplayManager
import time

def main():
    print("LED Display - Quick Start")
    print("=" * 50)

    # KROK 1: Utwórz manager
    # Zmień 'COM3' na swój port (Windows: COM3, Linux: /dev/ttyUSB0)
    # Zmień 9600 na baudrate swojej tablicy
    led = LEDDisplayManager(port='COM3', baudrate=9600)

    # KROK 2: Połącz z tablicą
    if not led.initialize():
        print("❌ Nie można połączyć z tablicą")
        print("   Sprawdź port COM i baudrate")
        return

    print("✅ Tablica połączona!\n")

    # KROK 3: Wyświetl nazwę wydarzenia (opcjonalnie)
    print("1️⃣ Wyświetlam nazwę wydarzenia...")
    led.show_event_name("ZAWODY TESTOWE", duration=3)
    time.sleep(3.5)

    # KROK 4: Wyczyść tablicę (nowy bieg)
    print("\n2️⃣ Czyszczenie tablicy (nowy bieg)...")
    led.clear_display()
    time.sleep(2)

    # KROK 5: Wyświetl wyniki - JEDEN ZAWODNIK
    print("\n3️⃣ Wyniki - 1 zawodnik...")
    led.update_race_results({
        'race_number': 1,
        'lanes': 1,
        'results': [
            {'lane': 1, 'time': '01:23.456'}
        ]
    })
    time.sleep(5)

    # KROK 6: Nowy bieg - wyczyść
    print("\n4️⃣ Nowy bieg - czyszczenie...")
    led.clear_display()
    time.sleep(2)

    # KROK 7: Wyświetl wyniki - DWÓCH ZAWODNIKÓW
    print("\n5️⃣ Wyniki - 2 zawodników...")
    led.update_race_results({
        'race_number': 2,
        'lanes': 2,
        'results': [
            {'lane': 1, 'time': '01:23.456'},
            {'lane': 2, 'time': '01:24.789'}
        ]
    })
    time.sleep(5)

    # KROK 8: Nowy bieg - wyczyść
    print("\n6️⃣ Nowy bieg - czyszczenie...")
    led.clear_display()
    time.sleep(2)

    # KROK 9: Wyświetl wyniki - CZTERECH ZAWODNIKÓW (rotacja!)
    print("\n7️⃣ Wyniki - 4 zawodników (rotacja)...")
    led.update_race_results({
        'race_number': 3,
        'lanes': 4,
        'results': [
            {'lane': 1, 'time': '01:23.456'},
            {'lane': 2, 'time': '01:24.789'},
            {'lane': 3, 'time': '01:25.123'},
            {'lane': 4, 'time': '01:26.456'}
        ]
    })
    print("   (obserwuj rotację przez 12 sekund...)")
    time.sleep(12)

    # KROK 10: Zakończenie
    print("\n8️⃣ Zakończenie - wyłączam tablicę...")
    led.shutdown()

    print("\n✅ Gotowe!")
    print("=" * 50)
    print("\nIntegracja z Twoim programem:")
    print("1. Importuj: from led_display import LEDDisplayManager")
    print("2. Na początku: led = LEDDisplayManager(port='COM3', baudrate=9600)")
    print("3. Inicjalizuj: led.initialize()")
    print("4. Przed biegiem: led.clear_display()")
    print("5. Po biegu: led.update_race_results(dane)")
    print("6. Na końcu: led.shutdown()")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️ Przerwano")
    except Exception as e:
        print(f"\n❌ Błąd: {e}")
        import traceback
        traceback.print_exc()
