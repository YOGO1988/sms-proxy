#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wysyła DOKŁADNIE te same bajty co oryginalny program
Testuje różne ustawienia portu
"""

import serial
import time
import sys


def hex_to_bytes(hex_string):
    """Convert HEX string to bytes"""
    hex_clean = hex_string.replace(" ", "").replace("\n", "")
    return bytes.fromhex(hex_clean)


def test_port_settings(port='COM5'):
    """Test different serial port settings"""

    # Bajty z Twojego DZIAŁAJĄCEGO programu - Set9600 (inicjalizacja)
    INIT_BYTES = "1B 09 0A 00 A4 EB 00 00 0D 0A"

    # Bajty wyświetlenia czasu - z Twojego programu
    TIME_DISPLAY_BYTES = """1B 07 3E 00 8D 57 00 00 00 00 00 00 00 00 00 00
00 00 00 00 0A 00 30 30 27 30 37 22 2E 38 33 35
20 54 4F 52 20 31 20 20 20 20 20 20 20 20 20 20
20 20 20 20 20 20 20 20 20 20 20 20 0D 0A"""

    # Clear command - z Twojego programu
    CLEAR_BYTES = "1B 08 EA 00 33 BD 00 00 00 00 00 00 00 00 00 00 00 10 00 00 0A 00"

    init_cmd = hex_to_bytes(INIT_BYTES)
    time_cmd = hex_to_bytes(TIME_DISPLAY_BYTES)
    clear_cmd = hex_to_bytes(CLEAR_BYTES)

    print("=" * 70)
    print("TEST RÓŻNYCH USTAWIEŃ PORTU")
    print("=" * 70)
    print(f"Port: {port}")
    print()

    # Test różnych kombinacji ustawień
    test_configs = [
        {"name": "Standard (8N1)", "params": {"bytesize": 8, "parity": 'N', "stopbits": 1}},
        {"name": "8E1 (Even parity)", "params": {"bytesize": 8, "parity": 'E', "stopbits": 1}},
        {"name": "8O1 (Odd parity)", "params": {"bytesize": 8, "parity": 'O', "stopbits": 1}},
        {"name": "8N2 (2 stop bits)", "params": {"bytesize": 8, "parity": 'N', "stopbits": 2}},
        {"name": "7E1", "params": {"bytesize": 7, "parity": 'E', "stopbits": 1}},
    ]

    for i, config in enumerate(test_configs, 1):
        print(f"\n{'─' * 70}")
        print(f"TEST {i}/{len(test_configs)}: {config['name']}")
        print(f"{'─' * 70}")

        try:
            # Otwórz port z tymi ustawieniami
            ser = serial.Serial(
                port=port,
                baudrate=9600,
                timeout=1,
                **config['params']
            )

            print(f"✓ Port otwarty: {ser.port}")
            print(f"  Ustawienia: {ser.baudrate} baud, {ser.bytesize}{ser.parity}{ser.stopbits}")
            print()

            # KROK 1: Inicjalizacja (wysłana 3x jak w oryginalnym programie)
            print("KROK 1: Wysyłam inicjalizację Set9600 (3x)...")
            for j in range(3):
                ser.write(init_cmd)
                print(f"  → Wysłano: {init_cmd.hex().upper()}")
                time.sleep(0.1)  # Krótka pauza między komendami

            time.sleep(0.5)

            # Sprawdź odpowiedź
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting)
                print(f"  ← ODPOWIEDŹ: {response.hex().upper()}")
            else:
                print(f"  ← Brak odpowiedzi")

            print()
            print("KROK 2: Wysyłam wyświetlenie czasu...")
            ser.write(time_cmd)
            print(f"  → Wysłano {len(time_cmd)} bajtów")
            print(f"  → HEX: {time_cmd.hex().upper()}")

            time.sleep(0.5)

            # Sprawdź odpowiedź
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting)
                print(f"  ← ODPOWIEDŹ: {response.hex().upper()}")
            else:
                print(f"  ← Brak odpowiedzi")

            print()
            print(">>> PATRZ NA TABLICĘ! <<<")
            print("    Czy wyświetliło się: 00'07\".835 TOR 1 ?")
            print()

            ser.close()

            result = input(f"Czy test {config['name']} ZADZIAŁAŁ? (t/n): ").strip().lower()

            if result == 't':
                print()
                print("!" * 70)
                print("ZNALEZIONO DZIAŁAJĄCE USTAWIENIE!")
                print(f"Użyj: {config['name']}")
                print(f"Parametry: baudrate=9600, {config['params']}")
                print("!" * 70)
                return config

        except Exception as e:
            print(f"✗ BŁĄD: {e}")

        print()
        input("Naciśnij Enter aby kontynuować do kolejnego testu...")

    print()
    print("=" * 70)
    print("Żaden test nie zadziałał :(")
    print("=" * 70)
    return None


def send_exact_sequence(port='COM5', params=None):
    """Wyślij dokładną sekwencję z działającego programu"""

    if params is None:
        params = {"bytesize": 8, "parity": 'N', "stopbits": 1}

    print()
    print("=" * 70)
    print("WYSYŁAM DOKŁADNĄ SEKWENCJĘ Z DZIAŁAJĄCEGO PROGRAMU")
    print("=" * 70)

    # To są DOKŁADNE sekwencje z Twojego działającego programu
    sequences = {
        "Init (Set9600 - 3x)": "1B 09 0A 00 A4 EB 00 00 0D 0A",
        "Display time TOR 1": """1B 07 3E 00 8D 57 00 00 00 00 00 00 00 00 00 00
