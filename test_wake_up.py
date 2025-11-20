#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test "obudzenia" tablicy - różne metody
Sprawdzamy co trzeba zrobić aby tablica przyjęła drugą komendę
"""

import serial
import time

# Pakiet inicjalizacyjny
INIT_PACKET = bytes.fromhex('1B 09 0A 00 A4 EB 00 00 0D 0A'.replace(' ', ''))

# Pakiety czasowe
TIME1 = bytes.fromhex('1B 07 3E 00 A1 2A 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 37 38 37 20 54 4F 52 20 31 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))
TIME2 = bytes.fromhex('1B 07 3E 00 8F 5C 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 30 30 27 31 30 22 2E 33 36 32 20 54 4F 52 20 32 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))

# Inne pakiety które mogą być "wakeup"
CMD_06_00 = bytes.fromhex('1B 06 0C 00 FB E8 00 00 00 00 0D 0A'.replace(' ', ''))
CMD_06_03 = bytes.fromhex('1B 06 0C 00 27 73 00 00 03 00 0D 0A'.replace(' ', ''))
EMPTY_LINE1 = bytes.fromhex('1B 07 54 00 14 75 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 2D 2D 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))

def send_init(ser, count=3):
    """Wysyła inicjalizację N razy"""
    print(f"   📤 Inicjalizacja {count}x...")
    for i in range(count):
        ser.write(INIT_PACKET)
        ser.flush()
        time.sleep(0.2)
    time.sleep(0.5)

def main():
    print("="*70)
    print("TEST OBUDZENIA TABLICY")
    print("="*70)
    print("\nSprawdzamy różne metody 'obudzenia' tablicy przed wysłaniem nowego tekstu")

    port = input("\nPort (Enter = COM5): ").strip() or "COM5"

    try:
        print(f"\nŁączę z {port}...")
        ser = serial.Serial(
            port=port,
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
        print("✅ Połączono!")
        time.sleep(0.3)

        # =======================================================================
        # TEST 1: Bez ponownej inicjalizacji (baseline - wiemy że nie działa)
        # =======================================================================
        print("\n" + "="*70)
        print("TEST 1: BEZ ponownej inicjalizacji (baseline)")
        print("="*70)

        send_init(ser)

        print("   📤 Wysyłam czas 1 (00'07\".787 TOR 1)...")
        ser.write(TIME1)
        ser.flush()
        time.sleep(0.3)

        resp = input("\n   👀 Czy wyświetlił czas 1? (t/n): ")
        if resp.lower() != 't':
            print("❌ Już pierwszy nie działa - sprawdź połączenie!")
            return

        print("\n   ⏱️  Czekam 3 sekundy (tablica wyświetla)...")
        time.sleep(3)

        print("   📤 Wysyłam czas 2 (00'10\".362 TOR 2) BEZ inicjalizacji...")
        ser.write(TIME2)
        ser.flush()
        time.sleep(0.3)

        resp = input("   👀 Czy wyświetlił czas 2? (t/n): ")
        test1_result = (resp.lower() == 't')
        print(f"   Wynik: {'✅ DZIAŁA' if test1_result else '❌ NIE DZIAŁA'}")

        # =======================================================================
        # TEST 2: Z ponowną inicjalizacją 3x przed drugim tekstem
        # =======================================================================
        print("\n" + "="*70)
        print("TEST 2: Z PONOWNĄ INICJALIZACJĄ 3x przed drugim tekstem")
        print("="*70)

        send_init(ser)

        print("   📤 Wysyłam czas 1...")
        ser.write(TIME1)
        ser.flush()
        time.sleep(0.3)

        resp = input("   👀 Czy wyświetlił czas 1? (t/n): ")
        if resp.lower() != 't':
            print("⚠️  Czas 1 nie wyświetlił się")

        print("\n   ⏱️  Czekam 3 sekundy...")
        time.sleep(3)

        print("   📤 PONOWNA INICJALIZACJA 3x...")
        send_init(ser, 3)

        print("   📤 Wysyłam czas 2...")
        ser.write(TIME2)
        ser.flush()
        time.sleep(0.3)

        resp = input("   👀 Czy wyświetlił czas 2? (t/n): ")
        test2_result = (resp.lower() == 't')
        print(f"   Wynik: {'✅ DZIAŁA' if test2_result else '❌ NIE DZIAŁA'}")

        # =======================================================================
        # TEST 3: Z ponowną inicjalizacją 1x przed drugim tekstem
        # =======================================================================
        print("\n" + "="*70)
        print("TEST 3: Z PONOWNĄ INICJALIZACJĄ 1x przed drugim tekstem")
        print("="*70)

        send_init(ser, 3)

        print("   📤 Wysyłam czas 1...")
        ser.write(TIME1)
        ser.flush()
        time.sleep(0.3)

        resp = input("   👀 Czy wyświetlił czas 1? (t/n): ")
        if resp.lower() != 't':
            print("⚠️  Czas 1 nie wyświetlił się")

        print("\n   ⏱️  Czekam 3 sekundy...")
        time.sleep(3)

        print("   📤 PONOWNA INICJALIZACJA 1x...")
        send_init(ser, 1)

        print("   📤 Wysyłam czas 2...")
        ser.write(TIME2)
        ser.flush()
        time.sleep(0.3)

        resp = input("   👀 Czy wyświetlił czas 2? (t/n): ")
        test3_result = (resp.lower() == 't')
        print(f"   Wynik: {'✅ DZIAŁA' if test3_result else '❌ NIE DZIAŁA'}")

        # =======================================================================
        # TEST 4: Z komendą CMD_06_00 przed drugim tekstem (może to wakeup?)
        # =======================================================================
        print("\n" + "="*70)
        print("TEST 4: Z komendą CMD_06_00 przed drugim tekstem")
        print("="*70)

        send_init(ser, 3)

        print("   📤 Wysyłam czas 1...")
        ser.write(TIME1)
        ser.flush()
        time.sleep(0.3)

        resp = input("   👀 Czy wyświetlił czas 1? (t/n): ")
        if resp.lower() != 't':
            print("⚠️  Czas 1 nie wyświetlił się")

        print("\n   ⏱️  Czekam 3 sekundy...")
        time.sleep(3)

        print("   📤 Wysyłam CMD_06_00 (możliwy wakeup)...")
        ser.write(CMD_06_00)
        ser.flush()
        time.sleep(0.3)

        print("   📤 Wysyłam czas 2...")
        ser.write(TIME2)
        ser.flush()
        time.sleep(0.3)

        resp = input("   👀 Czy wyświetlił czas 2? (t/n): ")
        test4_result = (resp.lower() == 't')
        print(f"   Wynik: {'✅ DZIAŁA' if test4_result else '❌ NIE DZIAŁA'}")

        # =======================================================================
        # TEST 5: Wysłanie pustej linii przed drugim tekstem (clear?)
        # =======================================================================
        print("\n" + "="*70)
        print("TEST 5: Wysłanie pustej linii przed drugim tekstem")
        print("="*70)

        send_init(ser, 3)

        print("   📤 Wysyłam czas 1...")
        ser.write(TIME1)
        ser.flush()
        time.sleep(0.3)

        resp = input("   👀 Czy wyświetlił czas 1? (t/n): ")
        if resp.lower() != 't':
            print("⚠️  Czas 1 nie wyświetlił się")

        print("\n   ⏱️  Czekam 3 sekundy...")
        time.sleep(3)

        print("   📤 Wysyłam pustą linię (clear)...")
        ser.write(EMPTY_LINE1)
        ser.flush()
        time.sleep(0.3)

        print("   📤 Wysyłam czas 2...")
        ser.write(TIME2)
        ser.flush()
        time.sleep(0.3)

        resp = input("   👀 Czy wyświetlił czas 2? (t/n): ")
        test5_result = (resp.lower() == 't')
        print(f"   Wynik: {'✅ DZIAŁA' if test5_result else '❌ NIE DZIAŁA'}")

        # =======================================================================
        # TEST 6: Krótszy delay (może tablica ma timeout?)
        # =======================================================================
        print("\n" + "="*70)
        print("TEST 6: KRÓTKI delay (0.5s) między komendami")
        print("="*70)

        send_init(ser, 3)

        print("   📤 Wysyłam czas 1...")
        ser.write(TIME1)
        ser.flush()
        time.sleep(0.3)

        resp = input("   👀 Czy wyświetlił czas 1? (t/n): ")
        if resp.lower() != 't':
            print("⚠️  Czas 1 nie wyświetlił się")

        print("\n   ⏱️  Czekam TYLKO 0.5 sekundy...")
        time.sleep(0.5)

        print("   📤 Wysyłam czas 2 (zaraz po pierwszym)...")
        ser.write(TIME2)
        ser.flush()
        time.sleep(0.3)

        resp = input("   👀 Czy wyświetlił czas 2? (t/n): ")
        test6_result = (resp.lower() == 't')
        print(f"   Wynik: {'✅ DZIAŁA' if test6_result else '❌ NIE DZIAŁA'}")

        # =======================================================================
        # PODSUMOWANIE
        # =======================================================================
        print("\n" + "="*70)
        print("📊 PODSUMOWANIE TESTÓW")
        print("="*70)
        print(f"TEST 1: Bez re-init                    : {'✅' if test1_result else '❌'}")
        print(f"TEST 2: Re-init 3x przed czas2         : {'✅' if test2_result else '❌'}")
        print(f"TEST 3: Re-init 1x przed czas2         : {'✅' if test3_result else '❌'}")
        print(f"TEST 4: CMD_06_00 przed czas2          : {'✅' if test4_result else '❌'}")
        print(f"TEST 5: Empty line przed czas2         : {'✅' if test5_result else '❌'}")
        print(f"TEST 6: Krótki delay (0.5s)            : {'✅' if test6_result else '❌'}")

        print("\n" + "="*70)
        if test2_result:
            print("💡 WNIOSEK: Trzeba wysłać RE-INIT 3x przed każdą nową komendą!")
        elif test3_result:
            print("💡 WNIOSEK: Trzeba wysłać RE-INIT 1x przed każdą nową komendą!")
        elif test4_result:
            print("💡 WNIOSEK: Trzeba wysłać CMD_06_00 przed każdą nową komendą!")
        elif test6_result:
            print("💡 WNIOSEK: Problem jest w długim opóźnieniu - tablica ma timeout!")
        else:
            print("⚠️  WNIOSEK: Żaden z testów nie zadziałał - trzeba dalej szukać...")
        print("="*70)

        ser.close()

    except Exception as e:
        print(f"\n❌ BŁĄD: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
    input("\nNaciśnij Enter...")
