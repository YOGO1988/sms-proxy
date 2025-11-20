#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test BEZ czyszczenia - sprawdzamy czy pakiety TIME mogą nadpisać tekst producenta
"""

import serial
import time

# Pakiet inicjalizacyjny
INIT = bytes.fromhex('1B 09 0A 00 A4 EB 00 00 0D 0A')

# Pakiet czasowy linia 1 - DOKŁADNIE z oryginalnego programu (00'02".074)
TIME_L1 = bytes.fromhex('1B 07 3A 00 EB 4F 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 32 22 2E 30 37 34 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A')

# Pakiet czasowy linia 2 - DOKŁADNIE z oryginalnego programu (00'02".074)
TIME_L2 = bytes.fromhex('1B 07 3A 00 65 44 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 30 30 27 30 32 22 2E 30 37 34 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A')

port = input("Port (Enter = COM5): ").strip() or "COM5"

try:
    print(f"\nŁączę z {port}...")
    ser = serial.Serial(port=port, baudrate=9600, timeout=1)
    print("✅ Połączono!")

    print("\n" + "="*70)
    print("KROK 1: INIT (3x)")
    print("="*70)
    for i in range(3):
        ser.write(INIT)
        ser.flush()
        print(f"  📤 INIT #{i+1}")
        time.sleep(0.2)

    print("\n⏱️  Czekam 1 sekundę...")
    time.sleep(1.0)

    print("\n" + "="*70)
    print("KROK 2: Wyświetlenie czasu na LINII 1")
    print("="*70)
    print("  📤 TIME L1: 00'02\".074")
    ser.write(TIME_L1)
    ser.flush()

    print("\n⏱️  Czekam 2 sekundy...")
    time.sleep(2.0)

    print("\n" + "="*70)
    print("KROK 3: Wyświetlenie czasu na LINII 2 (próba nadpisania tekstu producenta)")
    print("="*70)
    print("  📤 TIME L2: 00'02\".074")
    ser.write(TIME_L2)
    ser.flush()

    print("\n⏱️  Czekam 2 sekundy...")
    time.sleep(2.0)

    print("\n" + "="*70)
    print("KROK 4: Wysyłam ponownie czas na LINII 2 (może potrzebuje 2x?)")
    print("="*70)
    print("  📤 TIME L2: 00'02\".074 (drugi raz)")
    ser.write(TIME_L2)
    ser.flush()

    print("\n⏱️  Czekam 2 sekundy...")
    time.sleep(2.0)

    print("\n" + "="*70)
    print("KROK 5: Wysyłam ponownie czas na LINII 2 (trzeci raz)")
    print("="*70)
    print("  📤 TIME L2: 00'02\".074 (trzeci raz)")
    ser.write(TIME_L2)
    ser.flush()

    print("\n✅ Test zakończony!")
    print("\n" + "="*70)
    print("❓ CO WIDZISZ NA WYŚWIETLACZU?")
    print("="*70)
    print("\n📋 Odpowiedz na pytania:")
    print("   1. Czy linia 1 pokazuje: 00'02\".074  -")
    print("   2. Czy linia 2 nadal pokazuje tekst producenta?")
    print("   3. Czy linia 2 pokazuje: 00'02\".074  -")
    print("   4. Czy linia 2 coś miga/migało?")
    print("   5. Coś innego?")

    ser.close()

except Exception as e:
    print(f"\n❌ BŁĄD: {e}")
    import traceback
    traceback.print_exc()

input("\nNaciśnij Enter aby zakończyć...")
