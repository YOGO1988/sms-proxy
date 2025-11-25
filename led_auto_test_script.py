#!/usr/bin/env python3
"""
AUTOMATYCZNY SKRYPT TESTOWY LED - Symuluje chronometr z dwoma torami

Ten skrypt:
1. Łączy się z tablicą LED
2. Symuluje automatycznie oba scenariusze (TOR 1 i TOR 2 pierwszy)
3. Wyświetla szczegółowe logi diagnostyczne
4. Nie wymaga podpięcia czujników - wszystko jest automatyczne
"""

import serial
import time


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


def create_init_packet_line1(text: str = "TOR 1    0)") -> bytes:
    """Pakiet INIT dla linii 1"""
    base = bytearray.fromhex('1B 06 E8 00 C0 2C 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 54 4F 52 20 31 20 20 20 20 30 29 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))
    text_padded = text.ljust(34)[:34]
    base[22:56] = text_padded.encode('ascii', errors='replace')
    base[4] = 0
    base[5] = 0
    crc = calculate_crc16(bytes(base))
    base[4] = crc & 0xFF
    base[5] = (crc >> 8) & 0xFF
    return bytes(base)


def create_init_packet_line2(text: str = "TOR 2    0)") -> bytes:
    """Pakiet INIT dla linii 2"""
    base = bytearray.fromhex('1B 06 E8 00 94 AD 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 54 4F 52 20 32 20 20 20 20 30 29 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))
    text_padded = text.ljust(34)[:34]
    base[22:56] = text_padded.encode('ascii', errors='replace')
    base[4] = 0
    base[5] = 0
    crc = calculate_crc16(bytes(base))
    base[4] = crc & 0xFF
    base[5] = (crc >> 8) & 0xFF
    return bytes(base)


def create_time_packet_line1(time_str: str) -> bytes:
    """Pakiet czasu 0x3A dla linii 1"""
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
    """Pakiet czasu 0x3A dla linii 2"""
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
    """Pakiet finałowy 0x3E dla linii 1"""
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
    """Pakiet finałowy 0x3E dla linii 2"""
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


def clear_display(ser):
    """Czyści obie linie"""
    clear_line1 = bytes.fromhex('1B 07 54 00 14 75 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 2D 2D 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))
    clear_line2 = bytes.fromhex('1B 07 54 00 60 FC 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 2D 2D 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))
    ser.write(clear_line1)
    ser.flush()
    time.sleep(0.05)
    ser.write(clear_line2)
    ser.flush()


def run_test_scenario_2_first(ser):
    """Scenariusz: TOR 2 kończy pierwszy - PROBLEM DO NAPRAWY"""
    print("\n" + "="*70)
    print("SCENARIUSZ: TOR 2 KOŃCZY PIERWSZY")
    print("="*70)

    clear_display(ser)
    time.sleep(0.5)

    # INIT
    print("\n[1] Wysyłam pakiety INIT...")
    ser.write(create_init_packet_line1())
    ser.flush()
    print(f"    ✅ LINIA 1: TOR 1    0)")
    time.sleep(0.1)
    ser.write(create_init_packet_line2())
    ser.flush()
    print(f"    ✅ LINIA 2: TOR 2    0)")
    time.sleep(0.6)  # Czekamy >500ms (blokada)

    # Bieg - oba tory
    print("\n[2] Symulacja biegu - OBIE LINIE powinny pokazywać czas...")
    for i in range(4):
        t = f"00:0{i+1}.{50 + i*10:02d}"
        ser.write(create_time_packet_line1(t))
        ser.flush()
        print(f"    📤 LINIA 1: {t}")
        time.sleep(0.05)
        ser.write(create_time_packet_line2(t))
        ser.flush()
        print(f"    📤 LINIA 2: {t}")
        time.sleep(0.4)

    # TOR 2 kończy PIERWSZY
    print("\n[3] TOR 2 KOŃCZY PIERWSZY (to jest testowany przypadek!)")
    tor2_time = "00:04.85"
    ser.write(create_finish_packet_line2(tor2_time))
    ser.flush()
    print(f"    🏁 LINIA 2: {tor2_time} TOR 2")
    print(f"    ❓ CZY POJAWIŁ SIĘ NA TABLICY?")
    time.sleep(0.1)

    # TOR 1 biegnie dalej
    print("\n[4] TOR 1 biegnie dalej...")
    for i in range(3):
        t = f"00:0{5+i}.{20 + i*15:02d}"
        ser.write(create_time_packet_line1(t))
        ser.flush()
        print(f"    📤 LINIA 1: {t}")
        time.sleep(0.5)

    # TOR 1 kończy
    print("\n[5] TOR 1 kończy")
    tor1_time = "00:07.65"
    ser.write(create_finish_packet_line1(tor1_time))
    ser.flush()
    print(f"    🏁 LINIA 1: {tor1_time} TOR 1")

    print("\n" + "-"*70)
    print("WYNIK NA TABLICY:")
    print(f"  LINIA 1: {tor1_time} TOR 1")
    print(f"  LINIA 2: {tor2_time} TOR 2")
    print()
    print("DIAGNOZA:")
    print("  ✅ Jeśli obie linie pokazują wyniki → OK!")
    print("  ❌ Jeśli LINIA 2 jest pusta → BUG potwierdzony!")
    print("="*70)
    time.sleep(4)


def main():
    PORT = 'COM6'  # Zmień na odpowiedni port
    BAUDRATE = 9600

    print("="*70)
    print("AUTOMATYCZNY TEST LED - DWA TORY")
    print("="*70)
    print(f"Port: {PORT}")
    print()

    try:
        ser = serial.Serial(
            port=PORT,
            baudrate=BAUDRATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
        print(f"✅ Połączono z {PORT}\n")
        time.sleep(0.3)
    except Exception as e:
        print(f"❌ BŁĄD: {e}")
        return

    # Czyszczenie
    clear_display(ser)
    time.sleep(1)

    # Test scenariusza problematycznego
    run_test_scenario_2_first(ser)

    # Czyszczenie końcowe
    clear_display(ser)
    ser.close()
    print("\n✅ Test zakończony!")


if __name__ == "__main__":
    main()
