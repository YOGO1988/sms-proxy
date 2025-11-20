#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Szczegółowa analiza wzorców w checksum
Może checksum jest prostą sumą lub ma inny wzór?
"""

# Próbki pakietów
samples = [
    "1B 07 3A 00 AB 7A 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 31 30 27 30 36 22 2E 31 33 34 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A",
    "1B 07 3A 00 2F F1 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 31 30 27 30 36 22 2E 35 38 36 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A",
    "1B 07 3A 00 A1 FA 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 31 30 27 30 36 22 2E 35 38 36 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A",
    "1B 07 3A 00 70 C8 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 31 22 2E 38 31 31 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A",
    "1B 07 3A 00 FE C3 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 30 30 27 30 31 22 2E 38 31 31 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A",
]

def parse_packets():
    """Parse packets"""
    packets = []
    for hex_str in samples:
        data = bytes.fromhex(hex_str.replace(' ', ''))
        packets.append(data)
    return packets

def analyze_packet(pkt, idx):
    """Detailed packet analysis"""
    print(f"\n{'='*70}")
    print(f"PAKIET {idx+1}")
    print(f"{'='*70}")

    # Extract CRC
    crc_lo = pkt[4]
    crc_hi = pkt[5]
    crc = crc_lo | (crc_hi << 8)

    print(f"Długość: {len(pkt)} bajtów")
    print(f"CRC @ [4-5]: 0x{crc_lo:02X} 0x{crc_hi:02X} = 0x{crc:04X}")
    print(f"Tekst: '{pkt[22:35].decode('ascii', errors='replace')}'")

    # Compute various sums
    print(f"\nSumy różnych zakresów:")

    ranges = [
        ("Cały pakiet", slice(0, None)),
        ("Od [2] (bez 1B 07)", slice(2, None)),
        ("Od [2] bez CRC", slice(2, 4), slice(6, None)),
        ("Od [2] bez CRC i końca", slice(2, 4), slice(6, -2)),
        ("Od [6] (po CRC)", slice(6, None)),
        ("Od [6] bez końca", slice(6, -2)),
    ]

    for desc, *slices in ranges:
        # Concatenate slices
        if len(slices) == 1:
            data = pkt[slices[0]]
        else:
            data = b''.join(pkt[s] for s in slices)

        s = sum(data) & 0xFFFF
        s_inv = (~sum(data)) & 0xFFFF
        s_neg = (-sum(data)) & 0xFFFF

        match_sum = "✅" if s == crc else ""
        match_inv = "✅" if s_inv == crc else ""
        match_neg = "✅" if s_neg == crc else ""

        print(f"  {desc:30s}: suma=0x{s:04X} {match_sum}  ~suma=0x{s_inv:04X} {match_inv}  -suma=0x{s_neg:04X} {match_neg}")

    # Try XOR combinations
    print(f"\nCombinacje z innymi bajtami:")
    for i in [2, 3, 6, 7, 18, 19]:
        if i < len(pkt):
            val = pkt[i]
            xor_result = crc ^ val
            print(f"  CRC XOR pkt[{i}] (0x{val:02X}): 0x{xor_result:04X}")

def compare_similar_packets():
    """Compare packets with similar content"""
    print(f"\n{'='*70}")
    print("PORÓWNANIE PODOBNYCH PAKIETÓW")
    print(f"{'='*70}")

    packets = parse_packets()

    # Compare packets 2 and 3 (same text, different byte at [18])
    p1 = packets[1]  # "10'06".586", byte[18]=0x00
    p2 = packets[2]  # "10'06".586", byte[18]=0x10

    crc1 = p1[4] | (p1[5] << 8)
    crc2 = p2[4] | (p2[5] << 8)

    print(f"\nPakiet 2: CRC = 0x{crc1:04X}, byte[18] = 0x{p1[18]:02X}")
    print(f"Pakiet 3: CRC = 0x{crc2:04X}, byte[18] = 0x{p2[18]:02X}")
    print(f"Różnica CRC: 0x{(crc2-crc1)&0xFFFF:04X}")
    print(f"Różnica byte[18]: 0x{(p2[18]-p1[18])&0xFF:02X}")

    # Show all differences
    print(f"\nWszystkie różnice między pakietami 2 i 3:")
    for i in range(min(len(p1), len(p2))):
        if p1[i] != p2[i]:
            print(f"  [{i}]: 0x{p1[i]:02X} -> 0x{p2[i]:02X} (różnica: {p2[i]-p1[i]:+d})")

    # Compare packets 4 and 5 (same text, different byte at [18])
    p3 = packets[3]  # "00'01".811", byte[18]=0x00
    p4 = packets[4]  # "00'01".811", byte[18]=0x10

    crc3 = p3[4] | (p3[5] << 8)
    crc4 = p4[4] | (p4[5] << 8)

    print(f"\nPakiet 4: CRC = 0x{crc3:04X}, byte[18] = 0x{p3[18]:02X}")
    print(f"Pakiet 5: CRC = 0x{crc4:04X}, byte[18] = 0x{p4[18]:02X}")
    print(f"Różnica CRC: 0x{(crc4-crc3)&0xFFFF:04X}")
    print(f"Różnica byte[18]: 0x{(p4[18]-p3[18])&0xFF:02X}")

def main():
    print("="*70)
    print("SZCZEGÓŁOWA ANALIZA WZORCÓW CRC")
    print("="*70)

    packets = parse_packets()

    # Analyze each packet
    for i, pkt in enumerate(packets[:3]):  # First 3 packets
        analyze_packet(pkt, i)

    # Compare similar packets
    compare_similar_packets()

if __name__ == "__main__":
    main()
