#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST NAPRAWIONEGO PROTOKOŁU
Używa rzeczywistego protokołu z oryginalnego programu
"""

from led_display_fixed import LEDDisplayManager
import time

def main():
    print("=" * 60)
    print("TEST NAPRAWIONEGO PROTOKOŁU LED")
    print("Oparty na faktycznych danych z Twojego programu!")
    print("=" * 60)

    port = input("\nPort COM (Enter = COM5): ").strip() or "COM5"

    print(f"\n🔌 Łączę z tablicą na {port}...")
    print("⚠️  PATRZ NA TABLICĘ!")

    led = LEDDisplayManager(port=port, baudrate=9600)

    if not led.initialize():
        print("\n❌ Nie można połączyć!")
        print("Sprawdź:")
        print("  - Czy tablica jest włączona?")
        print("  - Czy port to faktycznie COM5?")
        print("  - Czy kabel jest podłączony?")
        return

    print("✅ Połączono!\n")

    input("➡️  Naciśnij Enter aby wyczyścić tablicę...")

    # Test 1: Wyczyść tablicę
    print("\n1️⃣ TEST: Czyszczenie tablicy")
    print("   👀 Czy tablica się wyłączyła/wyczyszcz?")
    led.clear_display()
    time.sleep(3)

    input("\n➡️  Naciśnij Enter aby wyświetlić POJEDYNCZY czas...")

    # Test 2: Pojedynczy czas
    print("\n2️⃣ TEST: Pojedynczy czas")
    print("   👀 Powinno pokazać: 00'02\".043 TOR 1")
    led.update_race_results({
        'race_number': 1,
        'lanes': 1,
        'results': [
            {'lane': 1, 'time': '00:02.043'}
        ]
    })
    time.sleep(5)

    input("\n➡️  Naciśnij Enter aby wyświetlić DWA czasy...")

    # Test 3: Dwa czasy
    print("\n3️⃣ TEST: Dwa czasy (2 linie)")
    print("   👀 Powinno pokazać:")
    print("      Linia 1: 00'07\".835 TOR 1")
    print("      Linia 2: 00'10\".197 TOR 2")
    led.clear_display()
    time.sleep(1)

    led.update_race_results({
        'race_number': 2,
        'lanes': 2,
        'results': [
            {'lane': 1, 'time': '00:07.835'},
            {'lane': 2, 'time': '00:10.197'}
        ]
    })
    time.sleep(5)

    input("\n➡️  Naciśnij Enter aby przetestować ROTACJĘ...")

    # Test 4: Rotacja (4 zawodników)
    print("\n4️⃣ TEST: Rotacja 4 zawodników")
    print("   👀 Powinno rotować co 3 sekundy:")
    print("      [0-3s]  TOR 1 + TOR 2")
    print("      [3-6s]  TOR 3 + TOR 4")
    print("      [6-9s]  TOR 1 + TOR 2 (powrót)")
    led.clear_display()
    time.sleep(1)

    led.update_race_results({
        'race_number': 3,
        'lanes': 4,
        'results': [
            {'lane': 1, 'time': '00:02.043'},
            {'lane': 2, 'time': '00:03.413'},
            {'lane': 3, 'time': '00:04.768'},
            {'lane': 4, 'time': '00:06.135'}
        ]
    })

    print("   Obserwuj przez 15 sekund...")
    time.sleep(15)

    # Test 5: Nazwa wydarzenia
    input("\n➡️  Naciśnij Enter aby wyświetlić NAZWĘ WYDARZENIA...")

    print("\n5️⃣ TEST: Nazwa wydarzenia")
    print("   👀 Powinno pokazać: MISTRZOSTWA 2025")
    led.clear_display()
    time.sleep(1)
    led.show_event_name("MISTRZOSTWA 2025", duration=5)

    # Zakończenie
    print("\n" + "=" * 60)
    print("KONIEC TESTÓW")
    print("=" * 60)

    print("\n📋 WYNIKI:")
    print("Czy tablica wyświetliła WSZYSTKIE testy poprawnie?")
    print("")
    print("JEŚLI TAK:")
    print("  ✅ Protokół działa!")
    print("  ✅ Możesz używać led_display_fixed.py w swoim programie!")
    print("")
    print("JEŚLI NIE:")
    print("  Powiedz mi:")
    print("  1. Które testy zadziałały?")
    print("  2. Co tablica pokazała (lub nie pokazała)?")
    print("  3. Czy były jakieś błędy w konsoli?")
    print("")

    led.shutdown()
    print("✅ Test zakończony")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️  Przerwano")
    except Exception as e:
        print(f"\n❌ Błąd: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("\nNaciśnij Enter aby zakończyć...")
