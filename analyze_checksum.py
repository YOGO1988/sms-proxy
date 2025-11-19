#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analiza checksum z działających pakietów
"""

# Działające pakiety z Twojego kodu
packets = {
    'time_7sec_tor1': '1B 07 3E 00 A1 2A 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 37 38 37 20 54 4F 52 20 31 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A',

    'time_10sec_tor2': '1B 07 3E 00 8F 5C 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 30 30 27 31 30 22 2E 33 36 32 20 54 4F 52 20 32 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A',

    'time_7sec': '1B 07 3A 00 51 8B 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 34 36 37 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A',

    'lane1': '1B 08 E8 00 E8 71 00 00 01 00 00 00 00 00 00 00 01 00 0A 00 00 00 00 00 00 00 00 00 5B 00 54 4F 52 20 31 20 20 20 30 29 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 0D 0A',

    'lane2': '1B 08 E8 00 F8 77 00 00 01 00 00 00 00 00 00 00 02 00 0A 00 00 00 10 00 00 00 00 00 38 00 54 4F 52 20 32 20 20 20 30 29 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 0D 0A',
}

def analyze_checksum():
    """Próba zrozumienia jak działa checksum"""

    print("="*80)
    print("ANALIZA CHECKSUM")
    print("="*80)

    for name, hex_str in packets.items():
        data = bytes.fromhex(hex_str.replace(' ', ''))

        print(f"\n{name}:")
        print(f"  Długość: {len(data)} bajtów")
        print(f"  Typ komendy: 0x{data[1]:02X}")
        print(f"  Typ pakietu: 0x{data[2]:02X}")
        print(f"  Checksum @ [4-5]: 0x{data[4]:02X} 0x{data[5]:02X} = {data[4] | (data[5] << 8)}")

        # Spróbuj różnych algorytmów CRC
        crc_data = data[2:]  # Od typu pakietu do końca (bez 1B 07)

        # Próba 1: Suma wszystkich bajtów
        sum_all = sum(crc_data) & 0xFFFF
        print(f"  Suma (od [2]): 0x{sum_all:04X}")

        # Próba 2: XOR
        xor_all = 0
        for b in crc_data:
            xor_all ^= b
        print(f"  XOR (od [2]): 0x{xor_all:02X}")

        # Próba 3: CRC-16 (różne warianty)
        try:
            import crcmod

            # CRC-16-CCITT
            crc16_ccitt = crcmod.predefined.mkCrcFun('crc-16')
            print(f"  CRC-16-CCITT: 0x{crc16_ccitt(crc_data):04X}")

            # CRC-16-MODBUS
            crc16_modbus = crcmod.predefined.mkCrcFun('modbus')
            print(f"  CRC-16-MODBUS: 0x{crc16_modbus(crc_data):04X}")

        except ImportError:
            print("  (crcmod nie zainstalowany - pomiń testy CRC)")

        # Spróbuj bez końcówki 0D 0A
        crc_data_no_end = data[2:-2]
        sum_no_end = sum(crc_data_no_end) & 0xFFFF
        print(f"  Suma (bez 0D 0A): 0x{sum_no_end:04X}")


def compare_similar_packets():
    """Porównaj podobne pakiety aby zobaczyć jak checksum się zmienia"""

    print("\n")
    print("="*80)
    print("PORÓWNANIE: time_7sec_tor1 vs time_10sec_tor2")
    print("="*80)

    p1 = bytes.fromhex(packets['time_7sec_tor1'].replace(' ', ''))
    p2 = bytes.fromhex(packets['time_10sec_tor2'].replace(' ', ''))

    print(f"\nDługość: {len(p1)} vs {len(p2)}")
    print(f"Checksum: 0x{p1[4]:02X}{p1[5]:02X} vs 0x{p2[4]:02X}{p2[5]:02X}")

    print("\nRóżnice w bajtach:")
    for i in range(min(len(p1), len(p2))):
        if p1[i] != p2[i]:
            char1 = chr(p1[i]) if 32 <= p1[i] < 127 else '.'
            char2 = chr(p2[i]) if 32 <= p2[i] < 127 else '.'
            print(f"  [{i:2d}]: 0x{p1[i]:02X} ({char1}) -> 0x{p2[i]:02X} ({char2})")

    print("\n")
    print("="*80)
    print("PORÓWNANIE: lane1 vs lane2")
    print("="*80)

    p1 = bytes.fromhex(packets['lane1'].replace(' ', ''))
    p2 = bytes.fromhex(packets['lane2'].replace(' ', ''))

    print(f"\nDługość: {len(p1)} vs {len(p2)}")
    print(f"Checksum: 0x{p1[4]:02X}{p1[5]:02X} vs 0x{p2[4]:02X}{p2[5]:02X}")

    print("\nRóżnice w bajtach (pierwsze 50):")
    for i in range(min(50, len(p1), len(p2))):
        if p1[i] != p2[i]:
            char1 = chr(p1[i]) if 32 <= p1[i] < 127 else '.'
            char2 = chr(p2[i]) if 32 <= p2[i] < 127 else '.'
            print(f"  [{i:2d}]: 0x{p1[i]:02X} ({char1}) -> 0x{p2[i]:02X} ({char2})")


def try_calculate_checksum():
    """Spróbuj obliczyć checksum dla znanego pakietu"""

    print("\n")
    print("="*80)
    print("PRÓBA OBLICZENIA CHECKSUM")
    print("="*80)

    # Użyj time_7sec_tor1 jako przykładu
    hex_str = packets['time_7sec_tor1']
    data = bytes.fromhex(hex_str.replace(' ', ''))

    actual_crc = data[4] | (data[5] << 8)
    print(f"\nRzeczywisty checksum: 0x{actual_crc:04X} (0x{data[4]:02X}, 0x{data[5]:02X})")

    # Spróbuj różnych zakresów danych
    ranges = [
        ("Cały pakiet (od [0])", data[0:]),
        ("Od typu pakietu (od [2])", data[2:]),
        ("Od typu pakietu bez CRC (od [6])", data[6:]),
        ("Od typu pakietu bez CRC i bez końca (od [6] do [-2])", data[6:-2]),
        ("Tylko payload (od [22])", data[22:]),
        ("Tylko payload bez końca (od [22] do [-2])", data[22:-2]),
    ]

    for desc, test_data in ranges:
        print(f"\n{desc}:")

        # Suma
        s = sum(test_data) & 0xFFFF
        match = "✓ MATCH!" if s == actual_crc else ""
        print(f"  Suma: 0x{s:04X} {match}")

        # Suma + długość
        s_len = (sum(test_data) + len(data)) & 0xFFFF
        match = "✓ MATCH!" if s_len == actual_crc else ""
        print(f"  Suma+długość: 0x{s_len:04X} {match}")

        # XOR sumy z długością
        s_xor = (sum(test_data) ^ len(data)) & 0xFFFF
        match = "✓ MATCH!" if s_xor == actual_crc else ""
        print(f"  Suma XOR długość: 0x{s_xor:04X} {match}")


if __name__ == "__main__":
    analyze_checksum()
    compare_similar_packets()
    try_calculate_checksum()

    print("\n")
    print("="*80)
    print("PODSUMOWANIE")
    print("="*80)
    print("Jeśli nie znaleziono dopasowania, checksum może być:")
    print("1. Własnościowy algorytm producenta")
    print("2. CRC z niestandardowymi parametrami")
    print("3. Zależny od innych danych (np. countera, czasu)")
    print()
    print("Rozwiązanie: Użyj działających pakietów jako szablonów")
    print("             i zamień TYLKO tekst (nie ruszaj checksum).")
    print("="*80)
