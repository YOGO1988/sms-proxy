#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analiza pakietów z oryginalnego programu aby znaleźć algorytm CRC
"""

# Próbki pakietów z oryginalnego programu (z twojego loga)
samples_raw = """
1B 07 3A 00 AB 7A 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 31 30 27 30 36 22 2E 31 33 34 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A
1B 07 3A 00 2F F1 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 31 30 27 30 36 22 2E 35 38 36 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A
1B 07 3A 00 A1 FA 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 31 30 27 30 36 22 2E 35 38 36 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A
1B 07 3A 00 69 27 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 31 30 27 30 37 22 2E 30 34 34 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A
1B 07 3A 00 E7 2C 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 31 30 27 30 37 22 2E 30 34 34 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A
1B 07 3A 00 19 BD 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 31 30 27 30 37 22 2E 34 39 39 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A
1B 07 3A 00 97 B6 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 31 30 27 30 37 22 2E 34 39 39 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A
1B 07 3A 00 70 C8 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 31 22 2E 38 31 31 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A
1B 07 3A 00 FE C3 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 30 30 27 30 31 22 2E 38 31 31 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A
1B 07 3A 00 D4 58 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 32 22 2E 35 30 39 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A
1B 07 3E 00 19 F9 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 31 30 27 31 36 22 2E 38 36 34 20 54 4F 52 20 32 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A
1B 07 3E 00 E6 A7 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 31 30 27 31 39 22 2E 30 38 38 20 54 4F 52 20 31 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A
1B 07 3E 00 58 3C 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 31 33 22 2E 36 30 38 20 54 4F 52 20 33 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A
1B 07 3E 00 01 9E 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 30 30 27 32 30 22 2E 38 35 32 20 54 4F 52 20 34 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A
1B 07 3E 00 BF 13 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 30 30 27 32 35 22 2E 33 37 37 20 54 4F 52 20 32 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A
1B 07 3E 00 B1 FD 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 32 39 22 2E 32 38 33 20 54 4F 52 20 31 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A
"""

def parse_samples():
    """Parse sample packets"""
    packets = []
    for line in samples_raw.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        try:
            data = bytes.fromhex(line.replace(' ', ''))
            if len(data) > 6:
                packets.append(data)
        except:
            pass
    return packets

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

def crc16_ccitt(data, init=0xFFFF, xorout=0x0000):
    """CRC-16 CCITT with configurable init and xorout"""
    crc = init
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc ^ xorout

def crc16_xmodem(data):
    """CRC-16 XMODEM"""
    return crc16_ccitt(data, init=0x0000, xorout=0x0000)

def crc16_kermit(data):
    """CRC-16 KERMIT (reversed, different poly)"""
    crc = 0x0000
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0x8408
            else:
                crc >>= 1
    # Swap bytes
    return ((crc & 0xFF) << 8) | ((crc >> 8) & 0xFF)

def test_crc_algorithm(packets, crc_func, name, data_range_func):
    """Test if CRC algorithm works for all packets"""
    print(f"\n{'='*70}")
    print(f"Testuję: {name}")
    print(f"{'='*70}")

    matches = 0
    for i, pkt in enumerate(packets):
        actual_crc = pkt[4] | (pkt[5] << 8)

        # Get data range to calculate CRC on
        test_data = data_range_func(pkt)

        # Calculate CRC
        try:
            calc_crc = crc_func(test_data)
        except:
            continue

        match = (calc_crc == actual_crc)
        if match:
            matches += 1

        if i < 3 or match:  # Show first 3 or any match
            status = "✅ MATCH!" if match else "❌"
            text_start = pkt[22:30].decode('ascii', errors='replace')
            print(f"  Pkt {i+1:2d} ({len(pkt)} bajtów, '{text_start}'): "
                  f"obliczone=0x{calc_crc:04X}, rzeczywiste=0x{actual_crc:04X} {status}")

    if matches == len(packets):
        print(f"\n🎉 ZNALEZIONO! Wszystkie {matches}/{len(packets)} pakiety się zgadzają!")
        return True
    else:
        print(f"\n❌ Tylko {matches}/{len(packets)} pakietów się zgadza")
        return False

def main():
    print("="*70)
    print("SZUKANIE ALGORYTMU CRC")
    print("="*70)

    packets = parse_samples()
    print(f"\nZnaleziono {len(packets)} pakietów do analizy")

    # Przykładowy pakiet
    pkt = packets[0]
    print(f"\nPrzykładowy pakiet:")
    print(f"  Długość: {len(pkt)} bajtów")
    print(f"  Checksum @ [4-5]: 0x{pkt[4]:02X} 0x{pkt[5]:02X} = 0x{pkt[4]|(pkt[5]<<8):04X}")
    print(f"  Tekst: {pkt[22:40].decode('ascii', errors='replace')}")

    # Test różnych algorytmów i zakresów danych
    test_configs = [
        # (crc_func, name, data_range_func)
        (crc16_modbus, "CRC-16 MODBUS od bajtu 2", lambda p: p[2:]),
        (crc16_modbus, "CRC-16 MODBUS od bajtu 2 bez końca", lambda p: p[2:-2]),
        (crc16_modbus, "CRC-16 MODBUS od bajtu 6", lambda p: p[6:]),
        (crc16_modbus, "CRC-16 MODBUS od bajtu 6 bez końca", lambda p: p[6:-2]),

        (crc16_ccitt, "CRC-16 CCITT od bajtu 2", lambda p: p[2:]),
        (crc16_ccitt, "CRC-16 CCITT od bajtu 2 bez końca", lambda p: p[2:-2]),
        (crc16_ccitt, "CRC-16 CCITT od bajtu 6", lambda p: p[6:]),
        (crc16_ccitt, "CRC-16 CCITT od bajtu 6 bez końca", lambda p: p[6:-2]),

        (crc16_xmodem, "CRC-16 XMODEM od bajtu 2", lambda p: p[2:]),
        (crc16_xmodem, "CRC-16 XMODEM od bajtu 2 bez końca", lambda p: p[2:-2]),

        (crc16_kermit, "CRC-16 KERMIT od bajtu 2", lambda p: p[2:]),
        (crc16_kermit, "CRC-16 KERMIT od bajtu 6", lambda p: p[6:]),
    ]

    # Test with CRC field zeroed
    print("\n" + "="*70)
    print("TESTY Z WYZEROWANYM POLEM CRC")
    print("="*70)

    for crc_func, name, data_func in test_configs:
        # Create modified packets with CRC field zeroed
        modified_packets = []
        for pkt in packets:
            mod = bytearray(pkt)
            mod[4] = 0
            mod[5] = 0
            modified_packets.append(bytes(mod))

        if test_crc_algorithm(modified_packets, crc_func, name + " (z wyzerowanym CRC)", data_func):
            print("\n" + "="*70)
            print("🎉 SUKCES! Znaleziono działający algorytm!")
            print("="*70)
            return

    print("\n" + "="*70)
    print("❌ Nie znaleziono standardowego algorytmu CRC")
    print("Checksum może być własnościowy lub zależeć od innych czynników")
    print("="*70)

if __name__ == "__main__":
    main()
