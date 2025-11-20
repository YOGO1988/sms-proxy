#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test ALL known CRC-16 variants using crccheck library
"""

import crccheck

# Sample packets
samples = [
    "1B 07 3A 00 AB 7A 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 31 30 27 30 36 22 2E 31 33 34 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A",
    "1B 07 3A 00 2F F1 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 31 30 27 30 36 22 2E 35 38 36 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A",
    "1B 07 3A 00 A1 FA 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 31 30 27 30 36 22 2E 35 38 36 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A",
    "1B 07 3A 00 69 27 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 31 30 27 30 37 22 2E 30 34 34 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A",
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

def get_all_crc16_classes():
    """Get all CRC-16 classes from crccheck"""
    crc16_classes = []
    for name in dir(crccheck.crc):
        if 'Crc16' in name and not name.startswith('_'):
            try:
                obj = getattr(crccheck.crc, name)
                if isinstance(obj, type):
                    crc16_classes.append((name, obj))
            except:
                pass
    return crc16_classes

def test_crc_class(packets, name, crc_class, data_ranges):
    """Test a CRC class with different data ranges"""
    for range_desc, range_func in data_ranges:
        matches = 0
        for pkt in packets:
            # Get actual CRC from packet
            actual_crc = pkt[4] | (pkt[5] << 8)

            # Get data to calculate CRC on
            test_data = range_func(pkt)

            try:
                # Calculate CRC
                calc_crc = crc_class.calc(test_data)

                if calc_crc == actual_crc:
                    matches += 1
            except:
                pass

        if matches == len(packets):
            print(f"\n🎉 ZNALEZIONO: {name} - {range_desc}")
            print(f"   Wszystkie {matches}/{len(packets)} pakietów się zgadzają!")

            # Show examples
            for i, pkt in enumerate(packets[:3]):
                actual_crc = pkt[4] | (pkt[5] << 8)
                test_data = range_func(pkt)
                calc_crc = crc_class.calc(test_data)
                text = pkt[22:32].decode('ascii', errors='replace')
                print(f"   Pkt {i+1} ('{text}'): obliczone=0x{calc_crc:04X}, rzeczywiste=0x{actual_crc:04X} ✅")

            return True
    return False

def main():
    print("="*70)
    print("TEST WSZYSTKICH WARIANTÓW CRC-16")
    print("="*70)

    packets = parse_packets()
    print(f"\nZnaleziono {len(packets)} pakietów do analizy")

    # Get all CRC-16 classes
    crc16_classes = get_all_crc16_classes()
    print(f"Znaleziono {len(crc16_classes)} wariantów CRC-16 do przetestowania\n")

    # Data ranges to test
    data_ranges = [
        ("od bajtu 2 (bez 1B 07)", lambda p: bytearray(p[2:4]) + bytearray([0, 0]) + bytearray(p[6:])),
        ("od bajtu 2 bez końca", lambda p: bytearray(p[2:4]) + bytearray([0, 0]) + bytearray(p[6:-2])),
        ("od bajtu 6 (po CRC)", lambda p: p[6:]),
        ("od bajtu 6 bez końca", lambda p: p[6:-2]),
        ("cały pakiet z CRC=0", lambda p: bytearray(p[:4]) + bytearray([0, 0]) + bytearray(p[6:])),
        ("od bajtu 2 z CRC=0 (całość)", lambda p: bytearray(p[2:][:2]) + bytearray([0, 0]) + bytearray(p[6:])),
    ]

    # Test each CRC class
    found = False
    for name, crc_class in crc16_classes:
        if test_crc_class(packets, name, crc_class, data_ranges):
            found = True
            break

    if not found:
        print("\n" + "="*70)
        print("❌ Nie znaleziono pasującego algorytmu CRC-16")
        print("="*70)
        print("\nDostępne algorytmy CRC-16:")
        for name, _ in crc16_classes:
            print(f"  - {name}")

if __name__ == "__main__":
    main()
