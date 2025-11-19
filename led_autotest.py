#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LED Auto-Test Script - Automatyczne testy różnych protokołów
Wersja rozszerzona z trybem interaktywnym
"""

import serial
import serial.tools.list_ports
import time
from datetime import datetime
import sys

def find_ports():
    """Znajduje dostępne porty COM"""
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def test_baudrate(port, baudrate, test_string="TEST"):
    """Testuje konkretny baudrate"""
    print(f"\n{'='*60}")
    print(f"TEST: {port} @ {baudrate} baud")
    print(f"{'='*60}")

    try:
        # Otwórz port
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=2
        )

        print(f"✅ Port otwarty")
        time.sleep(0.5)

        # Test 1: Prosty tekst ASCII
        print(f"\n📤 Wysyłam ASCII: '{test_string}'")
        ser.write(test_string.encode('utf-8'))
        time.sleep(0.5)

        # Sprawdź odpowiedź
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting)
            print(f"📥 ODPOWIEDŹ! HEX: {response.hex(' ')}")
            print(f"   ASCII: {response}")
        else:
            print("⚫ Brak odpowiedzi")

        # Test 2: Tekst z enterem
        print(f"\n📤 Wysyłam z \\n: '{test_string}\\n'")
        ser.write((test_string + "\n").encode('utf-8'))
        time.sleep(0.5)

        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting)
            print(f"📥 ODPOWIEDŹ! HEX: {response.hex(' ')}")
        else:
            print("⚫ Brak odpowiedzi")

        # Test 3: Tekst z \r\n
        print(f"\n📤 Wysyłam z \\r\\n: '{test_string}\\r\\n'")
        ser.write((test_string + "\r\n").encode('utf-8'))
        time.sleep(0.5)

        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting)
            print(f"📥 ODPOWIEDŹ! HEX: {response.hex(' ')}")
        else:
            print("⚫ Brak odpowiedzi")

        ser.close()
        print("\n✅ Test zakończony")
        return True

    except Exception as e:
        print(f"❌ BŁĄD: {str(e)}")
        return False

def test_hex_commands(port, baudrate):
    """Testuje komendy HEX"""
    print(f"\n{'='*60}")
    print(f"TEST HEX: {port} @ {baudrate} baud")
    print(f"{'='*60}")

    hex_commands = [
        ("INIT/RESET", "FF FF FF"),
        ("CLEAR", "00 00 00"),
        ("TEST 1", "01 02 03 04"),
        ("TEST 2", "AA BB CC DD"),
        ("STX/ETX", "02 54 45 53 54 03"),  # STX "TEST" ETX
    ]

    try:
        ser = serial.Serial(port, baudrate, timeout=2)
        print(f"✅ Port otwarty")

        for name, hex_str in hex_commands:
            print(f"\n📤 {name}: {hex_str}")
            data = bytes.fromhex(hex_str.replace(" ", ""))
            ser.write(data)
            time.sleep(0.5)

            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting)
                print(f"📥 ODPOWIEDŹ! HEX: {response.hex(' ')}")
            else:
                print("⚫ Brak odpowiedzi")

        ser.close()
        return True

    except Exception as e:
        print(f"❌ BŁĄD: {str(e)}")
        return False

def auto_detect_and_monitor(port, log_file):
    """Automatyczne wykrywanie baudrate i monitoring"""
    baudrates = [9600, 19200, 38400, 57600, 115200]

    print("\n🔍 ROZPOCZYNAM AUTO-DETECT...")
    print("Wysyłam test na każdym baudrate i nasłuchuję przez 5 sekund...")

    for baudrate in baudrates:
        print(f"\n{'='*60}")
        print(f"🔍 Testuję {baudrate} baud...")
        print(f"{'='*60}")

        try:
            ser = serial.Serial(port, baudrate, timeout=0.1)
            time.sleep(0.3)

            # Wyślij różne komendy testowe
            test_commands = [
                ("12.34", "Time format"),
                ("TEST\r\n", "ASCII with CRLF"),
                (bytes([0x02, 0x54, 0x45, 0x53, 0x54, 0x03]), "STX/ETX"),
            ]

            responses_found = False

            for cmd, desc in test_commands:
                if isinstance(cmd, str):
                    ser.write(cmd.encode('utf-8'))
                else:
                    ser.write(cmd)

                time.sleep(0.5)

                if ser.in_waiting > 0:
                    response = ser.read(ser.in_waiting)
                    print(f"✅ {desc}: ODPOWIEDŹ! HEX: {response.hex(' ')}")
                    responses_found = True

            # Nasłuchuj przez 5 sekund
            print(f"\n👂 Nasłuchuję przez 5 sekund...")
            start_time = time.time()
            data_received = False

            while time.time() - start_time < 5:
                if ser.in_waiting > 0:
                    data = ser.read(ser.in_waiting)
                    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    print(f"[{timestamp}] 📥 HEX: {data.hex(' ')} | ASCII: {data}")
                    data_received = True
                time.sleep(0.1)

            ser.close()

            if responses_found or data_received:
                print(f"\n🎯 {baudrate} baud wygląda obiecująco!")
                choice = input(f"\nChcesz przejść do pełnego monitoringu na {baudrate}? (t/n): ")
                if choice.lower() == 't':
                    monitor_and_send(port, baudrate, log_file)
                    return
            else:
                print(f"⚫ Brak aktywności na {baudrate}")

        except Exception as e:
            print(f"❌ Błąd: {e}")

    print("\n⚠️  Nie wykryto aktywnego baudrate")

def run_quick_tests(ser, log):
    """Szybkie testy różnych formatów"""
    print("\n🧪 URUCHAMIAM SZYBKIE TESTY...\n")

    tests = [
        # Format czasowy
        ("12.34", "Czas MM.SS"),
        ("1.23.45", "Czas H.MM.SS"),
        ("12:34", "Czas MM:SS"),
        ("01:23:45", "Czas HH:MM:SS"),

        # Liczby
        ("1234", "Liczba całkowita"),
        ("12.34", "Liczba dziesiętna"),

        # Z końcówkami linii
        ("TEST\n", "ASCII + LF"),
        ("TEST\r\n", "ASCII + CRLF"),
        ("TEST\r", "ASCII + CR"),

        # HEX komendy
        (bytes([0x02, 0x31, 0x32, 0x2E, 0x33, 0x34, 0x03]), "STX+12.34+ETX"),
        (bytes([0xFF, 0xFF, 0xFF]), "Reset/Init"),
        (bytes([0x01, 0x12, 0x34]), "Protokół 1"),
    ]

    for data, description in tests:
        print(f"📤 Test: {description}")

        if isinstance(data, str):
            ser.write(data.encode('utf-8'))
            print(f"   Wysłano: {data.encode('utf-8').hex(' ')}")
            log.write(f"TEST TX: {description} | {data.encode('utf-8').hex(' ')}\n")
        else:
            ser.write(data)
            print(f"   Wysłano HEX: {data.hex(' ')}")
            log.write(f"TEST TX: {description} | {data.hex(' ')}\n")

        time.sleep(0.8)

        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting)
            print(f"   📥 ODPOWIEDŹ: {response.hex(' ')}")
            log.write(f"TEST RX: {response.hex(' ')}\n")
        else:
            print(f"   ⚫ Brak odpowiedzi")

        print()

    print("✅ Testy zakończone\n")

def monitor_and_send(port, baudrate, log_file):
    """Główny tryb monitoringu i wysyłania komend"""
    print(f"\n{'='*60}")
    print(f"MONITOR PORTU: {port} @ {baudrate} baud")
    print(f"{'='*60}")
    print("\nKOMENDY:")
    print("  Wpisz tekst i Enter - wyśle jako ASCII")
    print("  HEX:AABBCC - wyśle jako bajty HEX")
    print("  'listen' - tylko nasłuchuj (30 sek)")
    print("  'test' - wyślij serie testów")
    print("  'clear' - wyczyść ekran")
    print("  'quit' - wyjście")
    print("=" * 60)

    try:
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.1
        )

        print(f"✅ Port otwarty na {baudrate} baud")
        print("👂 Nasłuchuję... (wpisz komendę i Enter)\n")

        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(f"\n\n{'='*60}\n")
            log.write(f"INTERACTIVE MODE: {baudrate} baud\n")
            log.write(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log.write(f"{'='*60}\n\n")

            # Bufor dla pełnego monitoringu
            import threading

            def monitor_serial():
                """Funkcja w osobnym wątku do ciągłego monitoringu"""
                while ser.is_open:
                    if ser.in_waiting > 0:
                        data = ser.read(ser.in_waiting)
                        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                        hex_data = data.hex(' ')

                        try:
                            ascii_data = data.decode('utf-8', errors='replace')
                        except:
                            ascii_data = str(data)

                        print(f"\n📥 [{timestamp}] Otrzymano:")
                        print(f"   HEX: {hex_data}")
                        print(f"   ASCII: {ascii_data}")
                        print(f"   Długość: {len(data)} bajtów")
                        print("\n> ", end='', flush=True)

                        log.write(f"[{timestamp}] RX: {hex_data} | {ascii_data}\n")
                        log.flush()

                    time.sleep(0.05)

            # Uruchom monitoring w tle
            monitor_thread = threading.Thread(target=monitor_serial, daemon=True)
            monitor_thread.start()

            # Główna pętla komend
            while True:
                try:
                    user_input = input("> ").strip()

                    if not user_input:
                        continue

                    # Przetwórz komendę
                    if user_input.lower() == 'quit':
                        break

                    elif user_input.lower() == 'clear':
                        # Wyczyść ekran (Windows/Linux)
                        import os
                        os.system('cls' if os.name == 'nt' else 'clear')
                        print(f"MONITOR: {port} @ {baudrate} baud\n")

                    elif user_input.lower() == 'listen':
                        print("\n👂 NASŁUCHUJĘ przez 30 sekund...")
                        print("   (wpisz cokolwiek aby przerwać)")

                        listen_start = time.time()
                        while time.time() - listen_start < 30:
                            time.sleep(0.1)
                            # Monitor działa w tle, więc tu tylko czekamy

                        print("✅ Nasłuchiwanie zakończone\n")

                    elif user_input.lower() == 'test':
                        run_quick_tests(ser, log)

                    elif user_input.upper().startswith('HEX:'):
                        # Wyślij HEX
                        hex_str = user_input[4:].replace(' ', '').replace(':', '')
                        try:
                            data = bytes.fromhex(hex_str)
                            ser.write(data)
                            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                            print(f"📤 [{timestamp}] Wysłano HEX: {data.hex(' ')}")
                            log.write(f"[{timestamp}] TX HEX: {data.hex(' ')}\n")
                            log.flush()
                        except ValueError:
                            print("❌ Nieprawidłowy format HEX!")

                    else:
                        # Wyślij jako ASCII
                        # Sprawdź czy użytkownik chce dodać końcówki linii
                        data_to_send = user_input

                        # Automatycznie wykryj escape sequences
                        data_to_send = data_to_send.replace('\\n', '\n')
                        data_to_send = data_to_send.replace('\\r', '\r')
                        data_to_send = data_to_send.replace('\\t', '\t')

                        ser.write(data_to_send.encode('utf-8'))
                        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                        print(f"📤 [{timestamp}] Wysłano ASCII: {repr(data_to_send)}")
                        log.write(f"[{timestamp}] TX ASCII: {repr(data_to_send)}\n")
                        log.flush()

                except KeyboardInterrupt:
                    print("\n\n⚠️  Użyj 'quit' aby wyjść")
                    continue

        ser.close()
        print("\n✅ Port zamknięty")

    except Exception as e:
        print(f"\n❌ BŁĄD: {e}")
        if 'ser' in locals() and ser.is_open:
            ser.close()

def interactive_mode(port, log_file):
    """Tryb interaktywny - nasłuchiwanie i wysyłanie komend"""
    print("\n" + "=" * 60)
    print("TRYB INTERAKTYWNY")
    print("=" * 60)

    # Wybór baudrate
    print("\n📍 Który baudrate działał najlepiej?")
    print("   1. 9600")
    print("   2. 19200")
    print("   3. 38400")
    print("   4. 57600")
    print("   5. 115200")
    print("   6. Sprawdź wszystkie po kolei (auto-detect)")

    choice = input("Wybór (1-6): ").strip()

    baudrates = {
        '1': 9600,
        '2': 19200,
        '3': 38400,
        '4': 57600,
        '5': 115200
    }

    if choice == '6':
        # Auto-detect mode
        auto_detect_and_monitor(port, log_file)
    elif choice in baudrates:
        monitor_and_send(port, baudrates[choice], log_file)
    else:
        print("❌ Nieprawidłowy wybór")

def main():
    print("=" * 60)
    print("LED DISPLAY AUTO-TEST")
    print("YO&GO Events - 2025")
    print("Wersja z trybem interaktywnym")
    print("=" * 60)

    # Znajdź porty
    ports = find_ports()

    if not ports:
        print("\n❌ Nie znaleziono portów COM!")
        print("   Sprawdź czy konwerter USB-RS232 jest podłączony")
        input("\nNaciśnij Enter aby zakończyć...")
        return

    print(f"\n✅ Znaleziono porty: {', '.join(ports)}")

    # Wybierz port
    if len(ports) == 1:
        port = ports[0]
        print(f"\n📍 Używam: {port}")
    else:
        print("\n📍 Wybierz port:")
        for i, p in enumerate(ports, 1):
            print(f"   {i}. {p}")
        choice = input("Numer: ").strip()
        try:
            port = ports[int(choice) - 1]
        except:
            print("❌ Nieprawidłowy wybór!")
            return

    # Zapytaj czy chcemy tryb automatyczny czy od razu interaktywny
    print("\n" + "=" * 60)
    print("WYBÓR TRYBU:")
    print("  1. Automatyczne testy wszystkich baudrate (zalecane)")
    print("  2. Tryb interaktywny (jeśli znasz baudrate)")
    print("=" * 60)

    mode_choice = input("\nWybór (1-2): ").strip()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"LED_AutoTest_{timestamp}.txt"
    print(f"\n💾 Zapisuję logi do: {log_file}")

    if mode_choice == '2':
        # Bezpośrednio do trybu interaktywnego
        interactive_mode(port, log_file)
    else:
        # Standardowe testy automatyczne
        baudrates = [9600, 19200, 38400, 57600, 115200]

        print("\n" + "=" * 60)
        print("ROZPOCZYNAM TESTY BAUDRATE")
        print("=" * 60)

        input("\n⚠️  UWAGA: Upewnij się że tablica jest WŁĄCZONA!\nNaciśnij Enter aby kontynuować...")

        with open(log_file, 'w', encoding='utf-8') as log:
            log.write(f"LED Display Auto-Test\n")
            log.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log.write(f"Port: {port}\n")
            log.write("=" * 60 + "\n\n")

            for baudrate in baudrates:
                print(f"\n\n{'#' * 60}")
                print(f"TEST BAUDRATE: {baudrate}")
                print(f"{'#' * 60}")

                log.write(f"\n{'=' * 60}\n")
                log.write(f"BAUDRATE: {baudrate}\n")
                log.write(f"{'=' * 60}\n")

                # Test ASCII
                success = test_baudrate(port, baudrate, "12.34")
                log.write(f"ASCII Test: {'SUCCESS' if success else 'FAILED'}\n")

                time.sleep(1)

                # Test HEX
                success_hex = test_hex_commands(port, baudrate)
                log.write(f"HEX Test: {'SUCCESS' if success_hex else 'FAILED'}\n")

                time.sleep(2)

        print("\n\n" + "=" * 60)
        print("✅ TESTY ZAKOŃCZONE!")
        print(f"💾 Log zapisany: {log_file}")
        print("=" * 60)
        print("\n📋 NASTĘPNE KROKI:")
        print("1. Sprawdź czy tablica coś wyświetliła")
        print("2. Otwórz plik logu i zobacz które testy dały odpowiedź")
        print("3. Wyślij log do mnie - zintegruję z programem!")

        # Tryb interaktywny
        print("\n" + "=" * 60)
        choice = input("\nChcesz przejść do trybu interaktywnego? (t/n): ").lower()

        if choice == 't':
            interactive_mode(port, log_file)

    print("\n✅ Program zakończony")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️  Program przerwany przez użytkownika")
    except Exception as e:
        print(f"\n❌ Krytyczny błąd: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("\nNaciśnij Enter aby zakończyć...")
