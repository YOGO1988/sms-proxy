#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test różnych adresów dla linii 2
Sprawdzamy czy problem jest w adresowaniu
"""

import serial
import time

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

def create_time_packet_with_address(addr_byte1, addr_byte2):
    """Tworzy pakiet TIME z niestandardowym adresem"""
    # Bazowy pakiet (linia 2)
    packet = bytearray.fromhex('1B 07 3A 00 00 00 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 30 30 27 30 32 22 2E 30 37 34 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A')

    # Zmień adres
    packet[18] = addr_byte1
    packet[19] = addr_byte2

    # Przelicz CRC
    packet[4] = 0
    packet[5] = 0
    crc = calculate_crc16(bytes(packet))
    packet[4] = crc & 0xFF
    packet[5] = (crc >> 8) & 0xFF

    return bytes(packet)

# Pakiet inicjalizacyjny
INIT = bytes.fromhex('1B 09 0A 00 A4 EB 00 00 0D 0A')

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
    time.sleep(1.0)

    # Testujemy różne adresy dla linii 2
    test_addresses = [
        (0x10, 0x00, "Standardowy (10 00)"),
        (0x00, 0x10, "Odwrócony (00 10)"),
        (0x01, 0x00, "Jak linia 1 (01 00) - może to fizycznie linia 1?"),
        (0x02, 0x00, "Próba: 02 00"),
        (0x20, 0x00, "Próba: 20 00"),
        (0x00, 0x01, "Próba: 00 01"),
        (0x00, 0x02, "Próba: 00 02"),
    ]

    print("\n" + "="*70)
    print("TEST RÓŻNYCH ADRESÓW DLA LINII 2")
    print("="*70)

    for addr1, addr2, desc in test_addresses:
        print(f"\n📤 Test: bajty [18-19] = {addr1:02X} {addr2:02X} - {desc}")
        packet = create_time_packet_with_address(addr1, addr2)

        # Wysłij 2x dla pewności
        ser.write(packet)
        ser.flush()
        time.sleep(0.3)
        ser.write(packet)
        ser.flush()

        print(f"   Czekam 3 sekundy - SPRAWDŹ czy coś się zmieniło...")
        time.sleep(3.0)

    print("\n✅ Test zakończony!")
    print("\n" + "="*70)
    print("❓ KTÓRY ADRES ZADZIAŁAŁ?")
    print("="*70)
    print("\n📋 Zanotuj który wariant wyświetlił czas na linii 2:")

    for i, (addr1, addr2, desc) in enumerate(test_addresses, 1):
        print(f"   {i}. {addr1:02X} {addr2:02X} - {desc}")

    print("\nJeśli ŻADEN - napisz co dokładnie widzisz na wyświetlaczu")

    ser.close()

except Exception as e:
    print(f"\n❌ BŁĄD: {e}")
    import traceback
    traceback.print_exc()

input("\nNaciśnij Enter aby zakończyć...")
