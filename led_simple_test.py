#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LED Simple Test - Prosty test wszystkich pakietów
Używa tych samych pakietów co led_display_final.py
"""

import serial
import time

# WORKING PACKETS - identyczne jak w led_display_final.py
PACKETS = {
    'name_tymon': bytes.fromhex('1B 07 52 00 AA C2 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 54 79 6D 6F 6E 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 2D 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),
    'lane1': bytes.fromhex('1B 08 E8 00 E8 71 00 00 01 00 00 00 00 00 00 00 01 00 0A 00 00 00 00 00 00 00 00 00 5B 00 54 4F 52 20 31 20 20 20 30 29 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 0D 0A'.replace(' ', '')),
    'lane2': bytes.fromhex('1B 08 E8 00 F8 77 00 00 01 00 00 00 00 00 00 00 02 00 0A 00 00 00 10 00 00 00 00 00 38 00 54 4F 52 20 32 20 20 20 30 29 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 0D 0A'.replace(' ', '')),
    'time_7sec': bytes.fromhex('1B 07 3A 00 51 8B 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 34 36 37 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),
    'time_7sec_tor1': bytes.fromhex('1B 07 3E 00 A1 2A 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 37 38 37 20 54 4F 52 20 31 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),
    'time_10sec_tor2': bytes.fromhex('1B 07 3E 00 8F 5C 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 30 30 27 31 30 22 2E 33 36 32 20 54 4F 52 20 32 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),
}

def run_simple_test(port='COM5', baudrate=9600):
    """Prosty test - dokładnie jak test_all() z led_display_final.py"""
    print("\n" + "="*60)
    print("LED SIMPLE TEST")
    print("="*60)
    print(f"\nPort: {port}")
    print(f"Baudrate: {baudrate}")

    try:
        # Połącz
        print("\nŁączę z tablicą...")
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
        print("✅ Połączono!")
        time.sleep(0.3)

        # Testy - dokładnie ta sama kolejność jak w led_display_final.py
        tests = [
            ('name_tymon', "Event name: Tymon"),
            ('time_7sec', "Time 7.467s (no TOR)"),
            ('time_7sec_tor1', "Time 7.787s TOR 1"),
            ('time_10sec_tor2', "Time 10.362s TOR 2"),
            ('lane1', "Lane info TOR 1"),
            ('lane2', "Lane info TOR 2"),
        ]

        print("\n" + "="*60)
        print("WYSYŁAM PAKIETY...")
        print("="*60)

        for packet_name, desc in tests:
            packet = PACKETS[packet_name]
            print(f"\n📤 {desc}")
            print(f"   Pakiet: {packet_name}")
            print(f"   Długość: {len(packet)} bajtów")

            ser.write(packet)
            ser.flush()

            time.sleep(2.0)
            print("   ✅ Wysłano")

        print("\n" + "="*60)
        print("✅ TEST ZAKOŃCZONY")
        print("="*60)
        print("\nCzy tablica wyświetliła poprawnie wszystkie informacje?")
        print("Jeśli tak - kod działa!")

        ser.close()
        return True

    except Exception as e:
        print(f"\n❌ BŁĄD: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("LED SIMPLE TEST SCRIPT")
    print("Bazuje na działającej funkcji z led_display_final.py")
    print("="*60)

    port = input("\nPort (Enter = COM5): ").strip() or "COM5"

    print("\n⚠️  Upewnij się że tablica LED jest WŁĄCZONA!")
    input("Naciśnij Enter aby rozpocząć test...\n")

    run_simple_test(port, 9600)

    input("\nNaciśnij Enter aby zakończyć...")
