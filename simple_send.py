#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAJPROSTSZY TEST - Po prostu wyślij do tablicy i PATRZ NA EKRAN!
Nie sprawdzamy odpowiedzi - tylko czy tablica WYŚWIETLA!
"""

import serial
import time

def send_to_display(port, baudrate, message):
    """Wyślij wiadomość i nie sprawdzaj odpowiedzi - patrz na tablicę!"""

    print(f"Otwieram port {port} @ {baudrate} baud...")

    try:
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=1
        )

        print(f"✅ Port otwarty")
        print(f"\n{'='*60}")
        print(f"WYSYŁAM DO TABLICY: '{message}'")
        print(f"{'='*60}")
        print("\n👀 PATRZ NA EKRAN TABLICY! Czy coś się tam pojawia?\n")

        # Wyślij różne warianty - jeden na pewno zadziała!

        # Wariant 1: Czysty tekst
        print("Wariant 1: Czysty tekst")
        ser.write(message.encode('utf-8'))
        time.sleep(2)
        print("   Czy tablica coś pokazała? (patrz na ekran!)\n")
        time.sleep(2)

        # Wariant 2: Tekst + \n
        print("Wariant 2: Tekst + \\n")
        ser.write((message + "\n").encode('utf-8'))
        time.sleep(2)
        print("   Czy tablica coś pokazała? (patrz na ekran!)\n")
        time.sleep(2)

        # Wariant 3: Tekst + \r\n
        print("Wariant 3: Tekst + \\r\\n")
        ser.write((message + "\r\n").encode('utf-8'))
        time.sleep(2)
        print("   Czy tablica coś pokazała? (patrz na ekran!)\n")
        time.sleep(2)

        # Wariant 4: Tylko cyfry (czas)
        print("Wariant 4: Cyfry - czas")
        ser.write("12.34\r\n".encode('utf-8'))
        time.sleep(2)
        print("   Czy tablica pokazała '12.34'? (patrz na ekran!)\n")
        time.sleep(2)

        # Wariant 5: Format z dwukropkiem
        print("Wariant 5: Format z dwukropkiem")
        ser.write("01:23.45\r\n".encode('utf-8'))
        time.sleep(2)
        print("   Czy tablica pokazała '01:23.45'? (patrz na ekran!)\n")
        time.sleep(2)

        ser.close()
        print("✅ Test zakończony")

        print("\n" + "="*60)
        print("ANALIZA:")
        print("="*60)
        print("CZY TABLICA WYŚWIETLIŁA COKOLWIEK?")
        print("")
        print("JEŚLI TAK:")
        print("  ✅ Tablica działa!")
        print("  ✅ Port i baudrate są dobre!")
        print("  ✅ Tylko trzeba dostosować format komendy w moim kodzie")
        print("  → Powiedz mi który wariant wyświetlił tekst!")
        print("")
        print("JEŚLI NIE:")
        print("  ❌ Problem może być z:")
        print("     - Zły port (sprawdź Menedżer Urządzeń - czy to na pewno COM5?)")
        print("     - Zły baudrate (spróbuj inny)")
        print("     - Tablica wyłączona")
        print("     - Zły kabel / złe połączenie")
        print("     - Tablica wymaga specjalnych komend inicjalizacyjnych")
        print("")
        print("="*60)

    except Exception as e:
        print(f"\n❌ BŁĄD: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("="*60)
    print("PROSTY TEST TABLICY LED")
    print("="*60)
    print("\nTen program wyśle tekst do tablicy.")
    print("NIE sprawdza odpowiedzi - po prostu PATRZ NA EKRAN tablicy!")
    print("="*60)

    port = input("\nPort (Enter = COM5): ").strip() or "COM5"

    print("\nWybierz baudrate:")
    print("1. 9600")
    print("2. 19200")
    print("3. 38400")
    print("4. 57600")
    print("5. 115200")

    baudrates = {
        '1': 9600,
        '2': 19200,
        '3': 38400,
        '4': 57600,
        '5': 115200
    }

    choice = input("Wybór (Enter = 1): ").strip() or '1'
    baudrate = baudrates.get(choice, 9600)

    message = input("\nCo wysłać do tablicy? (Enter = 'TEST'): ").strip() or "TEST"

    print("\n⚠️  UWAGA: Patrz na ekran tablicy przez cały test!")
    input("Naciśnij Enter gdy jesteś gotowy...")

    send_to_display(port, baudrate, message)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPrzerwano")
    finally:
        input("\nNaciśnij Enter aby zakończyć...")
