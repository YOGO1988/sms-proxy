#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test z INICJALIZACJĄ (może tablica tego wymaga?)
"""

import serial
import time

# Pakiet inicjalizacyjny
INIT_PACKET = bytes.fromhex('1B 09 0A 00 A4 EB 00 00 0D 0A'.replace(' ', ''))

# Działający pakiet czasu
TIME_PACKET = bytes.fromhex('1B 07 3E 00 A1 2A 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 37 38 37 20 54 4F 52 20 31 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))

def main():
    print("="*60)
    print("TEST Z INICJALIZACJĄ")
    print("="*60)

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

        # KROK 1: Inicjalizacja (3x jak w oryginalnym programie)
        print("\n📤 KROK 1: Inicjalizacja (set9600) 3x...")
        for i in range(3):
            ser.write(INIT_PACKET)
            ser.flush()
            time.sleep(0.2)
        print("✅ Wysłano inicjalizację")
        time.sleep(1.0)

        # KROK 2: Wyślij czas
        print("\n📤 KROK 2: Wysyłam czas \"00'07\".787 TOR 1\"...")
        ser.write(TIME_PACKET)
        ser.flush()
        time.sleep(0.3)

        response = input("\n👀 Czy tablica wyświetliła czas? (t/n): ")

        if response.lower() == 't':
            print("\n✅ Działa z inicjalizacją!")

            # Test zmiany tekstu
            print("\n📤 KROK 3: Test zmiany tekstu...")
            modified = bytearray(TIME_PACKET)
            new_text = "00'99\".999 TOR 1"
            modified[22:22+36] = new_text.ljust(36).encode('ascii')

            ser.write(bytes(modified))
            ser.flush()
            time.sleep(0.3)

            response2 = input("\n👀 Czy wyświetliło \"00'99\".999\"? (t/n): ")
            if response2.lower() == 't':
                print("\n🎉 SUKCES! Możemy zmieniać tekst bez checksum!")
            else:
                print("\n⚠️  Checksum jest sprawdzany")
        else:
            print("\n❌ Nawet z inicjalizacją nie działa")

        ser.close()

    except Exception as e:
        print(f"\n❌ BŁĄD: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
    input("\nNaciśnij Enter...")
