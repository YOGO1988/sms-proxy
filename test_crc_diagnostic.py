#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnoza CRC - sprawdza czy nasz algorytm działa
"""

# Oryginalny pakiet z led_display_final.py (DZIAŁA!)
ORIGINAL = bytes.fromhex('1B 07 3A 00 51 8B 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 34 36 37 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A')

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


print("="*70)
print("TEST CRC - Diagnoza algorytmu")
print("="*70)

# Oryginalny CRC z pakietu
original_crc_byte4 = ORIGINAL[4]
original_crc_byte5 = ORIGINAL[5]
print(f"\n1️⃣ Oryginalny CRC z pakietu:")
print(f"   Bajt 4: 0x{original_crc_byte4:02X} ({original_crc_byte4})")
print(f"   Bajt 5: 0x{original_crc_byte5:02X} ({original_crc_byte5})")
print(f"   Razem:  0x{original_crc_byte5:02X}{original_crc_byte4:02X}")

# Wyzeruj CRC i policz naszym algorytmem
packet_copy = bytearray(ORIGINAL)
packet_copy[4] = 0
packet_copy[5] = 0

calculated_crc = calculate_crc16(bytes(packet_copy))
calc_byte4 = calculated_crc & 0xFF
calc_byte5 = (calculated_crc >> 8) & 0xFF

print(f"\n2️⃣ CRC policzony naszym algorytmem:")
print(f"   Bajt 4: 0x{calc_byte4:02X} ({calc_byte4})")
print(f"   Bajt 5: 0x{calc_byte5:02X} ({calc_byte5})")
print(f"   Razem:  0x{calc_byte5:02X}{calc_byte4:02X}")

print(f"\n3️⃣ Porównanie:")
if calc_byte4 == original_crc_byte4 and calc_byte5 == original_crc_byte5:
    print("   ✅ CRC SIĘ ZGADZA! Algorytm jest DOBRY!")
else:
    print("   ❌ CRC SIĘ NIE ZGADZA!")
    print(f"   Różnica bajt 4: {calc_byte4 - original_crc_byte4}")
    print(f"   Różnica bajt 5: {calc_byte5 - original_crc_byte5}")

    # Sprawdź odwrotną kolejność
    print(f"\n4️⃣ Sprawdzam odwrotną kolejność bajtów...")
    if calc_byte4 == original_crc_byte5 and calc_byte5 == original_crc_byte4:
        print("   ✅ ZGADZA SIĘ po zamianie! Kolejność powinna być ODWROTNA!")
        print("   Poprawny kod:")
        print("   packet[4] = (crc >> 8) & 0xFF  # Starszy bajt")
        print("   packet[5] = crc & 0xFF         # Młodszy bajt")
    else:
        print("   ❌ Nawet po zamianie się nie zgadza")
        print("   PROBLEM: Algorytm CRC jest zły lub liczony dla złych bajtów")

print("\n" + "="*70)

# Test 2: Sprawdź długość pakietu
print("\n5️⃣ Informacje o pakiecie:")
print(f"   Długość całkowita: {len(ORIGINAL)} bajtów")
print(f"   Header bajt 2: 0x{ORIGINAL[2]:02X} (rozmiar?)")
print(f"   Tekst zaczyna się od bajtu 22")
print(f"   Tekst: {ORIGINAL[22:58].decode('ascii', errors='replace')!r}")

input("\nNaciśnij Enter...")
