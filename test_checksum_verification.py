#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST: Czy tablica NAPRAWDĘ sprawdza checksum?

Wyślemy 3 pakiety:
1. Oryginalny (działa na pewno)
2. Zmieniony tekst, STARY checksum (jeśli działa = tablica NIE sprawdza)
3. Zmieniony tekst, ZEPSUTY checksum (jeśli NIE działa = tablica sprawdza)
"""

import serial
import time

# Pakiet inicjalizacyjny
INIT_PACKET = bytes.fromhex('1B 09 0A 00 A4 EB 00 00 0D 0A'.replace(' ', ''))

# Oryginalny pakiet (wiemy że działa)
ORIGINAL = bytes.fromhex('1B 07 3E 00 A1 2A 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 37 38 37 20 54 4F 52 20 31 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))

def send_init(ser, count=3):
    """Wysyła inicjalizację"""
    print(f"   📤 Inicjalizacja {count}x...")
    for i in range(count):
        ser.write(INIT_PACKET)
        ser.flush()
        time.sleep(0.2)
    time.sleep(0.5)

def main():
    print("="*70)
    print("TEST WERYFIKACJI CHECKSUM")
    print("="*70)
    print("\nSprawdzimy czy tablica NAPRAWDĘ sprawdza checksum")

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
        # TEST 1: Oryginalny pakiet (BASELINE)
        # =======================================================================
        print("\n" + "="*70)
        print("TEST 1: ORYGINALNY pakiet")
        print("="*70)
        print("Tekst: \"00'07\".787 TOR 1\"")
        print("Checksum: 0xA1 0x2A (ORYGINALNY)")

        send_init(ser)

        ser.write(ORIGINAL)
        ser.flush()
        time.sleep(0.3)

        resp = input("\n👀 Czy wyświetlił \"00'07\".787 TOR 1\"? (t/n): ")
        if resp.lower() != 't':
            print("❌ Oryginalny nie działa - sprawdź połączenie!")
            ser.close()
            return

        print("✅ OK - oryginalny działa")
        time.sleep(2)

        # =======================================================================
        # TEST 2: Zmieniony tekst, STARY checksum
        # =======================================================================
        print("\n" + "="*70)
        print("TEST 2: ZMIENIONY tekst, STARY checksum")
        print("="*70)

        # Skopiuj pakiet i zmień TYLKO tekst (od bajtu 22)
        modified = bytearray(ORIGINAL)
        new_text = "00'99\".999 XXX A"
        new_text_padded = new_text.ljust(36)
        modified[22:22+36] = new_text_padded.encode('ascii')

        print(f"Nowy tekst: \"{new_text}\"")
        print(f"Checksum: 0x{modified[4]:02X} 0x{modified[5]:02X} (NIEZMIENIONY - stary!)")

        send_init(ser)

        ser.write(bytes(modified))
        ser.flush()
        time.sleep(0.3)

        resp = input(f"\n👀 Czy wyświetlił \"{new_text}\"? (t/n): ")
        test2_ok = (resp.lower() == 't')

        if test2_ok:
            print("✅ DZIAŁA!")
        else:
            print("❌ NIE DZIAŁA")

        time.sleep(2)

        # =======================================================================
        # TEST 3: Zmieniony tekst, ZEPSUTY checksum
        # =======================================================================
        print("\n" + "="*70)
        print("TEST 3: ZMIENIONY tekst, ZEPSUTY checksum")
        print("="*70)

        # Skopiuj pakiet, zmień tekst I ZEPSUJ checksum
        modified2 = bytearray(ORIGINAL)
        new_text2 = "00'88\".888 YYY B"
        new_text2_padded = new_text2.ljust(36)
        modified2[22:22+36] = new_text2_padded.encode('ascii')
        # ZEPSUJ checksum
        modified2[4] = 0xFF
        modified2[5] = 0xFF

        print(f"Nowy tekst: \"{new_text2}\"")
        print(f"Checksum: 0x{modified2[4]:02X} 0x{modified2[5]:02X} (ZEPSUTY!)")

        send_init(ser)

        ser.write(bytes(modified2))
        ser.flush()
        time.sleep(0.3)

        resp = input(f"\n👀 Czy wyświetlił \"{new_text2}\"? (t/n): ")
        test3_ok = (resp.lower() == 't')

        if test3_ok:
            print("✅ DZIAŁA (pomimo zepsutego checksum!)")
        else:
            print("❌ NIE DZIAŁA")

        # =======================================================================
        # WNIOSKI
        # =======================================================================
        print("\n" + "="*70)
        print("📊 WYNIKI TESTÓW")
        print("="*70)
        print(f"TEST 1: Oryginalny pakiet            : ✅ (zawsze działa)")
        print(f"TEST 2: Zmieniony tekst, stary CRC   : {'✅' if test2_ok else '❌'}")
        print(f"TEST 3: Zmieniony tekst, zepsuty CRC : {'✅' if test3_ok else '❌'}")

        print("\n" + "="*70)
        print("💡 WNIOSKI:")
        print("="*70)

        if test2_ok and test3_ok:
            print("✅ Tablica NIE sprawdza checksum wcale!")
            print("   Możesz zmieniać tekst bez przeliczania checksum.")
        elif test2_ok and not test3_ok:
            print("⚠️  Tablica sprawdza czy checksum NIE jest zepsuty,")
            print("   ale przyjmuje stary checksum (nie przelicza).")
            print("   Możesz używać oryginalnego checksum dla nowych tekstów.")
        elif not test2_ok and not test3_ok:
            print("❌ Tablica SPRAWDZA checksum!")
            print("   Musimy znaleźć algorytm obliczania checksum.")
        else:
            print("❓ Dziwny wynik - powtórz test")
        print("="*70)

        ser.close()

    except Exception as e:
        print(f"\n❌ BŁĄD: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
    input("\nNaciśnij Enter...")
