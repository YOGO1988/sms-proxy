#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test: Czy tablica sprawdza checksum?
Bierzemy działający pakiet i zmieniamy TYLKO tekst ASCII (bez checksum)
"""

import serial
import time

# Oryginalny działający pakiet: time_05_429 = "00'05".429  -"
ORIGINAL_PACKET = bytes.fromhex('1B 07 3A 00 E9 7F 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 35 22 2E 34 32 39 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))

def modify_text_only(packet, new_text):
    """
    Modyfikuje TYLKO część tekstową pakietu (od bajtu 22)
    Checksum pozostaje NIEZMIENIONY!

    Args:
        packet: oryginalny pakiet (bytes)
        new_text: nowy tekst ASCII (string)

    Returns:
        bytes: zmodyfikowany pakiet
    """
    # Konwertuj na bytearray aby móc modyfikować
    modified = bytearray(packet)

    # Część tekstowa zaczyna się od bajtu 22, kończy przed 0D 0A
    text_start = 22
    text_end = len(packet) - 2  # Przed 0D 0A

    # Długość dostępnej przestrzeni na tekst
    text_space = text_end - text_start

    # Przygotuj tekst: dopełnij spacjami do pełnej długości
    text_bytes = new_text.ljust(text_space).encode('ascii')[:text_space]

    # Zastąp tekst
    modified[text_start:text_end] = text_bytes

    return bytes(modified)

def test_with_serial(port='COM5', baudrate=9600):
    """Test na prawdziwym porcie szeregowym"""

    print("="*80)
    print("TEST: Czy tablica LED sprawdza checksum?")
    print("="*80)

    try:
        # Otwórz port
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
        print(f"\n✅ Połączono z {port} @ {baudrate} baud")
        time.sleep(0.3)

        # TEST 1: Oryginalny pakiet (powinien zadziałać)
        print("\n" + "-"*80)
        print("TEST 1: Oryginalny pakiet")
        print("-"*80)
        original_text = ORIGINAL_PACKET[22:-2].decode('ascii')
        print(f"Tekst: \"{original_text.strip()}\"")
        print(f"Checksum: 0x{ORIGINAL_PACKET[4]:02X}{ORIGINAL_PACKET[5]:02X}")

        ser.write(ORIGINAL_PACKET)
        ser.flush()
        time.sleep(2.0)

        input("\n👀 Czy tablica wyświetliła \"00'05\".429  -\"? (Enter aby kontynuować)")

        # TEST 2: Zmieniony tekst, TEN SAM checksum
        print("\n" + "-"*80)
        print("TEST 2: Zmieniony tekst (checksum NIEZMIENIONY)")
        print("-"*80)

        modified1 = modify_text_only(ORIGINAL_PACKET, "00'99\".999  -")
        modified_text = modified1[22:-2].decode('ascii')
        print(f"Tekst: \"{modified_text.strip()}\"")
        print(f"Checksum: 0x{modified1[4]:02X}{modified1[5]:02X} (ten sam!)")

        ser.write(modified1)
        ser.flush()
        time.sleep(2.0)

        response = input("\n👀 Czy tablica wyświetliła \"00'99\".999  -\"? (t/n): ")

        if response.lower() == 't':
            print("\n🎉 SUKCES! Tablica NIE sprawdza checksum!")
            print("   Możemy generować dowolne pakiety zmieniając tylko tekst!")
            checksum_validated = False
        else:
            print("\n⚠️  Tablica odrzuciła pakiet - checksum JEST sprawdzany")
            checksum_validated = True

        # TEST 3: Więcej testów jeśli checksum nie jest sprawdzany
        if not checksum_validated:
            print("\n" + "-"*80)
            print("TEST 3: Różne czasy z tym samym checksumem")
            print("-"*80)

            test_times = [
                "00'12\".345  -",
                "01'23\".456  -",
                "00'00\".001  -",
            ]

            for test_text in test_times:
                modified = modify_text_only(ORIGINAL_PACKET, test_text)
                print(f"\nWysyłam: \"{test_text}\"")
                ser.write(modified)
                ser.flush()
                time.sleep(2.5)

            print("\n✅ Jeśli wszystkie czasy wyświetliły się poprawnie:")
            print("   Możemy używać jednego checksum dla wszystkich pakietów!")

        ser.close()
        return not checksum_validated

    except serial.SerialException as e:
        print(f"\n❌ Błąd portu szeregowego: {e}")
        return None
    except Exception as e:
        print(f"\n❌ Błąd: {e}")
        import traceback
        traceback.print_exc()
        return None

def demo_without_hardware():
    """Demo bez sprzętu - pokaż jak to działa"""

    print("="*80)
    print("DEMO: Modyfikacja pakietów (bez sprzętu)")
    print("="*80)

    print("\nOryginalny pakiet:")
    print(f"  HEX: {ORIGINAL_PACKET.hex(' ')[:60]}...")
    print(f"  Tekst: \"{ORIGINAL_PACKET[22:-2].decode('ascii').strip()}\"")
    print(f"  Checksum: 0x{ORIGINAL_PACKET[4]:02X}{ORIGINAL_PACKET[5]:02X}")

    # Testy modyfikacji
    test_cases = [
        "00'12\".345  -",
        "00'99\".888  -",
        "01'23\".456  -",
        "Hello World!!",
    ]

    for new_text in test_cases:
        modified = modify_text_only(ORIGINAL_PACKET, new_text)
        mod_text = modified[22:-2].decode('ascii').strip()

        print(f"\nNowy tekst: \"{new_text}\"")
        print(f"  → Pakiet: {modified.hex(' ')[:60]}...")
        print(f"  → Wyświetli: \"{mod_text}\"")
        print(f"  → Checksum: 0x{modified[4]:02X}{modified[5]:02X} (NIEZMIENIONY!)")

if __name__ == "__main__":
    print("="*80)
    print("TEST WALIDACJI CHECKSUM")
    print("="*80)

    print("\nCel: Sprawdzić czy tablica LED weryfikuje checksum")
    print("Jeśli NIE - możemy generować dowolne pakiety!")

    choice = input("\n1. Test z tablicą LED (wymaga sprzętu)\n2. Demo bez sprzętu\n\nWybór (1/2): ").strip()

    if choice == '1':
        port = input("\nPort (Enter = COM5): ").strip() or "COM5"
        print("\n⚠️  Upewnij się że tablica LED jest WŁĄCZONA!")
        input("Naciśnij Enter aby rozpocząć...\n")

        result = test_with_serial(port, 9600)

        if result == True:
            print("\n" + "="*80)
            print("✅ WYNIK: Checksum NIE jest sprawdzany!")
            print("="*80)
            print("\nMożemy teraz:")
            print("1. Użyć jednego checksum dla wszystkich pakietów")
            print("2. Generować dowolne czasy i teksty")
            print("3. Zaimplementować dynamiczne wyświetlanie w systemie")
        elif result == False:
            print("\n" + "="*80)
            print("⚠️  WYNIK: Checksum JEST sprawdzany")
            print("="*80)
            print("\nMusimy:")
            print("1. Znaleźć algorytm checksum (reverse engineering)")
            print("2. Lub użyć tylko z góry nagranych pakietów")
    else:
        demo_without_hardware()

    input("\nNaciśnij Enter aby zakończyć...")
