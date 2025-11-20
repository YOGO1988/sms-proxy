#!/usr/bin/env python3
"""Test brightness CRC calculation"""

def calculate_crc16(data: bytes) -> int:
    """CRC16 MODBUS"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc


# Known working packets
KNOWN_PACKETS = {
    0: bytes.fromhex('1B 06 0C 00 FB E8 00 00 00 00 0D 0A'.replace(' ', '')),
    9: bytes.fromhex('1B 06 0C 00 8C 1B 00 00 09 00 0D 0A'.replace(' ', '')),
    15: bytes.fromhex('1B 06 0C 00 15 3C 00 00 0F 00 0D 0A'.replace(' ', '')),
}

print("="*70)
print("BRIGHTNESS CRC VERIFICATION")
print("="*70)

for brightness, packet in KNOWN_PACKETS.items():
    print(f"\n📊 Brightness: {brightness}")
    print(f"   Packet: {packet.hex(' ')}")

    # Extract CRC from packet
    expected_crc_low = packet[4]
    expected_crc_high = packet[5]
    expected_crc = (expected_crc_high << 8) | expected_crc_low
    print(f"   Expected CRC: 0x{expected_crc:04X} ({expected_crc})")

    # Test different data variants for CRC calculation
    test_variants = {
        "Variant 1: Full packet without ESC, CRC, CRLF":
            bytes([0x06, 0x0C, 0x00, 0x00, 0x00, 0x00, 0x00, brightness, 0x00]),

        "Variant 2: After CRC bytes":
            bytes([0x00, 0x00, brightness, 0x00]),

        "Variant 3: Full packet without ESC":
            bytes([0x06, 0x0C, 0x00, expected_crc_low, expected_crc_high, 0x00, 0x00, brightness, 0x00, 0x0D, 0x0A]),

        "Variant 4: Entire packet":
            bytes([0x1B, 0x06, 0x0C, 0x00, expected_crc_low, expected_crc_high, 0x00, 0x00, brightness, 0x00, 0x0D, 0x0A]),
    }

    for desc, data in test_variants.items():
        crc = calculate_crc16(data)
        match = "✅ MATCH!" if crc == expected_crc else "❌ No match"
        print(f"   {desc}")
        print(f"      Data: {data.hex(' ')}")
        print(f"      CRC:  0x{crc:04X} ({crc}) {match}")

print("\n" + "="*70)
print("Testing brightness 20 and 100...")
print("="*70)

for brightness in [20, 100]:
    print(f"\n📊 Brightness: {brightness}")

    # Use Variant 1 (seems most logical)
    data = bytes([0x06, 0x0C, 0x00, 0x00, 0x00, 0x00, 0x00, brightness, 0x00])
    crc = calculate_crc16(data)
    crc_low = crc & 0xFF
    crc_high = (crc >> 8) & 0xFF

    packet = bytes([0x1B, 0x06, 0x0C, 0x00, crc_low, crc_high, 0x00, 0x00, brightness, 0x00, 0x0D, 0x0A])

    print(f"   Data for CRC: {data.hex(' ')}")
    print(f"   CRC: 0x{crc:04X} (low=0x{crc_low:02X}, high=0x{crc_high:02X})")
    print(f"   Full packet: {packet.hex(' ').upper()}")
