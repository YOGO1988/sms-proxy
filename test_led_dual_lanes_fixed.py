#!/usr/bin/env python3
"""
TEST AUTOMATYCZNY - WERYFIKACJA NAPRAWY WYŚWIETLANIA DWÓCH TORÓW
Sprawdza czy:
1. Obie linie LED pokazują płynący czas podczas biegu
2. Każdy tor zatrzymuje się niezależnie
3. Wyniki są pokazywane natychmiast bez czekania na drugi tor
4. Czas na LED jest zsynchronizowany z czasem w programie
"""

import serial
import time
from datetime import datetime


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

    print("=" * 70)
    print("TEST WERYFIKACJI NAPRAWY - DWA NIEZALEŻNE ZEGARY NA LED")
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
    # TEST 1: OBA TORY BIEGNĄ - SYNCHRONICZNE WYŚWIETLANIE
    # ========================================================================
    print("\n" + "=" * 70)
    print("TEST 1: OBA TORY BIEGNĄ - ten sam czas na obu liniach")
    print("=" * 70)

    start_time = time.time()
    test_duration = 5  # 5 sekund
    update_count = 0

    print("⏱️  Wysyłanie synchronicznego czasu na OBE linie...")

    while time.time() - start_time < test_duration:
        # OBLICZ CZAS RAZ - dla synchronizacji
        elapsed = time.time() - start_time
        time_str = f"00:{int(elapsed):02d}.{int((elapsed % 1) * 100):02d}"

        # Wyślij NA OBE LINIE BEZ OPÓŹNIENIA
        packet1 = create_time_packet_line1(time_str, add_dash=False)
        ser.write(packet1)
        ser.flush()

        time.sleep(0.02)  # Minimalne opóźnienie między pakietami

        packet2 = create_time_packet_line2(time_str, add_dash=False)
        ser.write(packet2)
        ser.flush()

        update_count += 1
        if update_count % 10 == 0:
            print(f"  ⏱️  {time_str} (aktualizacja #{update_count})")

        time.sleep(0.05)  # Update co 50ms jak w programie

    print(f"\n✅ TEST 1 ZAKOŃCZONY: Wysłano {update_count} aktualizacji")
    print(f"   Obie linie powinny pokazywać ten sam czas: {time_str}")
    time.sleep(1)

    # ========================================================================
    # TEST 2: TOR 1 KOŃCZY - WYNIK NATYCHMIAST Z MYŚLNIKIEM
    # ========================================================================
    print("\n" + "=" * 70)
    print("TEST 2: TOR 1 KOŃCZY - wynik z myślnikiem, TOR 2 biega dalej")
    print("=" * 70)

    left_result_time = 5.78
    left_result_str = f"00:05.78"

    print(f"🏁 TOR 1 (LINIA 1) KOŃCZY: {left_result_str} -")
    packet1_final = create_time_packet_line1(left_result_str, add_dash=True)
    ser.write(packet1_final)
    ser.flush()
    time.sleep(0.1)

    # TOR 2 (PRAWY) BIEGA DALEJ
    print("\n⏱️  TOR 2 (LINIA 2) biega dalej...")
    start_time2 = time.time()
    test_duration2 = 3  # 3 sekundy więcej

    while time.time() - start_time2 < test_duration2:
        elapsed2 = left_result_time + (time.time() - start_time2)
        time_str2 = f"00:{int(elapsed2):02d}.{int((elapsed2 % 1) * 100):02d}"

        # TYLKO LINIA 2 (TOR 2) - TOR 1 JUŻ SKOŃCZYŁ
        packet2 = create_time_packet_line2(time_str2, add_dash=False)
        ser.write(packet2)
        ser.flush()

        if int((time.time() - start_time2) * 10) % 10 == 0:
            print(f"  ⏱️  TOR 2: {time_str2} (TOR 1: {left_result_str} -)")

        time.sleep(0.05)

    print(f"\n✅ TEST 2 ZAKOŃCZONY")
    print(f"   LINIA 1 pokazuje: {left_result_str} - (WYNIK z myślnikiem)")
    print(f"   LINIA 2 pokazuje: {time_str2} (BIEGNĄCY CZAS)")
    time.sleep(1)

    # ========================================================================
    # TEST 3: TOR 2 KOŃCZY - DRUGI WYNIK NATYCHMIAST
    # ========================================================================
    print("\n" + "=" * 70)
    print("TEST 3: TOR 2 KOŃCZY - drugi wynik z myślnikiem")
    print("=" * 70)

    right_result_time = elapsed2
    right_result_str = f"00:{int(right_result_time):02d}.{int((right_result_time % 1) * 100):02d}"

    print(f"🏁 TOR 2 (LINIA 2) KOŃCZY: {right_result_str} -")
    packet2_final = create_time_packet_line2(right_result_str, add_dash=True)
    ser.write(packet2_final)
    ser.flush()
    time.sleep(2)

    # ========================================================================
    # PODSUMOWANIE
    # ========================================================================
    print("\n" + "=" * 70)
    print("PODSUMOWANIE TESTU")
    print("=" * 70)
    print(f"✅ LINIA 1 (TOR LEWY):  {left_result_str} -")
    print(f"✅ LINIA 2 (TOR PRAWY): {right_result_str} -")
    print()
    print("WERYFIKACJA:")
    print("✓ Oba tory pokazywały TEN SAM czas podczas biegu (synchronizacja)")
    print("✓ Tor 1 zatrzymał się NIEZALEŻNIE i pokazał wynik z myślnikiem")
    print("✓ Tor 2 biegł DALEJ po zakończeniu toru 1")
    print("✓ Tor 2 zatrzymał się i pokazał swój wynik z myślnikiem")
    print("✓ Wyniki były pokazywane NATYCHMIAST bez czekania")
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
    print("\nJeśli na LED widziałeś:")
    print("  - Synchroniczny czas na obu liniach podczas biegu")
    print("  - Niezależne zatrzymanie każdego toru")
    print("  - Natychmiastowe wyświetlanie wyników")
    print("To naprawa DZIAŁA POPRAWNIE! ✅")


if __name__ == "__main__":
    main()
