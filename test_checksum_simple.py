#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ULTRA-PROSTY TEST checksum
Bazuje DOKŁADNIE na led_display_final.py (który działa)
"""

import serial
import time

# Działający pakiet z led_display_final.py
WORKING_PACKET = bytes.fromhex('1B 07 3E 00 A1 2A 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 37 38 37 20 54 4F 52 20 31 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))

def main():
    print("="*60)
    print("ULTRA-PROSTY TEST")
    print("="*60)

    port = input("\nPort (Enter = COM5): ").strip() or "COM5"

    try:
        # Połącz - DOKŁADNIE jak w led_display_final.py
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

        # TEST 1: Oryginalny pakiet (MUSI zadziałać!)
        print("\n" + "="*60)
        print("TEST 1: Oryginalny pakiet (time_7sec_tor1)")
        print("="*60)
        print("Tekst w pakiecie: \"00'07\".787 TOR 1\"")
        print("Checksum: 0xA1 0x2A")

        ser.write(WORKING_PACKET)
        ser.flush()
        time.sleep(0.3)

        response = input("\n👀 Czy tablica wyświetliła \"00'07\".787 TOR 1\"? (t/n): ")

        if response.lower() != 't':
            print("\n❌ Oryginalny pakiet nie zadziałał!")
            print("Problem z połączeniem lub tablicą!")
            ser.close()
            return

        print("✅ OK! Oryginalny pakiet działa.")

        # TEST 2: Zmieńmy TYLKO tekst (od bajtu 22)
        print("\n" + "="*60)
        print("TEST 2: Zmieniony tekst, ten sam checksum")
        print("="*60)

        # Kopiuj pakiet
        modified = bytearray(WORKING_PACKET)

        # Nowy tekst: "00'99".999 TOR 1"
        new_text = "00'99\".999 TOR 1"
        # Dopełnij spacjami do długości 36 (długość tekstu w pakiecie)
        new_text_padded = new_text.ljust(36)

        # Zastąp tekst od bajtu 22
        modified[22:22+36] = new_text_padded.encode('ascii')

        print(f"Nowy tekst: \"{new_text}\"")
        print(f"Checksum: 0x{modified[4]:02X} 0x{modified[5]:02X} (NIEZMIENIONY!)")
        print(f"\nPakiet oryginalny: {WORKING_PACKET.hex()[:40]}...")
        print(f"Pakiet zmieniony:  {modified.hex()[:40]}...")

        ser.write(bytes(modified))
        ser.flush()
        time.sleep(0.3)

        response = input("\n👀 Czy tablica wyświetliła \"00'99\".999 TOR 1\"? (t/n): ")

        if response.lower() == 't':
            print("\n" + "="*60)
            print("🎉 SUKCES!!!")
            print("="*60)
            print("Tablica NIE sprawdza checksum!")
            print("Możemy generować DOWOLNE pakiety!")

            # TEST 3: Więcej testów
            print("\n" + "="*60)
            print("TEST 3: Różne czasy")
            print("="*60)

            test_times = [
                "00'12\".345 TOR 1",
                "01'23\".456 TOR 1",
                "00'00\".001 TOR 1",
            ]

            for test_text in test_times:
                print(f"\nWysyłam: \"{test_text}\"")
                modified = bytearray(WORKING_PACKET)
                modified[22:22+36] = test_text.ljust(36).encode('ascii')
                ser.write(bytes(modified))
                ser.flush()
                time.sleep(2.0)

            print("\n✅ Jeśli wszystkie czasy się wyświetliły - SUKCES!")

        else:
            print("\n" + "="*60)
            print("⚠️  Tablica sprawdza checksum")
            print("="*60)
            print("Musimy znaleźć algorytm checksum...")

        ser.close()

    except Exception as e:
        print(f"\n❌ BŁĄD: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
    input("\nNaciśnij Enter aby zakończyć...")
