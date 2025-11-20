#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimalny test - wysyła tylko init, clear i jeden pakiet czasowy
Sprawdza czy podstawowa komunikacja działa
"""

import serial
import time

# Pakiet inicjalizacyjny
INIT = bytes.fromhex('1B 09 0A 00 A4 EB 00 00 0D 0A')

# Pakiet czyszczący linię 1
CLEAR_L1 = bytes.fromhex('1B 08 E8 00 22 71 00 00 01 00 00 00 00 00 00 00 01 00 0A 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 0D 0A')

# Pakiet czyszczący linię 2
CLEAR_L2 = bytes.fromhex('1B 08 E8 00 23 E6 00 00 01 00 00 00 00 00 00 00 02 00 0A 00 00 00 10 00 00 00 00 00 38 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 0D 0A')

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
    time.sleep(0.3)

    print("\n" + "="*70)
    print("KROK 2: CLEAR linia 1 (2x)")
    print("="*70)
    ser.write(CLEAR_L1)
    ser.flush()
    print("  📤 CLEAR L1 #1")
    time.sleep(0.05)
    ser.write(CLEAR_L1)
    ser.flush()
    print("  📤 CLEAR L1 #2")
    time.sleep(0.05)

    print("\n" + "="*70)
    print("KROK 3: CLEAR linia 2 (2x)")
    print("="*70)
    ser.write(CLEAR_L2)
    ser.flush()
    print("  📤 CLEAR L2 #1")
    time.sleep(0.05)
    ser.write(CLEAR_L2)
    ser.flush()
    print("  📤 CLEAR L2 #2")
    time.sleep(0.3)

    print("\n" + "="*70)
    print("KROK 4: Wyświetlenie czasu 00'02\".074 na OBU liniach")
    print("="*70)
    ser.write(TIME_L1)
    ser.flush()
    print("  📤 TIME L1: 00'02\".074")
    time.sleep(0.05)
    ser.write(TIME_L2)
    ser.flush()
    print("  📤 TIME L2: 00'02\".074")

    print("\n✅ Test zakończony!")
    print("\n❓ Co widzisz na wyświetlaczu?")
    print("   A) Obie linie wyczyszczone (puste)")
    print("   B) Linia 1: 00'02\".074  -")
    print("   C) Linia 2: 00'02\".074  -")
    print("   D) Coś innego")

    ser.close()

except Exception as e:
    print(f"\n❌ BŁĄD: {e}")
    import traceback
    traceback.print_exc()

input("\nNaciśnij Enter aby zakończyć...")
