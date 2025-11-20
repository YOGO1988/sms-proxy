#!/usr/bin/env python3
"""Ekstrakcja i analiza pakietów czasowych"""

REAL_PACKETS = {
    'time_01_758': bytes.fromhex('1B 07 3A 00 51 E1 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 31 22 2E 37 35 38 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),
    'time_05_429': bytes.fromhex('1B 07 3A 00 E9 7F 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 35 22 2E 34 32 39 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),
    'time_10_421': bytes.fromhex('1B 07 3A 00 7A 75 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 31 30 22 2E 34 32 31 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),
    'time_20_832': bytes.fromhex('1B 07 3A 00 2D EC 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 32 30 22 2E 38 33 32 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),
    'time_30_824': bytes.fromhex('1B 07 3A 00 31 3A 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 33 30 22 2E 38 32 34 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),
    'time_45_773': bytes.fromhex('1B 07 3A 00 E8 5E 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 34 35 22 2E 37 37 33 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),
    'time_7sec_tor1': bytes.fromhex('1B 07 3E 00 A1 2A 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 37 38 37 20 54 4F 52 20 31 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),
    'time_10sec_tor2': bytes.fromhex('1B 07 3E 00 8F 5C 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 30 30 27 31 30 22 2E 33 36 32 20 54 4F 52 20 32 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),
    'name_tymon': bytes.fromhex('1B 07 52 00 AA C2 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 54 79 6D 6F 6E 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 2D 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),
    'name_gabriel': bytes.fromhex('1B 07 54 00 1B 46 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 47 61 62 72 69 65 6C 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 2D 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),
}

print("="*80)
print("ANALIZA PAKIETÓW CZASOWYCH")
print("="*80)

for name, packet in sorted(REAL_PACKETS.items()):
    if 'time' in name or 'name' in name:
        # Podstawowe info
        cmd = packet[1]
        typ = packet[2]
        checksum = packet[4] | (packet[5] << 8)
        line = packet[18]

        # Część tekstowa zaczyna się od bajtu 22
        text_start = 22
        text_bytes = packet[text_start:]
        # Usuń końcówkę 0D 0A
        text_bytes = text_bytes[:-2]
        # Dekoduj i usuń spacje na końcu
        text = text_bytes.decode('ascii', errors='replace').rstrip()

        print(f"\n{name}:")
        print(f"  Cmd: 0x{cmd:02X}, Typ: 0x{typ:02X}, Line: 0x{line:02X}")
        print(f"  Checksum: 0x{checksum:04X} (bytes: 0x{packet[4]:02X} 0x{packet[5]:02X})")
        print(f"  Text: \"{text}\"")
        print(f"  Długość pakietu: {len(packet)} bajtów")

print("\n" + "="*80)
print("PRÓBA ZNALEZIENIA WZORU CHECKSUM")
print("="*80)

# Porównaj pakiety z różnymi czasami ale tym samym formatem
time_packets = [(k, v) for k, v in REAL_PACKETS.items() if k.startswith('time_') and 'tor' not in k]

print("\nPakiety bez 'TOR' (format '00'XX\".XXX  - '):")
for name, packet in time_packets:
    checksum = packet[4] | (packet[5] << 8)
    text = packet[22:-2].decode('ascii', errors='replace').rstrip()

    # Oblicz różne sumy
    suma_payload = sum(packet[22:-2])
    suma_all = sum(packet)
    suma_without_crc = sum(packet[:4]) + sum(packet[6:])

    print(f"\n{name}: CRC=0x{checksum:04X}")
    print(f"  Tekst: \"{text}\"")
    print(f"  Suma payload: 0x{suma_payload:04X}")
    print(f"  Suma all: 0x{suma_all:04X}")
    print(f"  Suma bez CRC: 0x{suma_without_crc:04X}")

    # Próbuj różne operacje
    diff = checksum - suma_payload
    print(f"  CRC - suma_payload = 0x{diff:04X} ({diff})")

print("\n" + "="*80)
print("STRUKTURA PAKIETU")
print("="*80)

p = REAL_PACKETS['time_05_429']
print("\nPrzykład: time_05_429 (czas 00'05\".429)")
print("\nBajt po bajcie (pierwsze 30):")
for i in range(30):
    char = chr(p[i]) if 32 <= p[i] < 127 else '.'
    print(f"  [{i:2d}] 0x{p[i]:02X}  '{char}'", end='')
    if i == 0: print("  <- ESC (1B)")
    elif i == 1: print("  <- Komenda (07 = display)")
    elif i == 2: print("  <- Typ (3A = time bez TOR)")
    elif i == 3: print("  <- 00")
    elif i == 4: print("  <- Checksum LOW")
    elif i == 5: print("  <- Checksum HIGH")
    elif i == 18: print("  <- Linia (00=linia1, 10=linia2)")
    elif i == 22: print("  <- Start tekstu ASCII")
    else: print()

print("\nTekst ASCII (od bajtu 22):")
text_bytes = p[22:-2]
print(f"  {text_bytes.decode('ascii')}")
print(f"  HEX: {text_bytes.hex(' ')}")
