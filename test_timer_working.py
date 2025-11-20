#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Timer test using EXACT working packets from led_display_final.py
NO modifications - uses proven working hex packets!
"""

import serial
import time

# DOKŁADNIE z led_display_final.py - NIE MODYFIKUJ!
INIT = bytes.fromhex('1B 09 0A 00 A4 EB 00 00 0D 0A')

# Pakiet TIME dla TOR 1 - DOKŁADNIE z led_display_final.py
TIME_BASE_TOR1 = bytes.fromhex('1B 07 3A 00 51 8B 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 34 36 37 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A')

# Pakiet META dla TOR 1 - DOKŁADNIE z led_display_final.py
TIME_META_TOR1 = bytes.fromhex('1B 07 3E 00 A1 2A 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 37 38 37 20 54 4F 52 20 31 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A')

# Pakiet META dla TOR 2 - DOKŁADNIE z led_display_final.py
TIME_META_TOR2 = bytes.fromhex('1B 07 3E 00 8F 5C 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 30 30 27 31 30 22 2E 33 36 32 20 54 4F 52 20 32 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A')


def calculate_crc16(data: bytes) -> int:
    """CRC-16-CCITT"""
    crc = 0x0000
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc


def create_time_packet(text: str, base_packet: bytes) -> bytes:
    """
    Tworzy pakiet TIME z nowym tekstem (58 bajtów)
    Używa działającego pakietu jako bazowego
    """
    packet = bytearray(base_packet)

    # Tekst zaczyna się od bajtu 22, kończy na 55 (34 bajty)
    # Bajty 56-57 to ZAWSZE 0D 0A (\r\n) - NIE NADPISUJ!
    text_padded = text.ljust(34)[:34]  # Dokładnie 34 znaki (nie 36!)
    packet[22:56] = text_padded.encode('ascii', errors='replace')
    # packet[56:58] pozostaje 0D 0A

    # Przelicz CRC (bajty 4-5)
    packet[4] = 0
    packet[5] = 0
    crc = calculate_crc16(bytes(packet))
    packet[4] = crc & 0xFF
    packet[5] = (crc >> 8) & 0xFF

    return bytes(packet)


def create_meta_packet(text: str, base_packet: bytes) -> bytes:
    """
    Tworzy pakiet META z nowym tekstem (62 bajty)
    Pakiet META ma bajt 2 = 0x3E i tekst 38 znaków
    """
    packet = bytearray(base_packet)

    # Tekst zaczyna się od bajtu 22, kończy na 59 (38 bajtów)
    # Bajty 60-61 to ZAWSZE 0D 0A (\r\n) - NIE NADPISUJ!
    text_padded = text.ljust(38)[:38]  # Dokładnie 38 znaków
    packet[22:60] = text_padded.encode('ascii', errors='replace')
    # packet[60:62] pozostaje 0D 0A

    # Przelicz CRC (bajty 4-5)
    packet[4] = 0
    packet[5] = 0
    crc = calculate_crc16(bytes(packet))
    packet[4] = crc & 0xFF
    packet[5] = (crc >> 8) & 0xFF

    return bytes(packet)


def format_time(ms):
    """Format MM'SS".mmm"""
    total_sec = ms // 1000
    ms_part = ms % 1000
    minutes = total_sec // 60
    seconds = total_sec % 60
    return f"{minutes:02d}'{seconds:02d}\".{ms_part:03d}"


def send_packet(ser, packet, desc=""):
    """Wyślij pakiet (jak w led_display_final.py)"""
    if desc:
        print(f"📤 {desc}")
    ser.write(packet)
    ser.flush()
    time.sleep(0.3)


port = input("Port (Enter = COM5): ").strip() or "COM5"

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
    time.sleep(0.3)  # Jak w led_display_final.py

    print("\n" + "="*70)
    print("TEST 1: Wyślij działający pakiet (00'07\".467)")
    print("="*70)
    print("To jest ORYGINALNY pakiet z led_display_final.py")
    input("Naciśnij Enter aby wysłać...")

    send_packet(ser, TIME_BASE_TOR1, "TIME TOR 1: 00'07\".467 (oryginalny)")
    time.sleep(2)

    print("\n❓ CZY WYŚWIETLIŁO SIĘ 00'07\".467 NA TABLICY?")
    response = input("(t/n): ").strip().lower()

    if response != 't':
        print("\n❌ ORYGINALNY pakiet nie działa!")
        print("Problem NIE jest w moim kodzie - coś jest nie tak z połączeniem.")
        print("Sprawdź:")
        print("  - Czy tablica jest włączona")
        print("  - Czy port COM5 jest dobry")
        print("  - Czy nic innego nie używa portu")
        ser.close()
        input("\nNaciśnij Enter...")
        exit(1)

    print("\n✅ Oryginalny pakiet działa!")

    print("\n" + "="*70)
    print("TEST 2: Zmień czas na 00'00\".000")
    print("="*70)
    input("Naciśnij Enter aby wysłać...")

    packet = create_time_packet("00'00\".000  - ", TIME_BASE_TOR1)
    send_packet(ser, packet, "TIME TOR 1: 00'00\".000 (zmodyfikowany)")
    time.sleep(2)

    print("\n❓ CZY WYŚWIETLIŁO SIĘ 00'00\".000?")
    response = input("(t/n): ").strip().lower()

    if response != 't':
        print("\n❌ Zmodyfikowany pakiet nie działa!")
        print("Problem jest w mojej funkcji create_time_packet()")
        print("Prawdopodobnie:")
        print("  - Źle liczę CRC")
        print("  - Źle modyfikuję tekst")
        print("  - Psuję jakieś inne bajty")
        ser.close()
        input("\nNaciśnij Enter...")
        exit(1)

    print("\n✅ Zmodyfikowany pakiet działa!")

    print("\n" + "="*70)
    print("TEST 3: Timer - liczenie czasu")
    print("="*70)
    print("Będzie liczyć czas i wyświetlać co 100ms")
    print("Naciśnij Ctrl+C aby zatrzymać")
    input("Naciśnij Enter aby rozpocząć...")

    start_time = time.time()
    update_count = 0

    try:
        while True:
            elapsed_ms = int((time.time() - start_time) * 1000)
            time_str = format_time(elapsed_ms)

            packet = create_time_packet(f"{time_str}  - ", TIME_BASE_TOR1)
            ser.write(packet)
            ser.flush()

            update_count += 1
            if update_count % 10 == 0:
                print(f"   ⏱️  {time_str}")

            time.sleep(0.1)  # Update co 100ms

    except KeyboardInterrupt:
        print("\n\n⏹️  STOP!")
        final_ms = int((time.time() - start_time) * 1000)
        final_time = format_time(final_ms)
        print(f"Czas końcowy: {final_time}")

        # Wyślij META
        packet = create_meta_packet(f"{final_time} TOR 1", TIME_META_TOR1)
        send_packet(ser, packet, f"META TOR 1: {final_time}")

    print("\n" + "="*70)
    print("✅ TEST ZAKOŃCZONY!")
    print("="*70)

    ser.close()

except Exception as e:
    print(f"\n❌ BŁĄD: {e}")
    import traceback
    traceback.print_exc()

input("\nNaciśnij Enter aby zakończyć...")
