#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test napraw dla LED Display
- Ranking bez mrugania
- Timer START/META z wyświetlaniem czasu
"""

import time
from led_display_complete import LEDDisplayManager


def test_ranking_fix(manager):
    """Test naprawionego trybu rankingowego (bez mrugania)"""
    print("\n" + "="*60)
    print("TEST 1: RANKING BEZ MRUGANIA")
    print("="*60)
    print("Tablica powinna pokazywać:")
    print("  1. Miejsca 1-2 przez 3 sekundy")
    print("  2. Miejsca 3-4 przez 3 sekundy")
    print("  3. Z powrotem miejsca 1-2")
    print("  BEZ mrugania między zmianami!")
    print()

    input("Naciśnij ENTER aby rozpocząć test...")

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

    print("\n⏱️  Obserwuj rotację przez 15 sekund...")
    print("   ✅ Jeśli NIE mruga między zmianami - FIX DZIAŁA!")
    print("   ❌ Jeśli mruga - coś jest nie tak")

    time.sleep(15)
    manager.stop_rotation()

    print("\n✅ Test rankingu zakończony")
    return True


def test_timer_fix(manager):
    """Test naprawionego timera START/META"""
    print("\n" + "="*60)
    print("TEST 2: TIMER START/META")
    print("="*60)
    print("Tablica powinna wyświetlać płynący czas od startu do mety")
    print("BEZ gaśnięcia ekranu!")
    print()

    input("Naciśnij ENTER aby WYSTARTOWAĆ timer...")

    manager.start_timer()

    print("\n⏱️  Timer działa!")
    print("   Obserwuj wyświetlacz - powinien pokazywać płynący czas")
    print("   ✅ Jeśli czas płynie płynnie - FIX DZIAŁA!")
    print("   ❌ Jeśli ekran gaśnie lub mruga - coś jest nie tak")
    print()

    input("Naciśnij ENTER aby zatrzymać timer (META)...")

    final_time = manager.finish_timer()
    print(f"\n🏁 META! Czas końcowy: {final_time}")
    print("   Czas powinien być widoczny na tablicy")

    time.sleep(3)

    print("\n✅ Test timera zakończony")
    return True


def main():
    """Główna funkcja testowa"""
    print("="*70)
    print("TEST NAPRAW LED DISPLAY")
    print("="*70)
    print("\nNaprawy:")
    print("  1. Ranking - usunięto mruganie między zmianami")
    print("  2. Timer - naprawiono wyświetlanie płynącego czasu")

    port = input("\nPort (Enter = COM5): ").strip() or "COM5"

    # Initialize
    print(f"\n📡 Łączenie z tablicą na {port}...")
    manager = LEDDisplayManager(port, 9600)

    if not manager.initialize():
        print("\n❌ BŁĄD: Nie udało się połączyć!")
        print("   Sprawdź port i połączenie")
        return False

    print("\n✅ Połączono!")
    time.sleep(1)

    try:
        # Test 1: Ranking fix
        test_ranking_fix(manager)

        # Clear between tests
        print("\n🧹 Czyszczenie tablicy...")
        manager.clear_display()
        time.sleep(2)

        # Test 2: Timer fix
        test_timer_fix(manager)

        print("\n" + "="*60)
        print("PODSUMOWANIE")
        print("="*60)
        print("✅ Test 1: Ranking bez mrugania")
        print("✅ Test 2: Timer START/META z wyświetlaniem czasu")
        print()
        print("Jeśli oba testy działają prawidłowo - naprawy są OK! 🎉")
        print("="*60)

    except KeyboardInterrupt:
        print("\n\n⚠️  Test przerwany")
    finally:
        print("\n🔴 Wyłączanie tablicy...")
        manager.shutdown()
        print("✅ Gotowe!")


if __name__ == "__main__":
    main()
