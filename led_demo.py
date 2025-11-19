#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LED Display Demo - Demonstracja integracji tablicy LED z systemem zawodów
YO&GO Events - 2025

Ten program pokazuje jak zintegrować moduł led_display.py
z dowolnym systemem do obsługi zawodów.
"""

import time
from led_display import LEDDisplayManager, find_available_ports


def simulate_race_system():
    """
    Symulacja systemu obsługi zawodów z tablicą LED
    """
    print("=" * 70)
    print("LED DISPLAY - DEMONSTRACJA INTEGRACJI")
    print("YO&GO Events - 2025")
    print("=" * 70)

    # 1. Znajdź dostępne porty
    print("\n🔍 Szukam dostępnych portów COM...")
    ports = find_available_ports()

    if not ports:
        print("❌ Nie znaleziono portów COM!")
        print("   Upewnij się, że konwerter USB-RS232 jest podłączony")
        return

    print(f"✅ Znaleziono porty: {', '.join(ports)}")

    # Wybór portu
    if len(ports) == 1:
        selected_port = ports[0]
        print(f"📍 Używam portu: {selected_port}")
    else:
        print("\n📍 Wybierz port:")
        for i, port in enumerate(ports, 1):
            print(f"   {i}. {port}")

        while True:
            try:
                choice = int(input("Numer portu: "))
                if 1 <= choice <= len(ports):
                    selected_port = ports[choice - 1]
                    break
                else:
                    print("❌ Nieprawidłowy numer!")
            except ValueError:
                print("❌ Wpisz numer!")

    # Wybór baudrate
    print("\n⚡ Wybierz baudrate:")
    baudrates = [9600, 19200, 38400, 57600, 115200]
    for i, br in enumerate(baudrates, 1):
        print(f"   {i}. {br}")

    while True:
        try:
            choice = int(input("Numer (domyślnie 1 = 9600): ") or "1")
            if 1 <= choice <= len(baudrates):
                selected_baudrate = baudrates[choice - 1]
                break
            else:
                print("❌ Nieprawidłowy numer!")
        except ValueError:
            print("❌ Wpisz numer!")

    # 2. Inicjalizuj manager tablicy LED
    print(f"\n🔌 Łączę z tablicą: {selected_port} @ {selected_baudrate} baud...")
    manager = LEDDisplayManager(port=selected_port, baudrate=selected_baudrate)

    if not manager.initialize():
        print("❌ Nie udało się połączyć z tablicą!")
        return

    print("✅ Tablica LED połączona i gotowa!")

    # 3. Wyświetl nazwę wydarzenia
    print("\n" + "=" * 70)
    event_name = input("📝 Wpisz nazwę wydarzenia (Enter = pomiń): ").strip()
    if event_name:
        print(f"📺 Wyświetlam: {event_name}")
        manager.show_event_name(event_name, duration=5)
        time.sleep(1)

    # 4. Symulacja biegów
    print("\n" + "=" * 70)
    print("🏁 SYMULACJA ZAWODÓW")
    print("=" * 70)
    print("\nDostępne komendy:")
    print("  1 - Bieg z 1 zawodnikiem")
    print("  2 - Bieg z 2 zawodnikami")
    print("  4 - Bieg z 4 zawodnikami")
    print("  6 - Bieg z 6 zawodnikami")
    print("  c - Wyczyść tablicę (nowy bieg)")
    print("  n - Wyświetl nazwę wydarzenia")
    print("  q - Zakończ")
    print("=" * 70)

    race_number = 1

    # Przykładowe czasy do demonstracji
    sample_times = [
        "01:23.456",
        "01:24.789",
        "01:25.123",
        "01:26.456",
        "01:27.890",
        "01:28.234",
    ]

    while True:
        print(f"\n[Bieg #{race_number}]")
        command = input("> ").strip().lower()

        if command == 'q':
            print("\n👋 Zakończenie...")
            break

        elif command == 'c':
            # Wyczyść tablicę - sygnał że przechodzimy do nowego biegu
            manager.clear_display()
            print("🔴 Tablica wyczyszczona (gotowa na nowy bieg)")
            race_number += 1

        elif command == 'n':
            # Wyświetl nazwę wydarzenia
            event_name = input("📝 Nazwa wydarzenia: ").strip()
            if event_name:
                manager.show_event_name(event_name, duration=5)

        elif command in ['1', '2', '4', '6']:
            num_lanes = int(command)

            print(f"\n🏁 Bieg #{race_number} - {num_lanes} zawodnik{'ów' if num_lanes > 1 else ''}")

            # Przygotuj dane biegu
            results = []
            for i in range(num_lanes):
                lane = i + 1
                time_str = sample_times[i % len(sample_times)]
                results.append({'lane': lane, 'time': time_str})
                print(f"   TOR {lane}: {time_str}")

            race_data = {
                'race_number': race_number,
                'lanes': num_lanes,
                'results': results
            }

            # Aktualizuj tablicę
            manager.update_race_results(race_data)

            if num_lanes > 2:
                print(f"   ℹ️  Rotacja czasów aktywna (wyświetlanie po 2 naraz)")

        else:
            print("❌ Nieznana komenda!")

    # 5. Zakończenie
    print("\n" + "=" * 70)
    print("🛑 Wyłączam tablicę...")
    manager.shutdown()
    print("✅ Program zakończony")
    print("=" * 70)


def quick_test():
    """Szybki test wszystkich funkcji"""
    print("=" * 70)
    print("LED DISPLAY - SZYBKI TEST")
    print("=" * 70)

    ports = find_available_ports()
    if not ports:
        print("❌ Brak portów COM!")
        return

    port = ports[0]
    print(f"\n📍 Test na porcie: {port}")

    manager = LEDDisplayManager(port, baudrate=9600)

    if not manager.initialize():
        print("❌ Nie można połączyć!")
        return

    print("✅ Połączono!\n")

    # Test 1: Nazwa wydarzenia
    print("1️⃣ Test: Nazwa wydarzenia")
    manager.show_event_name("ZAWODY TESTOWE", duration=3)
    time.sleep(3.5)

    # Test 2: Jeden zawodnik
    print("\n2️⃣ Test: Jeden zawodnik")
    manager.clear_display()
    time.sleep(1)
    manager.update_race_results({
        'race_number': 1,
        'lanes': 1,
        'results': [{'lane': 1, 'time': '01:23.456'}]
    })
    time.sleep(4)

    # Test 3: Dwóch zawodników
    print("\n3️⃣ Test: Dwóch zawodników")
    manager.clear_display()
    time.sleep(1)
    manager.update_race_results({
        'race_number': 2,
        'lanes': 2,
        'results': [
            {'lane': 1, 'time': '01:23.456'},
            {'lane': 2, 'time': '01:24.789'}
        ]
    })
    time.sleep(4)

    # Test 4: Czterech zawodników (rotacja)
    print("\n4️⃣ Test: Czterech zawodników (rotacja)")
    manager.clear_display()
    time.sleep(1)
    manager.update_race_results({
        'race_number': 3,
        'lanes': 4,
        'results': [
            {'lane': 1, 'time': '01:23.456'},
            {'lane': 2, 'time': '01:24.789'},
            {'lane': 3, 'time': '01:25.123'},
            {'lane': 4, 'time': '01:26.456'}
        ]
    })
    print("   (rotacja przez 12 sekund...)")
    time.sleep(12)

    # Test 5: Czyszczenie
    print("\n5️⃣ Test: Czyszczenie tablicy")
    manager.clear_display()
    time.sleep(2)

    print("\n✅ Wszystkie testy zakończone!")
    manager.shutdown()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # Szybki test bez interakcji
        quick_test()
    else:
        # Tryb interaktywny
        try:
            simulate_race_system()
        except KeyboardInterrupt:
            print("\n\n⏸️ Program przerwany")
        except Exception as e:
            print(f"\n❌ Błąd: {e}")
            import traceback
            traceback.print_exc()
