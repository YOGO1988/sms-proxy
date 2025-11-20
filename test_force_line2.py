#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test AGRESYWNY dla linii 2 - wielokrotnie wysyła pakiet TIME
aby sprawdzić czy w końcu nadpisze tekst producenta
"""

import serial
import time

# Pakiet inicjalizacyjny
INIT = bytes.fromhex('1B 09 0A 00 A4 EB 00 00 0D 0A')

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
    print("KROK 2: BOMBARDOWANIE LINII 2 pakietami TIME")
    print("Wysyłam 10 razy z przerwami 0.5s")
    print("="*70)

    for i in range(10):
        print(f"  📤 TIME L2 #{i+1}/10: 00'02\".074")
        ser.write(TIME_L2)
        ser.flush()
        time.sleep(0.5)

    print("\n✅ Test zakończony!")
    print("\n" + "="*70)
    print("❓ CO WIDZISZ NA WYŚWIETLACZU?")
    print("="*70)
    print("\n📋 Odpowiedz:")
    print("   1. Czy linia 2 NADAL pokazuje tekst producenta?")
    print("   2. Czy linia 2 pokazuje: 00'02\".074  -")
    print("   3. Czy coś migało podczas wysyłania?")
    print("   4. Coś innego?")

    ser.close()

except Exception as e:
    print(f"\n❌ BŁĄD: {e}")
    import traceback
    traceback.print_exc()

input("\nNaciśnij Enter aby zakończyć...")
