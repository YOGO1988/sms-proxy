#!/usr/bin/env python3
"""
SKRYPT DIAGNOSTYCZNY - DWA TORY LED
Symuluje dwa scenariusze:
1. TOR 1 kończy pierwszy (DZIAŁA)
2. TOR 2 kończy pierwszy (NIE DZIAŁA)
"""

import serial
import time
from datetime import datetime


def calculate_crc16(data: bytes) -> int:
    """CRC-16-CCITT dla protokołu tablicy LED"""
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


def create_init_packet_line1(text: str = "") -> bytes:
    """Pakiet inicjalizacyjny dla linii 1"""
    base = bytearray.fromhex('1B 06 E8 00 C0 2C 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 54 4F 52 20 31 20 20 20 20 30 29 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))

    if text:
        text_padded = text.ljust(34)[:34]
        base[22:56] = text_padded.encode('ascii', errors='replace')

    base[4] = 0
    base[5] = 0
    crc = calculate_crc16(bytes(base))
    base[4] = crc & 0xFF
    base[5] = (crc >> 8) & 0xFF

    return bytes(base)


def create_init_packet_line2(text: str = "") -> bytes:
    """Pakiet inicjalizacyjny dla linii 2"""
    base = bytearray.fromhex('1B 06 E8 00 94 AD 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 54 4F 52 20 32 20 20 20 20 30 29 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))

    if text:
        text_padded = text.ljust(34)[:34]
        base[22:56] = text_padded.encode('ascii', errors='replace')

    base[4] = 0
    base[5] = 0
    crc = calculate_crc16(bytes(base))
    base[4] = crc & 0xFF
    base[5] = (crc >> 8) & 0xFF

    return bytes(base)


def create_time_packet_line1(time_str: str) -> bytes:
    """Pakiet czasu dla linii 1"""
    base = bytearray.fromhex('1B 07 3A 00 51 8B 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 34 36 37 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))

    parts = time_str.split(':')
    if len(parts) == 2:
        minutes = parts[0]
        sec_parts = parts[1].split('.')
        if len(sec_parts) == 2:
            formatted = f"{minutes}'{sec_parts[0]}\".{sec_parts[1]}"
        else:
            formatted = f"{minutes}'{parts[1]}\""
    else:
        formatted = time_str

    text_padded = (formatted + "  ").ljust(34)[:34]
    base[22:56] = text_padded.encode('ascii', errors='replace')

    base[4] = 0
    base[5] = 0
    crc = calculate_crc16(bytes(base))
    base[4] = crc & 0xFF
    base[5] = (crc >> 8) & 0xFF

    return bytes(base)


def create_time_packet_line2(time_str: str) -> bytes:
    """Pakiet czasu dla linii 2"""
    base = bytearray.fromhex('1B 07 3A 00 51 8B 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 30 30 27 30 37 22 2E 34 36 37 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))

    parts = time_str.split(':')
    if len(parts) == 2:
        minutes = parts[0]
        sec_parts = parts[1].split('.')
        if len(sec_parts) == 2:
            formatted = f"{minutes}'{sec_parts[0]}\".{sec_parts[1]}"
        else:
            formatted = f"{minutes}'{parts[1]}\""
    else:
        formatted = time_str

    text_padded = (formatted + "  ").ljust(34)[:34]
    base[22:56] = text_padded.encode('ascii', errors='replace')

    base[4] = 0
    base[5] = 0
    crc = calculate_crc16(bytes(base))
    base[4] = crc & 0xFF
    base[5] = (crc >> 8) & 0xFF

    return bytes(base)


def create_finish_packet_line1(time_str: str) -> bytes:
    """Pakiet finałowy dla linii 1"""
    base = bytearray.fromhex('1B 07 3E 00 A1 2A 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 37 38 37 20 54 4F 52 20 31 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))

    parts = time_str.split(':')
    if len(parts) == 2:
        minutes = parts[0]
        sec_parts = parts[1].split('.')
        if len(sec_parts) == 2:
            formatted = f"{minutes}'{sec_parts[0]}\".{sec_parts[1]}"
        else:
            formatted = f"{minutes}'{parts[1]}\""
    else:
        formatted = time_str

    display_text = f"{formatted} TOR 1 ".ljust(38)[:38]
    base[22:60] = display_text.encode('ascii', errors='replace')

    base[4] = 0
    base[5] = 0
    crc = calculate_crc16(bytes(base))
    base[4] = crc & 0xFF
    base[5] = (crc >> 8) & 0xFF

    return bytes(base)


def create_finish_packet_line2(time_str: str) -> bytes:
    """Pakiet finałowy dla linii 2"""
    base = bytearray.fromhex('1B 07 3E 00 8F 5C 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 30 30 27 31 30 22 2E 33 36 32 20 54 4F 52 20 32 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))

    parts = time_str.split(':')
    if len(parts) == 2:
        minutes = parts[0]
        sec_parts = parts[1].split('.')
        if len(sec_parts) == 2:
            formatted = f"{minutes}'{sec_parts[0]}\".{sec_parts[1]}"
        else:
            formatted = f"{minutes}'{parts[1]}\""
    else:
        formatted = time_str

    display_text = f"{formatted} TOR 2 ".ljust(38)[:38]
    base[22:60] = display_text.encode('ascii', errors='replace')

    base[4] = 0
    base[5] = 0
    crc = calculate_crc16(bytes(base))
    base[4] = crc & 0xFF
    base[5] = (crc >> 8) & 0xFF

    return bytes(base)


def main():
    PORT = 'COM6'  # Zmień na swój port
    BAUDRATE = 9600

    print("=" * 70)
    print("SKRYPT DIAGNOSTYCZNY - DWA TORY LED")
    print("=" * 70)
    print(f"Port: {PORT}")
    print(f"Baudrate: {BAUDRATE}")
    print()

    # Połączenie
    try:
        ser = serial.Serial(
            port=PORT,
            baudrate=BAUDRATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
        print(f"✅ Połączono z {PORT}")
        time.sleep(0.3)
    except Exception as e:
        print(f"❌ BŁĄD: Nie można połączyć z {PORT}")
        print(f"   Szczegóły: {e}")
        return

    # Czyszczenie
    print("\n🧹 Czyszczenie ekranu...")
    clear_line1 = bytes.fromhex('1B 07 54 00 14 75 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 2D 2D 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))
    clear_line2 = bytes.fromhex('1B 07 54 00 60 FC 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 2D 2D 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))
    ser.write(clear_line1)
    ser.flush()
    time.sleep(0.05)
    ser.write(clear_line2)
    ser.flush()
    time.sleep(1)

    # ========================================================================
    # SCENARIUSZ 1: TOR 1 KOŃCZY PIERWSZY (DZIAŁA POPRAWNIE)
    # ========================================================================
    print("\n" + "=" * 70)
    print("SCENARIUSZ 1: TOR 1 KOŃCZY PIERWSZY (powinien działać)")
    print("=" * 70)

    # Inicjalizacja
    print("\n📺 Wysyłam pakiety INIT...")
    init1 = create_init_packet_line1("TOR 1    0)")
    init2 = create_init_packet_line2("TOR 2    0)")
    ser.write(init1)
    ser.flush()
    print(f"   ✅ INIT LINIA 1: TOR 1    0)")
    time.sleep(0.1)
    ser.write(init2)
    ser.flush()
    print(f"   ✅ INIT LINIA 2: TOR 2    0)")
    time.sleep(0.5)

    # Symulacja biegu - oba tory biegną
    print("\n⏱️  Symulacja biegu - oba tory biegną...")
    start_time = time.time()
    for i in range(5):
        elapsed = time.time() - start_time
        time_str = f"00:{int(elapsed):02d}.{int((elapsed % 1) * 100):02d}"

        packet1 = create_time_packet_line1(time_str)
        ser.write(packet1)
        ser.flush()
        print(f"   📤 LINIA 1: {time_str}")
        time.sleep(0.05)

        packet2 = create_time_packet_line2(time_str)
        ser.write(packet2)
        ser.flush()
        print(f"   📤 LINIA 2: {time_str}")
        time.sleep(0.4)

    # TOR 1 kończy
    print("\n🏁 TOR 1 KOŃCZY PIERWSZY!")
    tor1_time = "00:05.23"
    packet1_finish = create_finish_packet_line1(tor1_time)
    ser.write(packet1_finish)
    ser.flush()
    print(f"   ✅ LINIA 1: {tor1_time} TOR 1 (pakiet 0x3E)")
    time.sleep(0.1)

    # TOR 2 biegnie dalej
    print("\n⏱️  TOR 2 biegnie dalej...")
    for i in range(3):
        elapsed = 6.0 + i * 0.5
        time_str = f"00:{int(elapsed):02d}.{int((elapsed % 1) * 100):02d}"

        packet2 = create_time_packet_line2(time_str)
        ser.write(packet2)
        ser.flush()
        print(f"   📤 LINIA 2: {time_str}")
        time.sleep(0.5)

    # TOR 2 kończy
    print("\n🏁 TOR 2 KOŃCZY!")
    tor2_time = "00:07.89"
    packet2_finish = create_finish_packet_line2(tor2_time)
    ser.write(packet2_finish)
    ser.flush()
    print(f"   ✅ LINIA 2: {tor2_time} TOR 2 (pakiet 0x3E)")

    print("\n✅ SCENARIUSZ 1 ZAKOŃCZONY")
    print(f"   LINIA 1: {tor1_time} TOR 1")
    print(f"   LINIA 2: {tor2_time} TOR 2")
    time.sleep(3)

    # Czyszczenie
    ser.write(clear_line1)
    ser.flush()
    time.sleep(0.05)
    ser.write(clear_line2)
    ser.flush()
    time.sleep(2)

    # ========================================================================
    # SCENARIUSZ 2: TOR 2 KOŃCZY PIERWSZY (NIE DZIAŁA - TESTUJEMY)
    # ========================================================================
    print("\n" + "=" * 70)
    print("SCENARIUSZ 2: TOR 2 KOŃCZY PIERWSZY (problem do zdiagnozowania)")
    print("=" * 70)

    # Inicjalizacja
    print("\n📺 Wysyłam pakiety INIT...")
    init1 = create_init_packet_line1("TOR 1    0)")
    init2 = create_init_packet_line2("TOR 2    0)")
    ser.write(init1)
    ser.flush()
    print(f"   ✅ INIT LINIA 1: TOR 1    0)")
    time.sleep(0.1)
    ser.write(init2)
    ser.flush()
    print(f"   ✅ INIT LINIA 2: TOR 2    0)")
    time.sleep(0.5)

    # Symulacja biegu - oba tory biegną
    print("\n⏱️  Symulacja biegu - oba tory biegną...")
    start_time = time.time()
    for i in range(5):
        elapsed = time.time() - start_time
        time_str = f"00:{int(elapsed):02d}.{int((elapsed % 1) * 100):02d}"

        packet1 = create_time_packet_line1(time_str)
        ser.write(packet1)
        ser.flush()
        print(f"   📤 LINIA 1: {time_str}")
        time.sleep(0.05)

        packet2 = create_time_packet_line2(time_str)
        ser.write(packet2)
        ser.flush()
        print(f"   📤 LINIA 2: {time_str}")
        time.sleep(0.4)

    # TOR 2 KOŃCZY PIERWSZY (to jest krytyczny moment!)
    print("\n🏁 TOR 2 KOŃCZY PIERWSZY!")
    tor2_time = "00:05.67"
    packet2_finish = create_finish_packet_line2(tor2_time)
    print(f"   📤 Wysyłam pakiet finałowy na LINIĘ 2...")
    ser.write(packet2_finish)
    ser.flush()
    print(f"   ✅ LINIA 2: {tor2_time} TOR 2 (pakiet 0x3E)")
    print(f"   ❓ CZY WYŚWIETLIŁO SIĘ NA LINII 2? (sprawdź tablicę!)")
    time.sleep(0.1)

    # TOR 1 biegnie dalej
    print("\n⏱️  TOR 1 biegnie dalej...")
    for i in range(3):
        elapsed = 6.0 + i * 0.5
        time_str = f"00:{int(elapsed):02d}.{int((elapsed % 1) * 100):02d}"

        packet1 = create_time_packet_line1(time_str)
        ser.write(packet1)
        ser.flush()
        print(f"   📤 LINIA 1: {time_str}")
        time.sleep(0.5)

    # TOR 1 kończy
    print("\n🏁 TOR 1 KOŃCZY!")
    tor1_time = "00:08.12"
    packet1_finish = create_finish_packet_line1(tor1_time)
    ser.write(packet1_finish)
    ser.flush()
    print(f"   ✅ LINIA 1: {tor1_time} TOR 1 (pakiet 0x3E)")

    print("\n✅ SCENARIUSZ 2 ZAKOŃCZONY")
    print(f"   LINIA 1: {tor1_time} TOR 1")
    print(f"   LINIA 2: {tor2_time} TOR 2")
    print()
    print("❓ DIAGNO ZA:")
    print("   - Czy na LINII 2 wyświetlił się wynik TOR 2?")
    print("   - Czy wynik był widoczny przez cały czas aż do końca TOR 1?")
    print("   - Jeśli LINIA 2 była pusta, to jest to BUG!")

    time.sleep(3)

    # Czyszczenie
    print("\n🧹 Czyszczenie ekranu...")
    ser.write(clear_line1)
    ser.flush()
    time.sleep(0.05)
    ser.write(clear_line2)
    ser.flush()

    ser.close()
    print("\n✅ Test zakończony!")


if __name__ == "__main__":
    main()