00 00 00 00 0A 00 30 30 27 30 37 22 2E 38 33 35
20 54 4F 52 20 31 20 20 20 20 20 20 20 20 20 20
20 20 20 20 20 20 20 20 20 20 20 20 0D 0A""",
        "Display time TOR 2": """1B 07 3E 00 8D 57 00 00 10 00 00 00 00 00 00 00
00 00 10 00 0A 00 30 30 27 31 30 22 2E 31 39 37
20 54 4F 52 20 32 20 20 20 20 20 20 20 20 20 20
20 20 20 20 20 20 20 20 20 20 20 20 0D 0A""",
    }

    try:
        ser = serial.Serial(
            port=port,
            baudrate=9600,
            timeout=1,
            **params
        )

        print(f"Port: {ser.port}")
        print(f"Ustawienia: {ser.baudrate} baud, {ser.bytesize}{ser.parity}{ser.stopbits}")
        print()

        for name, hex_data in sequences.items():
            print(f"\n{'─' * 70}")
            print(f"Wysyłam: {name}")
            print(f"{'─' * 70}")

            cmd = hex_to_bytes(hex_data)

            if "Init" in name:
                # Wysyłamy 3 razy
                for i in range(3):
                    ser.write(cmd)
                    print(f"  {i+1}/3 → Wysłano {len(cmd)} bajtów: {cmd.hex().upper()}")
                    time.sleep(0.1)
            else:
                ser.write(cmd)
                print(f"  → Wysłano {len(cmd)} bajtów")
                print(f"  → HEX: {cmd.hex().upper()}")

            time.sleep(0.5)

            # Czytaj odpowiedź
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting)
                print(f"  ← ODPOWIEDŹ: {response.hex().upper()}")
            else:
                print(f"  ← Brak odpowiedzi")

            print()
            print(">>> PATRZ NA TABLICĘ! <<<")
            input("Naciśnij Enter aby wysłać kolejną komendę...")

        ser.close()

    except Exception as e:
        print(f"BŁĄD: {e}")
        import traceback
        traceback.print_exc()


def main():
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "TEST DOKŁADNYCH BAJTÓW Z PROGRAMU" + " " * 20 + "║")
    print("╚" + "═" * 68 + "╝")
    print()

    port = input("Port COM (Enter = COM5): ").strip() or "COM5"

    print()
    print("Co chcesz zrobić?")
    print("  1. Przetestuj różne ustawienia portu (POLECANE!)")
    print("  2. Wyślij sekwencję ze standardowymi ustawieniami")
    print()

    choice = input("Wybór (Enter = 1): ").strip() or "1"

    if choice == "1":
        working_config = test_port_settings(port)
        if working_config:
            print("\nCzy chcesz teraz wysłać pełną sekwencję z tymi ustawieniami?")
            if input("(t/n): ").strip().lower() == 't':
                send_exact_sequence(port, working_config['params'])
    else:
        send_exact_sequence(port)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPrzerwano przez użytkownika")
    except Exception as e:
        print(f"\nBŁĄD: {e}")
        import traceback
        traceback.print_exc()
