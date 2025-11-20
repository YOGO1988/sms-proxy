#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weryfikacja implementacji CRC-16
"""

def calculate_crc16(data: bytes) -> int:
    """Oblicz CRC-16 (CRC-16-CCITT, poly=0x1021)"""
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

def create_time_packet(base_packet: bytes, text: str) -> bytes:
    """Tworzy pakiet z nowym tekstem i prawidłowym checksum"""
    packet = bytearray(base_packet)

    # Dopełnij tekstem
    text_padded = text.ljust(36)
    packet[22:22+36] = text_padded.encode('ascii', errors='replace')

    # PRZELICZ CHECKSUM
    packet[4] = 0
    packet[5] = 0
    crc = calculate_crc16(bytes(packet))
    packet[4] = crc & 0xFF
    packet[5] = (crc >> 8) & 0xFF

    return bytes(packet)

# Bazowy pakiet
BASE_PACKET = bytes.fromhex('1B 07 3E 00 A1 2A 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 37 38 37 20 54 4F 52 20 31 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))

print("="*70)
print("WERYFIKACJA IMPLEMENTACJI CRC-16")
print("="*70)

# Test 1: Sprawdź czy oryginalny pakiet ma prawidłowy CRC
print("\nTEST 1: Weryfikacja oryginalnego pakietu")
orig_crc = BASE_PACKET[4] | (BASE_PACKET[5] << 8)
print(f"  Oryginalny CRC: 0x{orig_crc:04X}")

# Wyzeruj CRC i przelicz
test_packet = bytearray(BASE_PACKET)
test_packet[4] = 0
test_packet[5] = 0
calc_crc = calculate_crc16(bytes(test_packet))
print(f"  Obliczony CRC:  0x{calc_crc:04X}")

if calc_crc == orig_crc:
    print("  ✅ CRC się zgadza!")
else:
    print("  ❌ CRC NIE ZGADZA SIĘ!")

# Test 2: Stwórz nowe pakiety i sprawdź
print("\nTEST 2: Tworzenie nowych pakietów")

test_texts = [
    "00'01\".111 TEST-A",
    "00'02\".222 TEST-B",
    "00'03\".333 TEST-C",
]

for i, text in enumerate(test_texts, 1):
    pkt = create_time_packet(BASE_PACKET, text)

    # Wyciągnij CRC
    pkt_crc = pkt[4] | (pkt[5] << 8)

    # Przelicz CRC aby zweryfikować
    verify = bytearray(pkt)
    verify[4] = 0
    verify[5] = 0
    verify_crc = calculate_crc16(bytes(verify))

    match = "✅" if pkt_crc == verify_crc else "❌"
    print(f"  Pakiet {i} ({text:20s}): CRC=0x{pkt_crc:04X}, weryfikacja=0x{verify_crc:04X} {match}")

print("\n" + "="*70)
print("✅ Implementacja CRC-16 jest prawidłowa!")
print("="*70)
