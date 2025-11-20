#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test START/STOP dla 2 TORÓW - Symulacja stopera sportowego dwutorowego
TOR 1 i TOR 2 niezależnie: START → czas płynie → META → czas się zatrzymuje
"""

import serial
import time
import threading
import sys

# Pakiet inicjalizacyjny
INIT_PACKET = bytes.fromhex('1B 09 0A 00 A4 EB 00 00 0D 0A'.replace(' ', ''))

# Pakiet czyszczący linię 1 (TOR 1)
EMPTY_LINE1 = bytes.fromhex('1B 07 3A 00 BD CA 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))

# Pakiet czyszczący linię 2 (TOR 2) - UWAGA: bajty [18-19] = 10 00!
EMPTY_LINE2 = bytes.fromhex('1B 07 3A 00 60 FC 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))

# Bazowy pakiet czasowy (TOR 1) - bajty [18-19] = 00 00
BASE_PACKET_TOR1 = bytes.fromhex('1B 07 3A 00 51 E1 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 31 22 2E 37 35 38 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))

# Bazowy pakiet czasowy (TOR 2) - bajty [18-19] = 10 00
BASE_PACKET_TOR2 = bytes.fromhex('1B 07 3A 00 A7 1C 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 30 30 27 30 31 22 2E 39 38 32 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))

# Bazowy pakiet META (TOR 1) - rozmiar 0x3E (62 bajty), zawiera "TOR 1"
BASE_META_TOR1 = bytes.fromhex('1B 07 3E 00 C9 8B 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 36 22 2E 30 33 33 20 54 4F 52 20 31 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))

# Bazowy pakiet META (TOR 2) - rozmiar 0x3E (62 bajty), zawiera "TOR 2"
BASE_META_TOR2 = bytes.fromhex('1B 07 3E 00 AF EA 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 30 30 27 30 38 22 2E 39 36 38 20 54 4F 52 20 32 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))


def calculate_crc16(data: bytes) -> int:
    """
    Oblicz CRC-16 dla pakietu LED (CRC-16-CCITT, poly=0x1021).

    Args:
        data: Dane do obliczenia CRC (z wyzerowanym polem CRC na pozycji [4-5])

    Returns:
        16-bitowy CRC
    """
    crc = 0x0000  # Init value
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc


def format_time_mm_ss_ms(milliseconds: int) -> str:
    """
    Formatuje czas w milisekundach na format MM'SS".mmm

    Args:
        milliseconds: Czas w milisekundach

    Returns:
        Sformatowany string np. "00'05".432"
    """
    total_seconds = milliseconds // 1000
    ms = milliseconds % 1000

    minutes = total_seconds // 60
    seconds = total_seconds % 60

    return f"{minutes:02d}'{seconds:02d}\".{ms:03d}"


def create_time_packet(text: str, lane: int) -> bytes:
    """
    Tworzy pakiet czasowy z podanym tekstem dla wybranego toru.

    Args:
        text: Tekst do wyświetlenia (np. "00'05".432  - ")
        lane: Numer toru (1 lub 2)

    Returns:
        Gotowy pakiet do wysłania
    """
    # Wybierz bazowy pakiet
    base = BASE_PACKET_TOR1 if lane == 1 else BASE_PACKET_TOR2
    packet = bytearray(base)

    # Dopełnij tekstem spacjami do długości 36 (długość tekstu w pakiecie)
    text_padded = text.ljust(36)

    # Zastąp tekst od bajtu 22
    packet[22:22+36] = text_padded.encode('ascii', errors='replace')

    # PRZELICZ CHECKSUM
    # Wyzeruj pole CRC
    packet[4] = 0
    packet[5] = 0

    # Oblicz CRC-16 na całym pakiecie
    crc = calculate_crc16(bytes(packet))

    # Wstaw CRC w formacie little-endian
    packet[4] = crc & 0xFF
    packet[5] = (crc >> 8) & 0xFF

    return bytes(packet)


def create_meta_packet(text: str, lane: int) -> bytes:
    """
    Tworzy pakiet META z podanym tekstem dla wybranego toru.
    Pakiet META jest większy (0x3E = 62 bajty) i zawiera "TOR X".

    Args:
        text: Tekst do wyświetlenia (np. "00'06".033 TOR 1      ")
        lane: Numer toru (1 lub 2)

    Returns:
        Gotowy pakiet do wysłania
    """
    # Wybierz bazowy pakiet META
    base = BASE_META_TOR1 if lane == 1 else BASE_META_TOR2
    packet = bytearray(base)

    # Dopełnij tekstem spacjami do długości 40 (większy pakiet!)
    text_padded = text.ljust(40)

    # Zastąp tekst od bajtu 22
    packet[22:22+40] = text_padded.encode('ascii', errors='replace')

    # PRZELICZ CHECKSUM
    # Wyzeruj pole CRC
    packet[4] = 0
    packet[5] = 0

    # Oblicz CRC-16 na całym pakiecie
    crc = calculate_crc16(bytes(packet))

    # Wstaw CRC w formacie little-endian
    packet[4] = crc & 0xFF
    packet[5] = (crc >> 8) & 0xFF

    return bytes(packet)


def send_init(ser, count=3):
    """Wysyła inicjalizację N razy"""
    for i in range(count):
        ser.write(INIT_PACKET)
        ser.flush()
        time.sleep(0.2)
    time.sleep(0.3)


def clear_lane(ser, lane: int):
    """Czyści wybrany tor (1 lub 2)"""
    packet = EMPTY_LINE1 if lane == 1 else EMPTY_LINE2
    ser.write(packet)
    ser.flush()
    time.sleep(0.1)


class LaneTimer:
    """Klasa do zarządzania licznikiem czasu dla jednego toru"""

    def __init__(self, ser, lane: int, update_interval=0.1):
        self.ser = ser
        self.lane = lane  # 1 lub 2
        self.update_interval = update_interval
        self.running = False
        self.start_time = None
        self.elapsed_ms = 0
        self.thread = None
        self.update_count = 0
        self.lane_name = f"TOR {lane}"

    def start(self):
        """Rozpoczyna liczenie"""
        self.start_time = time.time()
        self.running = True
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()
        print(f"⏱️  {self.lane_name} - START!")

    def stop(self):
        """Zatrzymuje liczenie"""
        self.running = False
        if self.thread:
            self.thread.join()
        return self.elapsed_ms

    def _update_loop(self):
        """Wątek aktualizujący wyświetlacz"""
        while self.running:
            # Oblicz aktualny czas
            self.elapsed_ms = int((time.time() - self.start_time) * 1000)

            # Sformatuj czas
            time_str = format_time_mm_ss_ms(self.elapsed_ms)

            # Wyślij na wyświetlacz
            try:
                # WAŻNE: Wyczyść linię przed aktualizacją
                clear_lane(self.ser, self.lane)

                # Wyślij nowy czas (z "  - " na końcu jak w oryginalnych pakietach)
                packet = create_time_packet(f"{time_str}  - ", self.lane)
                self.ser.write(packet)
                self.ser.flush()

                # Debug: wyświetl czas co 10 aktualizacji
                self.update_count += 1
                if self.update_count % 10 == 0:
                    print(f"   📟 {self.lane_name}: {time_str} (#{self.update_count})")

            except Exception as e:
                print(f"❌ {self.lane_name} - Błąd wysyłania: {e}")
                self.running = False
                break

            # Czekaj przed następną aktualizacją
            time.sleep(self.update_interval)


def main():
    print("="*70)
    print("TEST START/STOP - 2 TORY")
    print("="*70)
    print("\n📋 Scenariusz:")
    print("   1. Inicjalizacja tablicy + czyszczenie obu torów")
    print("   2. Wyświetlenie czasu startowego 00'00\".000 na obu torach")
    print("   3. Naciśnij Enter → START TOR 1 (czas płynie)")
    print("   4. Naciśnij Enter → META TOR 1 + START TOR 2")
    print("   5. Naciśnij Enter → META TOR 2")
    print("\n💡 Funkcje:")
    print("   ✓ Dwutorowy stoper (TOR 1 i TOR 2)")
    print("   ✓ Niezależne timery dla każdego toru")
    print("   ✓ Automatyczne czyszczenie linii przed aktualizacją")
    print("   ✓ Pakiety META z identyfikacją toru")

    port = input("\nPort (Enter = COM5): ").strip() or "COM5"

    try:
        print(f"\nŁączę z {port}...")
        ser = serial.Serial(
            port=port,
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
        print("✅ Połączono!")
        time.sleep(0.3)

        # =======================================================================
        # KROK 1: Inicjalizacja + czyszczenie
        # =======================================================================
        print("\n" + "="*70)
        print("KROK 1: Inicjalizacja tablicy")
        print("="*70)

        print("📤 Wysyłam inicjalizację 3x...")
        send_init(ser, 3)

        print("📤 Czyszczę TOR 1...")
        clear_lane(ser, 1)

        print("📤 Czyszczę TOR 2...")
        clear_lane(ser, 2)

        print("✅ Tablica gotowa!")

        # =======================================================================
        # KROK 2: Wyświetl początkowe czasy
        # =======================================================================
        print("\n" + "="*70)
        print("KROK 2: Wyświetlenie czasów startowych")
        print("="*70)

        print("📤 TOR 1: 00'00\".000")
        packet1 = create_time_packet("00'00\".000  - ", 1)
        ser.write(packet1)
        ser.flush()
        time.sleep(0.2)

        print("📤 TOR 2: 00'00\".000")
        packet2 = create_time_packet("00'00\".000  - ", 2)
        ser.write(packet2)
        ser.flush()
        time.sleep(0.5)

        # =======================================================================
        # KROK 3: START TOR 1
        # =======================================================================
        input("\n🏁 Naciśnij Enter aby wystartować TOR 1... ")

        print("\n" + "="*70)
        print("KROK 3: TOR 1 - CZAS PŁYNIE...")
        print("="*70)

        timer1 = LaneTimer(ser, lane=1, update_interval=0.1)
        timer1.start()

        # =======================================================================
        # KROK 4: META TOR 1 + START TOR 2
        # =======================================================================
        input("\n🏁 Naciśnij Enter aby META TOR 1 i START TOR 2... ")

        print("\n" + "="*70)
        print("KROK 4: META TOR 1 + START TOR 2")
        print("="*70)

        # Zatrzymaj TOR 1
        final_ms_1 = timer1.stop()
        final_time_1 = format_time_mm_ss_ms(final_ms_1)
        print(f"⏱️  TOR 1 META: {final_time_1}")

        # Wyślij META dla TOR 1
        meta_packet_1 = create_meta_packet(f"{final_time_1} TOR 1", 1)
        ser.write(meta_packet_1)
        ser.flush()

        time.sleep(0.5)

        # Start TOR 2
        timer2 = LaneTimer(ser, lane=2, update_interval=0.1)
        timer2.start()

        # =======================================================================
        # KROK 5: META TOR 2
        # =======================================================================
        input("\n🏁 Naciśnij Enter aby META TOR 2... ")

        print("\n" + "="*70)
        print("KROK 5: META TOR 2")
        print("="*70)

        # Zatrzymaj TOR 2
        final_ms_2 = timer2.stop()
        final_time_2 = format_time_mm_ss_ms(final_ms_2)
        print(f"⏱️  TOR 2 META: {final_time_2}")

        # Wyślij META dla TOR 2
        meta_packet_2 = create_meta_packet(f"{final_time_2} TOR 2", 2)
        ser.write(meta_packet_2)
        ser.flush()

        # =======================================================================
        # KONIEC
        # =======================================================================
        print("\n✅ Test zakończony!")
        print("="*70)
        print(f"\n📊 WYNIKI:")
        print(f"   TOR 1: {final_time_1}")
        print(f"   TOR 2: {final_time_2}")
        print("="*70)

        ser.close()

    except KeyboardInterrupt:
        print("\n\n⚠️  Przerwano przez użytkownika (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ BŁĄD: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
    input("\nNaciśnij Enter aby zakończyć...")
