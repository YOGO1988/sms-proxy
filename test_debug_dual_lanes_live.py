#!/usr/bin/env python3
"""
TEST DEBUGGOWANIA - Symulacja problemu z blokowaniem czasu na linii 2
Cel: Sprawdzić czy czas płynie poprawnie gdy tor 1 kończy a tor 2 biegnący dalej
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


def create_time_packet_line1(time_str: str, lane_name: str = None) -> bytes:
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

    if lane_name:
        suffix = f"  {lane_name}"
    else:
        suffix = "  "

    text_padded = (formatted + suffix).ljust(34)[:34]
    base[22:56] = text_padded.encode('ascii', errors='replace')

    base[4] = 0
    base[5] = 0
    crc = calculate_crc16(bytes(base))
    base[4] = crc & 0xFF
    base[5] = (crc >> 8) & 0xFF

    return bytes(base)


def create_time_packet_line2(time_str: str, lane_name: str = None) -> bytes:
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

    if lane_name:
        suffix = f"  {lane_name}"
    else:
        suffix = "  "

    text_padded = (formatted + suffix).ljust(34)[:34]
    base[22:56] = text_padded.encode('ascii', errors='replace')

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
    print("TEST DEBUGGOWANIA - PROBLEM Z BLOKOWANIEM CZASU")
    print("=" * 70)
    print(f"Port: {PORT}")
    print(f"Baudrate: {BAUDRATE}")
    print()
    print("Ten test sprawdza czy czas płynie poprawnie na linii 2")
    print("gdy tor 1 już zakończył bieg.")
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
        print(f"✅ Połączono z {PORT}")
        time.sleep(0.3)
    except Exception as e:
        print(f"❌ BŁĄD: Nie można połączyć z {PORT}")
        print(f"   Szczegóły: {e}")
        return

    # Wyczyść ekran
    print("\n🧹 Czyszczenie ekranu...")
    clear_line1 = bytes.fromhex('1B 07 54 00 14 75 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 2D 2D 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))
    clear_line2 = bytes.fromhex('1B 07 54 00 60 FC 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 2D 2D 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))
    ser.write(clear_line1)
    ser.flush()
    time.sleep(0.02)
    ser.write(clear_line2)
    ser.flush()
    time.sleep(0.5)

    # FAZA 1: Oba tory biegną (5 sekund)
    print("\n" + "=" * 70)
    print("FAZA 1: OBA TORY BIEGNĄ (5 sekund)")
    print("=" * 70)
    print("Obie linie LED powinny pokazywać TEN SAM płynący czas.")
    print()

    start_time = time.time()
    update_count = 0

    while time.time() - start_time < 5.0:
        elapsed = time.time() - start_time
        time_str = f"00:{int(elapsed):02d}.{int((elapsed % 1) * 100):02d}"

        # Wysyłaj na obie linie
        packet1 = create_time_packet_line1(time_str)
        ser.write(packet1)
        ser.flush()
        time.sleep(0.02)

        packet2 = create_time_packet_line2(time_str)
        ser.write(packet2)
        ser.flush()

        update_count += 1
        if update_count % 20 == 0:
            print(f"  ⏱️  {time_str} (update #{update_count})")

        time.sleep(0.05)  # Co 50ms jak w programie

    print(f"\n✅ FAZA 1 zakończona: wysłano {update_count} aktualizacji")
    print(f"   Obie linie powinny pokazywać: {time_str}")
    time.sleep(1)

    # FAZA 2: TOR 1 KOŃCZY - wynik z nazwą "TOR 1"
    print("\n" + "=" * 70)
    print("FAZA 2: TOR 1 KOŃCZY (linia 1 = wynik, linia 2 = biegnący czas)")
    print("=" * 70)
    print("LINIA 1: pokaże wynik 00'05\".00 TOR 1 (zatrzymany)")
    print("LINIA 2: powinien DALEJ płynąć czas (05.00 → 05.05 → 05.10...)")
    print()

    # Wyślij wynik na linię 1
    result_tor1 = "00:05.00"
    print(f"🏁 TOR 1 zakończył: {result_tor1}")
    packet1_final = create_time_packet_line1(result_tor1, lane_name="TOR 1")
    ser.write(packet1_final)
    ser.flush()
    print(f"   📡 Wysłano packet1 (wynik z nazwą TOR 1)")
    time.sleep(0.1)

    # TOR 2 biegnący dalej (kolejne 5 sekund)
    print("\n⏱️  TOR 2 biegnący dalej (5 sekund)...")
    print("    OBSERWUJ LINIĘ 2 - CZY CZAS PŁYNIE?")
    print()

    phase2_start = time.time()
    update_count2 = 0

    while time.time() - phase2_start < 5.0:
        # Oblicz czas od oryginalnego startu (5s + elapsed)
        total_elapsed = 5.0 + (time.time() - phase2_start)
        time_str_line2 = f"00:{int(total_elapsed):02d}.{int((total_elapsed % 1) * 100):02d}"

        # TYLKO LINIA 2 - linia 1 pokazuje wynik
        packet2 = create_time_packet_line2(time_str_line2)
        ser.write(packet2)
        ser.flush()

        update_count2 += 1
        if update_count2 % 20 == 0:
            print(f"  ⏱️  LINIA 2: {time_str_line2} (update #{update_count2}) | LINIA 1: {result_tor1} TOR 1")

        time.sleep(0.05)  # Co 50ms

    print(f"\n✅ FAZA 2 zakończona: wysłano {update_count2} aktualizacji dla linii 2")
    print(f"   LINIA 1 powinna pokazywać: {result_tor1} TOR 1 (zatrzymany)")
    print(f"   LINIA 2 powinna pokazywać: {time_str_line2} (płynący)")
    time.sleep(1)

    # FAZA 3: TOR 2 kończy
    print("\n" + "=" * 70)
    print("FAZA 3: TOR 2 KOŃCZY - wynik z nazwą TOR 2")
    print("=" * 70)

    result_tor2 = f"00:{int(total_elapsed):02d}.{int((total_elapsed % 1) * 100):02d}"
    print(f"🏁 TOR 2 zakończył: {result_tor2}")
    packet2_final = create_time_packet_line2(result_tor2, lane_name="TOR 2")
    ser.write(packet2_final)
    ser.flush()
    print(f"   📡 Wysłano packet2 (wynik z nazwą TOR 2)")
    time.sleep(2)

    # PODSUMOWANIE
    print("\n" + "=" * 70)
    print("PODSUMOWANIE")
    print("=" * 70)
    print(f"✅ LINIA 1: {result_tor1} TOR 1")
    print(f"✅ LINIA 2: {result_tor2} TOR 2")
    print()
    print("PYTANIA:")
    print("1. Czy w FAZIE 1 obie linie pokazywały TEN SAM płynący czas?")
    print("2. Czy w FAZIE 2 linia 2 PŁYNĘŁA dalej po zakończeniu toru 1?")
    print("   ← TO JEST KLUCZOWE PYTANIE!")
    print("3. Czy w FAZIE 3 obie linie pokazują końcowe wyniki?")
    print()
    print("Jeśli linia 2 w FAZIE 2 SIĘ BLOKOWAŁA (nie płynęła),")
    print("to problem jest albo:")
    print("  a) W LED hardware/firmware (nie przetwarza pakietów)")
    print("  b) W protokole (pakiety są źle sformatowane)")
    print("  c) W opóźnieniach (pakiety kolidują)")
    print()

    # Wyczyść ekran
    time.sleep(3)
    print("🧹 Czyszczenie ekranu...")
    ser.write(clear_line1)
    ser.flush()
    time.sleep(0.02)
    ser.write(clear_line2)
    ser.flush()

    ser.close()
    print("\n✅ Test zakończony!")


if __name__ == "__main__":
    main()
