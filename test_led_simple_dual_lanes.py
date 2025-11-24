#!/usr/bin/env python3
"""
TEST UPROSZCZONEJ LOGIKI - DWA NIEZALEŻNE TORY NA LED

ZASADA:
- TOR 1 → LINIA 1 (górna) - ZAWSZE
- TOR 2 → LINIA 2 (dolna) - ZAWSZE
- START: czas biegnie na obu liniach
- META TOR 1: zatrzymuje się tylko linia 1, pokazuje "TOR 1 00:05.78"
- META TOR 2: zatrzymuje się tylko linia 2, pokazuje "TOR 2 00:08.34"
"""

import serial
import time


# ============================================================================
# FUNKCJE LED
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


def create_time_packet_line1(time_str: str, lane_name: str = None) -> bytes:
    """
    Pakiet czasu dla linii 1 (TOR 1)
    Args:
        time_str: Czas w formacie "00:05.78"
        lane_name: Nazwa toru (np. "TOR 1") - wyświetla się na początku
    """
    base = bytearray.fromhex('1B 07 3A 00 51 8B 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 34 36 37 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))

    # Formatowanie czasu
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

    # Dodaj nazwę toru jeśli podana (wynik finałowy)
    if lane_name:
        text = f"{lane_name}    {formatted}"
    else:
        text = formatted

    text_padded = text.ljust(34)[:34]
    base[22:56] = text_padded.encode('ascii', errors='replace')

    # Przelicz CRC
    base[4] = 0
    base[5] = 0
    crc = calculate_crc16(bytes(base))
    base[4] = crc & 0xFF
    base[5] = (crc >> 8) & 0xFF

    return bytes(base)


def create_time_packet_line2(time_str: str, lane_name: str = None) -> bytes:
    """
    Pakiet czasu dla linii 2 (TOR 2)
    Args:
        time_str: Czas w formacie "00:05.78"
        lane_name: Nazwa toru (np. "TOR 2") - wyświetla się na początku
    """
    base = bytearray.fromhex('1B 07 3A 00 51 8B 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 30 30 27 30 37 22 2E 34 36 37 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))

    # Formatowanie czasu
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

    # Dodaj nazwę toru jeśli podana (wynik finałowy)
    if lane_name:
        text = f"{lane_name}    {formatted}"
    else:
        text = formatted

    text_padded = text.ljust(34)[:34]
    base[22:56] = text_padded.encode('ascii', errors='replace')

    # Przelicz CRC
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

    print("=" * 70)
    print("TEST UPROSZCZONEJ LOGIKI - DWA NIEZALEŻNE TORY")
    print("=" * 70)
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
    time.sleep(0.02)
    ser.write(clear_line2)
    ser.flush()
    time.sleep(0.5)

    # ========================================================================
    # FAZA 1: START - OBA TORY BIEGNĄ
    # ========================================================================
    print("\n" + "=" * 70)
    print("FAZA 1: START - czas biegnie na OBUDWÓCH liniach jednocześnie")
    print("=" * 70)

    start_time = time.time()
    phase1_duration = 5  # 5 sekund

    print("⏱️  Obie linie pokazują ten sam bieżący czas...")

    while time.time() - start_time < phase1_duration:
        elapsed = time.time() - start_time
        time_str = f"00:{int(elapsed):02d}.{int((elapsed % 1) * 100):02d}"

        # Wyślij NA OBE LINIE - ten sam czas
        packet1 = create_time_packet_line1(time_str)
        ser.write(packet1)
        ser.flush()
        time.sleep(0.02)

        packet2 = create_time_packet_line2(time_str)
        ser.write(packet2)
        ser.flush()

        if int(elapsed * 2) % 2 == 0:  # Log co ~sekudę
            print(f"  📺 LINIA 1: {time_str}  |  LINIA 2: {time_str}")

        time.sleep(0.05)

    print(f"\n✅ FAZA 1 ZAKOŃCZONA - obie linie pokazują: {time_str}")
    time.sleep(1)

    # ========================================================================
    # FAZA 2: TOR 1 KOŃCZY - LINIA 1 ZATRZYMUJE SIĘ
    # ========================================================================
    print("\n" + "=" * 70)
    print("FAZA 2: TOR 1 KOŃCZY - LINIA 1 zatrzymuje się, LINIA 2 biegnie dalej")
    print("=" * 70)

    tor1_result = elapsed
    tor1_result_str = f"00:{int(tor1_result):02d}.{int((tor1_result % 1) * 100):02d}"

    print(f"🏁 TOR 1 (LINIA 1) META: {tor1_result_str}")
    print(f"   Wyświetlam: 'TOR 1    {tor1_result_str}'")

    # LINIA 1 - zatrzymana z nazwą toru
    packet1_final = create_time_packet_line1(tor1_result_str, lane_name="TOR 1")
    ser.write(packet1_final)
    ser.flush()
    time.sleep(0.1)

    # LINIA 2 - kontynuuje bieżący czas
    print("\n⏱️  TOR 2 (LINIA 2) biegnie dalej...")
    phase2_start = time.time()
    phase2_duration = 3  # 3 sekundy więcej

    while time.time() - phase2_start < phase2_duration:
        elapsed2 = tor1_result + (time.time() - phase2_start)
        time_str2 = f"00:{int(elapsed2):02d}.{int((elapsed2 % 1) * 100):02d}"

        # Tylko LINIA 2 - TOR 1 już skończył
        packet2 = create_time_packet_line2(time_str2)
        ser.write(packet2)
        ser.flush()

        # LINIA 1 - kontynuuj wysyłanie wyniku finałowego (symulacja update_live_timer)
        ser.write(packet1_final)
        ser.flush()

        if int((time.time() - phase2_start) * 2) % 2 == 0:
            print(f"  📺 LINIA 1: TOR 1    {tor1_result_str}  |  LINIA 2: {time_str2}")

        time.sleep(0.05)

    print(f"\n✅ FAZA 2 ZAKOŃCZONA")
    print(f"   LINIA 1: TOR 1    {tor1_result_str} (ZATRZYMANA)")
    print(f"   LINIA 2: {time_str2} (BIEGNIE)")
    time.sleep(1)

    # ========================================================================
    # FAZA 3: TOR 2 KOŃCZY - LINIA 2 ZATRZYMUJE SIĘ
    # ========================================================================
    print("\n" + "=" * 70)
    print("FAZA 3: TOR 2 KOŃCZY - LINIA 2 zatrzymuje się")
    print("=" * 70)

    tor2_result = elapsed2
    tor2_result_str = f"00:{int(tor2_result):02d}.{int((tor2_result % 1) * 100):02d}"

    print(f"🏁 TOR 2 (LINIA 2) META: {tor2_result_str}")
    print(f"   Wyświetlam: 'TOR 2    {tor2_result_str}'")

    # LINIA 2 - zatrzymana z nazwą toru
    packet2_final = create_time_packet_line2(tor2_result_str, lane_name="TOR 2")
    ser.write(packet2_final)
    ser.flush()
    time.sleep(2)

    # ========================================================================
    # PODSUMOWANIE
    # ========================================================================
    print("\n" + "=" * 70)
    print("🏁 PODSUMOWANIE - OBA TORY UKOŃCZONE")
    print("=" * 70)
    print(f"✅ LINIA 1 (TOR 1): TOR 1    {tor1_result_str}")
    print(f"✅ LINIA 2 (TOR 2): TOR 2    {tor2_result_str}")
    print()
    print("WERYFIKACJA:")
    print("✓ Obie linie pokazywały TEN SAM czas podczas biegu")
    print("✓ TOR 1 zatrzymał się NIEZALEŻNIE (linia 1)")
    print("✓ TOR 2 biegł DALEJ po zakończeniu toru 1 (linia 2)")
    print("✓ TOR 2 zatrzymał się NIEZALEŻNIE (linia 2)")
    print("✓ Każdy tor ma swoją DEDYKOWANĄ linię")
    print()

    # Czyszczenie po teście
    time.sleep(3)
    print("🧹 Czyszczenie ekranu po teście...")
    ser.write(clear_line1)
    ser.flush()
    time.sleep(0.02)
    ser.write(clear_line2)
    ser.flush()

    ser.close()
    print("\n✅ Test zakończony pomyślnie!")


if __name__ == "__main__":
    main()
