#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test START/STOP - Symulacja stopera sportowego
Impuls START → czas płynie → Enter (META) → czas się zatrzymuje
"""

import serial
import time
import threading
import sys

# Pakiet inicjalizacyjny
INIT_PACKET = bytes.fromhex('1B 09 0A 00 A4 EB 00 00 0D 0A'.replace(' ', ''))

# Pakiet czyszczący linię 2 (usuwa tekst producenta)
EMPTY_LINE2 = bytes.fromhex('1B 07 54 00 60 FC 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 2D 2D 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))

# Bazowy pakiet czasowy (linia 1)
BASE_PACKET = bytes.fromhex('1B 07 3A 00 51 E1 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 31 22 2E 37 35 38 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))


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


def create_time_packet(text: str) -> bytes:
    """
    Tworzy pakiet czasowy z podanym tekstem.
    Używa bazowego pakietu i zmienia tylko tekst (od bajtu 22),
    następnie przelicza checksum.

    Args:
        text: Tekst do wyświetlenia (np. "00'05".432")

    Returns:
        Gotowy pakiet do wysłania
    """
    packet = bytearray(BASE_PACKET)

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


def send_init(ser, count=3):
    """Wysyła inicjalizację N razy"""
    for i in range(count):
        ser.write(INIT_PACKET)
        ser.flush()
        time.sleep(0.2)
    time.sleep(0.3)


def clear_line2(ser):
    """Czyści linię 2 (usuwa tekst producenta)"""
    ser.write(EMPTY_LINE2)
    ser.flush()
    time.sleep(0.3)


class Timer:
    """Klasa do zarządzania licznikiem czasu"""

    def __init__(self, ser, update_interval=0.2):
        self.ser = ser
        self.update_interval = update_interval  # Co ile sekund aktualizować wyświetlacz
        self.running = False
        self.start_time = None
        self.elapsed_ms = 0
        self.thread = None

    def start(self):
        """Rozpoczyna liczenie"""
        self.start_time = time.time()
        self.running = True
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()
        print("⏱️  Stoper uruchomiony! Wciśnij Enter aby STOP...")

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
                # IMPORTANT: Re-init przed każdym nowym pakietem!
                send_init(self.ser, 1)
                packet = create_time_packet(time_str)
                self.ser.write(packet)
                self.ser.flush()
            except Exception as e:
                print(f"❌ Błąd wysyłania: {e}")
                self.running = False
                break

            # Czekaj przed następną aktualizacją
            time.sleep(self.update_interval)


def main():
    print("="*70)
    print("TEST START/STOP - STOPER SPORTOWY")
    print("="*70)
    print("\n📋 Scenariusz:")
    print("   1. Inicjalizacja tablicy + czyszczenie linii 2")
    print("   2. Naciśnij Enter → START (czas zaczyna płynąć)")
    print("   3. Naciśnij Enter → META/STOP (czas się zatrzymuje)")
    print("   4. Wyświetlenie końcowego wyniku")

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
        # KROK 1: Inicjalizacja + czyszczenie linii 2
        # =======================================================================
        print("\n" + "="*70)
        print("KROK 1: Inicjalizacja tablicy")
        print("="*70)

        print("📤 Wysyłam inicjalizację 3x...")
        send_init(ser, 3)

        print("📤 Czyszczę linię 2 (usuwam tekst producenta)...")
        clear_line2(ser)

        print("✅ Tablica gotowa!")

        # =======================================================================
        # KROK 2: Oczekiwanie na START
        # =======================================================================
        print("\n" + "="*70)
        print("KROK 2: Oczekiwanie na START")
        print("="*70)

        # Wyświetl początkowy czas 00'00".000
        print("📤 Wyświetlam czas startowy: 00'00\".000")
        send_init(ser, 1)
        start_packet = create_time_packet("00'00\".000")
        ser.write(start_packet)
        ser.flush()
        time.sleep(0.3)

        input("\n🏁 Naciśnij Enter aby wystartować... ")

        # =======================================================================
        # KROK 3: START - czas płynie
        # =======================================================================
        print("\n" + "="*70)
        print("KROK 3: CZAS PŁYNIE...")
        print("="*70)

        timer = Timer(ser, update_interval=0.2)  # Aktualizuj co 200ms
        timer.start()

        # Czekaj na Enter (META/STOP)
        input()  # Użytkownik wciska Enter

        # =======================================================================
        # KROK 4: STOP - zatrzymaj czas
        # =======================================================================
        print("\n" + "="*70)
        print("KROK 4: META/STOP!")
        print("="*70)

        final_ms = timer.stop()
        final_time_str = format_time_mm_ss_ms(final_ms)

        print(f"⏱️  Końcowy czas: {final_time_str}")

        # Wyślij końcowy czas na wyświetlacz (z dodatkowym "META")
        print("📤 Wysyłam końcowy wynik...")
        send_init(ser, 1)
        final_packet = create_time_packet(f"{final_time_str} META")
        ser.write(final_packet)
        ser.flush()

        print("\n✅ Test zakończony!")
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
