#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Empiryczna analiza checksum - porównanie dwóch pakietów
"""

# Dwa pakiety które różnią się tylko tekstem
pkt1_hex = '1B 07 3E 00 A1 2A 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 37 38 37 20 54 4F 52 20 31 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'
pkt2_hex = '1B 07 3E 00 8F 5C 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 30 30 27 31 30 22 2E 33 36 32 20 54 4F 52 20 32 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'

pkt1 = bytes.fromhex(pkt1_hex.replace(' ', ''))
pkt2 = bytes.fromhex(pkt2_hex.replace(' ', ''))

print("="*80)
print("ANALIZA EMPIRYCZNA CHECKSUM")
print("="*80)

# Wypisz checksumę
crc1 = pkt1[4] | (pkt1[5] << 8)
crc2 = pkt2[4] | (pkt2[5] << 8)

print(f"\nPakiet 1: checksum = 0x{crc1:04X} (bajty: 0x{pkt1[4]:02X} 0x{pkt1[5]:02X})")
print(f"Pakiet 2: checksum = 0x{crc2:04X} (bajty: 0x{pkt2[4]:02X} 0x{pkt2[5]:02X})")
print(f"Różnica: {crc2 - crc1} (0x{(crc2-crc1)&0xFFFF:04X})")

# Różnice w bajtach
print("\nRóżnice w bajtach (oprócz checksum):")
for i in range(len(pkt1)):
    if i == 4 or i == 5:  # Skip checksum bytes
        continue
    if pkt1[i] != pkt2[i]:
        char1 = chr(pkt1[i]) if 32 <= pkt1[i] < 127 else '.'
        char2 = chr(pkt2[i]) if 32 <= pkt2[i] < 127 else '.'
        diff = pkt2[i] - pkt1[i]
        print(f"  [{i:2d}]: 0x{pkt1[i]:02X} ({char1:3}) -> 0x{pkt2[i]:02X} ({char2:3})  różnica: {diff:+4d} (0x{diff&0xFF:02X})")

# Spróbuj CRC-16 MODBUS ręcznie
print("\n" + "="*80)
print("PRÓBA: CRC-16 MODBUS (ręczna implementacja)")
print("="*80)

def crc16_modbus(data):
    """CRC-16 MODBUS"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc

# Spróbuj różne zakresy danych
ranges = [
    ("Cały pakiet", slice(0, None)),
    ("Od bajtu 2", slice(2, None)),
    ("Od bajtu 2, bez końcówki 0D 0A", slice(2, -2)),
    ("Od bajtu 6 (po checksum)", slice(6, None)),
    ("Od bajtu 6, bez końcówki", slice(6, -2)),
]

for desc, s in ranges:
    # Bez checksum
    data1 = bytearray(pkt1)
    data1[4] = 0
    data1[5] = 0
    test1 = bytes(data1[s])

    data2 = bytearray(pkt2)
    data2[4] = 0
    data2[5] = 0
    test2 = bytes(data2[s])

    calc1 = crc16_modbus(test1)
    calc2 = crc16_modbus(test2)

    match1 = "✓ MATCH!" if calc1 == crc1 else ""
    match2 = "✓ MATCH!" if calc2 == crc2 else ""

    print(f"\n{desc}:")
    print(f"  Pkt1: obliczone=0x{calc1:04X}, rzeczywiste=0x{crc1:04X} {match1}")
    print(f"  Pkt2: obliczone=0x{calc2:04X}, rzeczywiste=0x{crc2:04X} {match2}")

print("\n" + "="*80)
print("PRÓBA: CRC-16 CCITT")
print("="*80)

def crc16_ccitt(data, init=0xFFFF):
    """CRC-16 CCITT"""
    crc = init
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc

for desc, s in ranges:
    data1 = bytearray(pkt1)
    data1[4] = 0
    data1[5] = 0
    test1 = bytes(data1[s])

    data2 = bytearray(pkt2)
    data2[4] = 0
    data2[5] = 0
    test2 = bytes(data2[s])

    calc1 = crc16_ccitt(test1)
    calc2 = crc16_ccitt(test2)

    match1 = "✓ MATCH!" if calc1 == crc1 else ""
    match2 = "✓ MATCH!" if calc2 == crc2 else ""

    print(f"\n{desc}:")
    print(f"  Pkt1: obliczone=0x{calc1:04X}, rzeczywiste=0x{crc1:04X} {match1}")
    print(f"  Pkt2: obliczone=0x{calc2:04X}, rzeczywiste=0x{crc2:04X} {match2}")

print("\n" + "="*80)
print("Jeśli nadal brak dopasowania - tablica może:")
print("1. NIE sprawdzać checksum (mimo że wydaje się że sprawdza)")
print("2. Używać własnościowego algorytmu")
print("3. Checksum zależy od innych czynników (czas, licznik)")
print("="*80)
