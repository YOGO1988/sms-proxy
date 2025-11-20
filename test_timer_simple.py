#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROSTY test START/STOP dla 2 torów
Bazuje na DZIAŁAJĄCYM test_line2_addresses.py
BEZ wątków, BEZ komplikacji - tylko to co działa!
"""

import serial
import time
import msvcrt  # dla Windows - wykrywanie klawisza bez Enter

# Pakiet inicjalizacyjny
INIT = bytes.fromhex('1B 09 0A 00 A4 EB 00 00 0D 0A')

# Bazowy pakiet TIME dla TOR 1 (bajty [18-19] = 00 00)
BASE_TOR1 = bytes.fromhex('1B 07 3A 00 EB 4F 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 32 22 2E 30 37 34 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A')

# Bazowy pakiet TIME dla TOR 2 (bajty [18-19] = 10 00)
BASE_TOR2 = bytes.fromhex('1B 07 3A 00 65 44 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 30 30 27 30 32 22 2E 30 37 34 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A')

# Bazowy pakiet META dla TOR 1 (0x3E = 62 bajty)
META_TOR1 = bytes.fromhex('1B 07 3E 00 B3 DA 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 36 22 2E 30 35 36 20 54 4F 52 20 31 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A')

# Bazowy pakiet META dla TOR 2 (0x3E = 62 bajty)
META_TOR2 = bytes.fromhex('1B 07 3E 00 23 84 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 30 30 27 30 38 22 2E 34 35 30 20 54 4F 52 20 32 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A')


def calculate_crc16(data: bytes) -> int:
    """CRC-16 dla pakietu LED"""
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


def create_packet(text: str, lane: int, is_meta=False):
    """Tworzy pakiet (TIME lub META) z tekstem - DOKŁADNIE jak w test_line2_addresses.py"""
    if is_meta:
        base = META_TOR1 if lane == 1 else META_TOR2
        text_len = 40
    else:
        base = BASE_TOR1 if lane == 1 else BASE_TOR2
        text_len = 36

    packet = bytearray(base)
    text_padded = text.ljust(text_len)
    packet[22:22+text_len] = text_padded.encode('ascii', errors='replace')

    # Przelicz CRC
    packet[4] = 0
    packet[5] = 0
    crc = calculate_crc16(bytes(packet))
    packet[4] = crc & 0xFF
    packet[5] = (crc >> 8) & 0xFF

    return bytes(packet)


def send_packet_2x(ser, packet, desc=""):
    """Wysyła pakiet 2x - JAK W DZIAŁAJĄCYM test_line2_addresses.py"""
    if desc:
        print(f"📤 {desc}")
    ser.write(packet)
    ser.flush()
    time.sleep(0.3)
    ser.write(packet)
    ser.flush()


def format_time(ms):
    """Formatuje czas MM'SS".mmm"""
    total_sec = ms // 1000
    ms_part = ms % 1000
    minutes = total_sec // 60
    seconds = total_sec % 60
    return f"{minutes:02d}'{seconds:02d}\".{ms_part:03d}"


port = input("Port (Enter = COM5): ").strip() or "COM5"

try:
    print(f"\nŁączę z {port}...")
    ser = serial.Serial(port=port, baudrate=9600, timeout=1)
    print("✅ Połączono!")

    print("\n" + "="*70)
    print("INIT (3x)")
    print("="*70)
    for i in range(3):
        ser.write(INIT)
        ser.flush()
        time.sleep(0.2)
    time.sleep(1.0)  # Jak w działającym skrypcie
    print("✅ Tablica zainicjowana")

    print("\n" + "="*70)
    print("Wyświetlam 00'00\".000 na obu torach")
    print("="*70)

    # TOR 1 - 2x jak w test_line2_addresses.py
    packet = create_packet("00'00\".000  - ", 1)
    send_packet_2x(ser, packet, "TOR 1: 00'00\".000")
    time.sleep(0.5)

    # TOR 2 - 2x jak w test_line2_addresses.py
    packet = create_packet("00'00\".000  - ", 2)
    send_packet_2x(ser, packet, "TOR 2: 00'00\".000")
    time.sleep(0.5)

    print("✅ Obie linie powinny pokazywać: 00'00\".000  -")

    # ========================================================================
    # TOR 1 - START
    # ========================================================================
    input("\n🏁 Naciśnij Enter aby START TOR 1... ")

    print("\n" + "="*70)
    print("TOR 1 - CZAS PŁYNIE (naciśnij 's' aby STOP)")
    print("="*70)

    start_time = time.time()
    update_count = 0

    while True:
        # Oblicz czas
        elapsed_ms = int((time.time() - start_time) * 1000)
        time_str = format_time(elapsed_ms)

        # Wyślij pakiet 2x (JAK W DZIAŁAJĄCYM SKRYPCIE!)
        packet = create_packet(f"{time_str}  - ", 1)
        ser.write(packet)
        ser.flush()
        time.sleep(0.05)
        ser.write(packet)
        ser.flush()

        update_count += 1
        if update_count % 10 == 0:
            print(f"   ⏱️  TOR 1: {time_str}")

        # Sprawdź czy użytkownik nacisnął 's'
        if msvcrt.kbhit():
            key = msvcrt.getch().decode('utf-8').lower()
            if key == 's':
                break

        time.sleep(0.05)  # Aktualizacja co 50ms

    # Zatrzymaj TOR 1 i pokaż META
    final_time_1 = format_time(int((time.time() - start_time) * 1000))
    print(f"\n⏹️  TOR 1 STOP: {final_time_1}")

    meta_packet = create_packet(f"{final_time_1} TOR 1", 1, is_meta=True)
    send_packet_2x(ser, meta_packet, f"META TOR 1: {final_time_1}")

    # ========================================================================
    # TOR 2 - START
    # ========================================================================
    input("\n🏁 Naciśnij Enter aby START TOR 2... ")

    print("\n" + "="*70)
    print("TOR 2 - CZAS PŁYNIE (naciśnij 's' aby STOP)")
    print("="*70)

    start_time = time.time()
    update_count = 0

    while True:
        # Oblicz czas
        elapsed_ms = int((time.time() - start_time) * 1000)
        time_str = format_time(elapsed_ms)

        # Wyślij pakiet 2x
        packet = create_packet(f"{time_str}  - ", 2)
        ser.write(packet)
        ser.flush()
        time.sleep(0.05)
        ser.write(packet)
        ser.flush()

        update_count += 1
        if update_count % 10 == 0:
            print(f"   ⏱️  TOR 2: {time_str}")

        # Sprawdź czy użytkownik nacisnął 's'
        if msvcrt.kbhit():
            key = msvcrt.getch().decode('utf-8').lower()
            if key == 's':
                break

        time.sleep(0.05)

    # Zatrzymaj TOR 2 i pokaż META
    final_time_2 = format_time(int((time.time() - start_time) * 1000))
    print(f"\n⏹️  TOR 2 STOP: {final_time_2}")

    meta_packet = create_packet(f"{final_time_2} TOR 2", 2, is_meta=True)
    send_packet_2x(ser, meta_packet, f"META TOR 2: {final_time_2}")

    print("\n" + "="*70)
    print("✅ TEST ZAKOŃCZONY!")
    print("="*70)
    print(f"TOR 1: {final_time_1}")
    print(f"TOR 2: {final_time_2}")
    print("="*70)

    ser.close()

except Exception as e:
    print(f"\n❌ BŁĄD: {e}")
    import traceback
    traceback.print_exc()

input("\nNaciśnij Enter aby zakończyć...")
