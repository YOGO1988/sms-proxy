#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test dla LED Display Complete
Sprawdza wszystkie nowe funkcje:
- Jasność 0-100%
- Wygaszanie/włączanie
- Tryb 2-torowy
- Tryb rankingowy
"""

import time
from led_display_complete import LEDDisplayManager


def test_brightness(manager):
    """Test kontroli jasności"""
    print("\n" + "="*60)
    print("TEST 1: KONTROLA JASNOŚCI")
    print("="*60)

    brightness_levels = [100, 75, 50, 25, 10, 0]

    for brightness in brightness_levels:
        print(f"\n📊 Jasność: {brightness}%")
        manager.set_brightness(brightness)
        time.sleep(2)

    print("\n✅ Test jasności zakończony")
    return True


def test_on_off(manager):
    """Test włączania/wyłączania"""
    print("\n" + "="*60)
    print("TEST 2: WŁĄCZANIE/WYŁĄCZANIE")
    print("="*60)

    print("\n🔴 Wyłączam tablicę...")
    manager.turn_off()
    time.sleep(3)

    print("\n✅ Włączam tablicę (50%)...")
    manager.turn_on(50)
    time.sleep(2)

    print("\n✅ Włączam tablicę (100%)...")
    manager.turn_on(100)
    time.sleep(2)

    print("\n✅ Test włączania/wyłączania zakończony")
    return True


def test_2lane_mode(manager):
    """Test trybu 2-torowego"""
    print("\n" + "="*60)
    print("TEST 3: TRYB 2-TOROWY")
    print("="*60)

    # Clear first
    print("\n🧹 Czyszczenie...")
    manager.clear_display()
    time.sleep(1)

    # Test 1: Single competitor
    print("\n📊 Test 3.1: Jeden zawodnik")
    manager.update_race_results({
        'race_number': 1,
        'lanes': 2,
        'results': [
            {'lane': 1, 'time': '00:07.787', 'place': 1}
        ]
    })
    time.sleep(4)

    # Test 2: Two competitors
    print("\n📊 Test 3.2: Dwóch zawodników")
    manager.update_race_results({
        'race_number': 2,
        'lanes': 2,
        'results': [
            {'lane': 1, 'time': '00:07.787', 'place': 1},
            {'lane': 2, 'time': '00:10.362', 'place': 2}
        ]
    })
    time.sleep(4)

    print("\n✅ Test trybu 2-torowego zakończony")
    return True


def test_ranking_mode(manager):
    """Test trybu rankingowego"""
    print("\n" + "="*60)
    print("TEST 4: TRYB RANKINGOWY")
    print("="*60)

    # Clear first
    print("\n🧹 Czyszczenie...")
    manager.clear_display()
    time.sleep(1)

    # Test: 4 competitors with rotation
    print("\n📊 Czterech zawodników (rotacja 1-2, 3-4)")
    manager.update_race_results({
        'race_number': 1,
        'lanes': 4,
        'results': [
            {'lane': 1, 'time': '00:07.787', 'place': 1},
            {'lane': 2, 'time': '00:10.362', 'place': 2},
            {'lane': 3, 'time': '00:11.234', 'place': 3},
            {'lane': 4, 'time': '00:12.456', 'place': 4}
        ]
    })

    print("\n⏱️  Obserwuj rotację przez 12 sekund...")
    print("   Powinno pokazać:")
    print("   - Miejsca 1-2 (3 sekundy)")
    print("   - Miejsca 3-4 (3 sekundy)")
    print("   - Powrót do 1-2...")
    time.sleep(12)

    # Stop rotation
    manager.stop_rotation()

    print("\n✅ Test trybu rankingowego zakończony")
    return True


def test_clear(manager):
    """Test czyszczenia wyświetlacza"""
    print("\n" + "="*60)
    print("TEST 5: CZYSZCZENIE WYŚWIETLACZA")
    print("="*60)

    print("\n🧹 Czyszczenie...")
    manager.clear_display()
    time.sleep(2)

    print("\n✅ Test czyszczenia zakończony")
    return True


def run_all_tests(port='COM5'):
    """
    Uruchom wszystkie testy

    Args:
        port: Port COM do tablicy
    """
    print("="*70)
    print("TEST LED DISPLAY - KOMPLETNA WERSJA")
    print("="*70)
    print(f"\nPort: {port}")
    print("Baudrate: 9600")

    # Initialize manager
    print("\n📡 Łączenie z tablicą...")
    manager = LEDDisplayManager(port, 9600)

    if not manager.initialize():
        print("\n❌ BŁĄD: Nie udało się połączyć z tablicą!")
        print("   Sprawdź:")
        print("   - Czy port jest poprawny")
        print("   - Czy tablica jest włączona")
        print("   - Czy kabel jest podłączony")
        return False

    print("\n✅ Połączono z tablicą!")
    time.sleep(2)

    # Run tests
    results = []

    try:
        # Test 1: Brightness
        results.append(('Jasność', test_brightness(manager)))
        time.sleep(1)

        # Test 2: On/Off
        results.append(('Włączanie/Wyłączanie', test_on_off(manager)))
        time.sleep(1)

        # Test 3: 2-lane mode
        results.append(('Tryb 2-torowy', test_2lane_mode(manager)))
        time.sleep(1)

        # Test 4: Ranking mode
        results.append(('Tryb rankingowy', test_ranking_mode(manager)))
        time.sleep(1)

        # Test 5: Clear
        results.append(('Czyszczenie', test_clear(manager)))

    except KeyboardInterrupt:
        print("\n\n⚠️  Testy przerwane przez użytkownika")
        results.append(('Przerwane', False))

    finally:
        # Cleanup
        print("\n" + "="*60)
        print("PODSUMOWANIE")
        print("="*60)

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}  {test_name}")

        print("\n" + "="*60)
        print(f"Wynik: {passed}/{total} testów zaliczonych")
        print("="*60)

        # Shutdown
        print("\n🔴 Wyłączanie tablicy...")
        manager.shutdown()

        return passed == total


if __name__ == "__main__":
    import sys

    # Get port from command line or use default
    port = sys.argv[1] if len(sys.argv) > 1 else 'COM5'

    # Run tests
    success = run_all_tests(port)

    # Exit with appropriate code
    sys.exit(0 if success else 1)
