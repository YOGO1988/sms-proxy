#!/usr/bin/env python3
"""
AUTOMATYCZNY TEST TABLICY LED - DWA TORY
Symuluje bieg dwóch zawodników i sprawdza wyświetlanie na dwóch liniach
"""

import serial
import time
from datetime import datetime

# ============================================================================
# FUNKCJE LED (skopiowane z chronometr_v5_LED.py)
# ============================================================================

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


def create_time_packet_line1(time_str: str, add_dash: bool = False) -> bytes:
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

    suffix = "  - " if add_dash else "  "
    text_padded = (formatted + suffix).ljust(34)[:34]
    base[22:56] = text_padded.encode('ascii', errors='replace')

    base[4] = 0
    base[5] = 0
    crc = calculate_crc16(bytes(base))
    base[4] = crc & 0xFF
    base[5] = (crc >> 8) & 0xFF

    return bytes(base)


def create_time_packet_line2(time_str: str, add_dash: bool = False) -> bytes:
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

    suffix = "  - " if add_dash else "  "
    text_padded = (formatted + suffix).ljust(34)[:34]
    base[22:56] = text_padded.encode('ascii', errors='replace')

    base[4] = 0
    base[5] = 0
    crc = calculate_crc16(bytes(base))
    base[4] = crc & 0xFF
    base[5] = (crc >> 8) & 0xFF

    return bytes(base)


# ============================================================================
# SKRYPT TESTOWY
# ============================================================================

def main():
    PORT = 'COM6'  # Zmień na swój port
    BAUDRATE = 9600

    print("=" * 60)
    print("TEST AUTOMATYCZNY - DWA TORY NA LED")
    print("=" * 60)
    print(f"Port: {PORT}")
    print(f"Baudrate: {BAUDRATE}")
    print()

    # Połączenie z LED
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

    # Czyszczenie ekranu
    print("\n🧹 Czyszczenie ekranu...")
    clear_line1 = bytes.fromhex('1B 07 54 00 14 75 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 2D 2D 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))
    clear_line2 = bytes.fromhex('1B 07 54 00 60 FC 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 2D 2D 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))
    ser.write(clear_line1)
    ser.flush()
    time.sleep(0.05)
    ser.write(clear_line2)
    ser.flush()
    time.sleep(0.5)

    # Test 1: Symulacja biegu - oba tory biegną
    print("\n📊 TEST 1: Symulacja biegu - oba tory biegną")
    print("-" * 60)

    start_time = time.time()
    for i in range(10):
        elapsed = time.time() - start_time
        time_str = f"00:{int(elapsed):02d}.{int((elapsed % 1) * 100):02d}"

        # Wysyłanie na LINIA 1 (TOR LEWY)
        packet1 = create_time_packet_line1(time_str, add_dash=False)
        ser.write(packet1)
        ser.flush()
        time.sleep(0.05)

        # Wysyłanie na LINIA 2 (TOR PRAWY)
        packet2 = create_time_packet_line2(time_str, add_dash=False)
        ser.write(packet2)
        ser.flush()

        print(f"  ⏱️  Czas: {time_str} (na obu liniach)")
        time.sleep(0.5)

    # Test 2: TOR LEWY kończy - pokazuje wynik z myślnikiem
    print("\n✅ TEST 2: TOR LEWY kończy - wynik z myślnikiem")
    print("-" * 60)
    left_result = "00:05.78"
    packet1 = create_time_packet_line1(left_result, add_dash=True)
    ser.write(packet1)
    ser.flush()
    print(f"  🏁 TOR LEWY zakończony: {left_result} -")
    time.sleep(0.1)

    # TOR PRAWY dalej biega
    print("\n⏱️  TOR PRAWY biega dalej...")
    for i in range(5):
        elapsed = 6.0 + i * 0.5
        time_str = f"00:{int(elapsed):02d}.{int((elapsed % 1) * 100):02d}"

        # LINIA 2 (TOR PRAWY) - dalej biega
        packet2 = create_time_packet_line2(time_str, add_dash=False)
        ser.write(packet2)
        ser.flush()

        print(f"  ⏱️  TOR PRAWY: {time_str}")
        time.sleep(0.5)

    # Test 3: TOR PRAWY kończy - pokazuje wynik z myślnikiem
    print("\n✅ TEST 3: TOR PRAWY kończy - wynik z myślnikiem")
    print("-" * 60)
    right_result = "00:08.42"
    packet2 = create_time_packet_line2(right_result, add_dash=True)
    ser.write(packet2)
    ser.flush()
    print(f"  🏁 TOR PRAWY zakończony: {right_result} -")
    time.sleep(2)

    # Podsumowanie
    print("\n" + "=" * 60)
    print("PODSUMOWANIE TESTU")
    print("=" * 60)
    print(f"✅ LINIA 1 (TOR LEWY):  {left_result} -")
    print(f"✅ LINIA 2 (TOR PRAWY): {right_result} -")
    print()
    print("Wyniki powinny być widoczne na obu liniach LED.")
    print("Każdy wynik powinien mieć myślnik (-) na końcu.")
    print()

    # Czyszczenie po teście
    time.sleep(3)
    print("🧹 Czyszczenie ekranu po teście...")
    ser.write(clear_line1)
    ser.flush()
    time.sleep(0.05)
    ser.write(clear_line2)
    ser.flush()

    ser.close()
    print("\n✅ Test zakończony pomyślnie!")


if __name__ == "__main__":
    main()
