#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LED Display DIAGNOSTICS - Prosty test połączenia
Znajduje DOKŁADNIE co działa z tablicą
"""

import serial
import time

def test_connection(port, baudrate):
    """Test podstawowego połączenia"""
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
            timeout=2,
            write_timeout=2
        )

        print(f"✅ Port otwarty pomyślnie")
        time.sleep(0.5)

        # Lista testów - DOKŁADNIE jak w Twoim oryginalnym skrypcie
        tests = [
            ("1. Prosty tekst", "TEST", "ascii"),
            ("2. Tekst + \\n", "TEST\n", "ascii"),
            ("3. Tekst + \\r\\n", "TEST\r\n", "ascii"),
            ("4. Tekst + \\r", "TEST\r", "ascii"),
            ("5. Czas MM.SS", "12.34", "ascii"),
            ("6. Czas MM.SS + \\n", "12.34\n", "ascii"),
            ("7. Czas MM.SS + \\r\\n", "12.34\r\n", "ascii"),
            ("8. HEX: FF FF FF", "FFFFFF", "hex"),
            ("9. HEX: 00 00 00", "000000", "hex"),
            ("10. STX+TEST+ETX", "0254455354103", "hex"),
        ]

        for name, data, format_type in tests:
            print(f"\n{name}")

            if format_type == "ascii":
                bytes_to_send = data.encode('utf-8')
                print(f"   Wysyłam ASCII: {repr(data)}")
                print(f"   Bajty HEX: {bytes_to_send.hex(' ').upper()}")
            else:  # hex
                bytes_to_send = bytes.fromhex(data)
                print(f"   Wysyłam HEX: {bytes_to_send.hex(' ').upper()}")

            # Wyczyść bufor
            ser.reset_input_buffer()

            # Wyślij
            ser.write(bytes_to_send)
            ser.flush()

            # Czekaj na odpowiedź
            time.sleep(1.0)

            # Sprawdź czy coś przyszło
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting)
                print(f"   📥 ODPOWIEDŹ!")
                print(f"      HEX: {response.hex(' ').upper()}")
                print(f"      ASCII: {response}")
                print(f"      Długość: {len(response)} bajtów")
            else:
                print(f"   ⚫ Brak odpowiedzi")

            print(f"   ⏱️  Czekam 2 sekundy...")
            time.sleep(2)

        # Dodatkowy test - nasłuchuj przez 5 sekund
        print(f"\n{'='*60}")
        print("NASŁUCHIWANIE - Czy tablica coś wysyła sama?")
        print("Czekam 5 sekund...")
        print(f"{'='*60}")

        ser.reset_input_buffer()
        start = time.time()
        received_anything = False

        while time.time() - start < 5:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                print(f"\n📥 Otrzymano spontanicznie:")
                print(f"   HEX: {data.hex(' ').upper()}")
                print(f"   ASCII: {data}")
                received_anything = True
            time.sleep(0.1)

        if not received_anything:
            print("⚫ Tablica nic nie wysłała")

        ser.close()
        print(f"\n✅ Port zamknięty")
        return True

    except Exception as e:
        print(f"\n❌ BŁĄD: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*60)
    print("LED DISPLAY - DIAGNOSTYKA")
    print("="*60)

    # Domyślnie COM5 jak użytkownik powiedział
    port = input("\nPort COM (Enter = COM5): ").strip() or "COM5"

    print("\nKtóry baudrate chcesz przetestować?")
    print("1. Przetestuj WSZYSTKIE (9600, 19200, 38400, 57600, 115200)")
    print("2. Tylko jeden konkretny")

    choice = input("Wybór (1 lub 2): ").strip()

    if choice == "1":
        baudrates = [9600, 19200, 38400, 57600, 115200]

        print("\n" + "="*60)
        print("⚠️  UWAGA: Upewnij się że tablica jest WŁĄCZONA!")
        input("Naciśnij Enter aby kontynuować...")

        for br in baudrates:
            test_connection(port, br)

            # Zapytaj czy chce kontynuować
            if br != baudrates[-1]:  # Jeśli to nie ostatni
                cont = input("\nKontynuować następny baudrate? (t/n): ").lower()
                if cont != 't':
                    break
    else:
        br = int(input("Podaj baudrate (np. 9600): ").strip())

        print("\n" + "="*60)
        print("⚠️  UWAGA: Upewnij się że tablica jest WŁĄCZONA!")
        input("Naciśnij Enter aby kontynuować...")

        test_connection(port, br)

    print("\n" + "="*60)
    print("DIAGNOSTYKA ZAKOŃCZONA")
    print("="*60)
    print("\n📋 ANALIZA WYNIKÓW:")
    print("1. Sprawdź powyżej czy JAKAKOLWIEK komenda dała odpowiedź")
    print("2. Jeśli TAK - zanotuj:")
    print("   - Który baudrate?")
    print("   - Która komenda?")
    print("   - Co tablica odpowiedziała?")
    print("3. Jeśli NIE - możliwe przyczyny:")
    print("   - Zły port (sprawdź Menedżer Urządzeń)")
    print("   - Tablica wyłączona")
    print("   - Zły kabel")
    print("   - Tablica nie obsługuje żadnego z testowanych formatów")
    print("\n4. Czy tablica coś WYŚWIETLIŁA na ekranie?")
    print("   To najważniejsze! Nawet jeśli nie odpowiada przez port,")
    print("   powinna coś pokazać na swoim wyświetlaczu!")
    print("\n5. Prześlij mi te informacje i naprawię kod!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️ Przerwano")
    except Exception as e:
        print(f"\n❌ Błąd: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("\nNaciśnij Enter aby zakończyć...")
