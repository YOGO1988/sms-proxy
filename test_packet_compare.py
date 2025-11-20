#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Porównanie BAJT PO BAJCIE - oryginalny vs zmodyfikowany
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
    """
    Tworzy pakiet TIME z nowym tekstem
    """
    packet = bytearray(base_packet)

    # Tekst zaczyna się od bajtu 22
    text_padded = text.ljust(36)[:36]  # Dokładnie 36 znaków
    packet[22:58] = text_padded.encode('ascii', errors='replace')

    # Przelicz CRC (bajty 4-5)
    packet[4] = 0
    packet[5] = 0
    crc = calculate_crc16(bytes(packet))
    packet[4] = crc & 0xFF
    packet[5] = (crc >> 8) & 0xFF

    return bytes(packet)


# Oryginalny pakiet (DZIAŁA!)
ORIGINAL = bytes.fromhex('1B 07 3A 00 51 8B 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 34 36 37 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A')

# Tworzę zmodyfikowany pakiet
MODIFIED = create_time_packet("00'00\".000  - ", ORIGINAL)

print("="*70)
print("PORÓWNANIE BAJT PO BAJCIE")
print("="*70)

print(f"\nDługość oryginalnego: {len(ORIGINAL)} bajtów")
print(f"Długość zmodyfikowanego: {len(MODIFIED)} bajtów")

if len(ORIGINAL) != len(MODIFIED):
    print("\n❌ PROBLEM: RÓŻNE DŁUGOŚCI!")
else:
    print("✅ Długości się zgadzają")

# Porównaj bajt po bajcie
print("\n" + "="*70)
print("RÓŻNICE:")
print("="*70)
print(f"{'Pozycja':<8} {'Oryginal':<15} {'Zmodyfikowany':<15} {'ASCII':<20}")
print("-"*70)

differences = 0
for i in range(max(len(ORIGINAL), len(MODIFIED))):
    if i >= len(ORIGINAL):
        print(f"{i:<8} {'BRAK':<15} {MODIFIED[i]:02X} ({MODIFIED[i]:3d})   {'DODANY':<20}")
        differences += 1
    elif i >= len(MODIFIED):
        print(f"{i:<8} {ORIGINAL[i]:02X} ({ORIGINAL[i]:3d})   {'BRAK':<15} {'USUNIĘTY':<20}")
        differences += 1
    elif ORIGINAL[i] != MODIFIED[i]:
        orig_char = chr(ORIGINAL[i]) if 32 <= ORIGINAL[i] < 127 else '.'
        mod_char = chr(MODIFIED[i]) if 32 <= MODIFIED[i] < 127 else '.'
        print(f"{i:<8} {ORIGINAL[i]:02X} ({ORIGINAL[i]:3d})   {MODIFIED[i]:02X} ({MODIFIED[i]:3d})     '{orig_char}' -> '{mod_char}'")
        differences += 1

if differences == 0:
    print("✅ Pakiety są IDENTYCZNE!")
else:
    print(f"\n❌ Znaleziono {differences} różnic")

# Pokaż teksty
print("\n" + "="*70)
print("TEKST (bajty 22-57):")
print("="*70)
orig_text = ORIGINAL[22:58].decode('ascii', errors='replace')
mod_text = MODIFIED[22:58].decode('ascii', errors='replace')
print(f"Oryginalny:     '{orig_text}'")
print(f"Zmodyfikowany:  '{mod_text}'")

# Pokaż CRC
print("\n" + "="*70)
print("CRC (bajty 4-5):")
print("="*70)
print(f"Oryginalny:     0x{ORIGINAL[5]:02X}{ORIGINAL[4]:02X}")
print(f"Zmodyfikowany:  0x{MODIFIED[5]:02X}{MODIFIED[4]:02X}")

# Wyeksportuj pakiety do porównania
print("\n" + "="*70)
print("PAKIETY HEX:")
print("="*70)
print("\nOryginalny:")
print(' '.join(f'{b:02X}' for b in ORIGINAL))
print("\nZmodyfikowany:")
print(' '.join(f'{b:02X}' for b in MODIFIED))

print("\n" + "="*70)
