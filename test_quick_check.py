#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Szybki test - czy poprawka działa?
"""

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
    """POPRAWIONA funkcja"""
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


# Oryginalny pakiet
ORIGINAL = bytes.fromhex('1B 07 3A 00 51 8B 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 34 36 37 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A')

# Test 1: Czy zmiana tekstu zachowuje 0D 0A?
packet1 = create_time_packet("00'00\".000  - ", ORIGINAL)

print("="*70)
print("TEST POPRAWKI")
print("="*70)

print("\n1️⃣ Czy zachowuje 0D 0A na końcu?")
if packet1[56] == 0x0D and packet1[57] == 0x0A:
    print("   ✅ TAK! Bajty 56-57 = 0D 0A")
else:
    print(f"   ❌ NIE! Bajty 56-57 = {packet1[56]:02X} {packet1[57]:02X}")

print("\n2️⃣ Długość pakietu:")
print(f"   Oryginał:     {len(ORIGINAL)} bajtów")
print(f"   Zmodyfikowany: {len(packet1)} bajtów")
if len(ORIGINAL) == len(packet1):
    print("   ✅ ZGADZA SIĘ!")
else:
    print("   ❌ RÓŻNE!")

print("\n3️⃣ Tekst (bajty 22-55):")
text_orig = ORIGINAL[22:56].decode('ascii', errors='replace')
text_mod = packet1[22:56].decode('ascii', errors='replace')
print(f"   Oryginalny:     '{text_orig}'")
print(f"   Zmodyfikowany:  '{text_mod}'")

print("\n4️⃣ CRC:")
print(f"   Oryginalny:     0x{ORIGINAL[5]:02X}{ORIGINAL[4]:02X}")
print(f"   Zmodyfikowany:  0x{packet1[5]:02X}{packet1[4]:02X}")

print("\n5️⃣ Porównanie HEX:")
print("\nOryginalny:")
print(' '.join(f'{b:02X}' for b in ORIGINAL))
print("\nZmodyfikowany:")
print(' '.join(f'{b:02X}' for b in packet1))

# Test 2: Czy oryginalny tekst daje oryginalny pakiet?
print("\n" + "="*70)
print("TEST 2: Czy możemy odtworzyć ORYGINALNY pakiet?")
print("="*70)

packet2 = create_time_packet("00'07\".467  - ", ORIGINAL)

if packet2 == ORIGINAL:
    print("✅ TAK! Zmodyfikowany pakiet z oryginalnym tekstem = oryginalny pakiet!")
else:
    print("❌ NIE! Są różnice:")
    for i in range(len(ORIGINAL)):
        if ORIGINAL[i] != packet2[i]:
            print(f"   Bajt {i}: {ORIGINAL[i]:02X} != {packet2[i]:02X}")

print("\n" + "="*70)
print("WNIOSEK:")
if packet1[56] == 0x0D and packet1[57] == 0x0A and len(packet1) == 58:
    print("✅ POPRAWKA DZIAŁA! Teraz należy przetestować na prawdziwym urządzeniu!")
else:
    print("❌ Poprawka nie rozwiązała problemu")
print("="*70)
