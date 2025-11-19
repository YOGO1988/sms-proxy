#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LED Display Driver - YO&GO Events
Driver dla tablicy LED Color-LED do wyświetlania czasów zawodników
"""

import serial
import time
import struct

class LEDDisplay:
    """
    Driver dla tablicy LED Color-LED
    Obsługuje wyświetlanie czasów, nazw zawodników i informacji o torach
    """

    # DZIAŁAJĄCE PAKIETY Z LOGU (ORYGINALNE - ZWERYFIKOWANE)
    PACKETS = {
        'name_tymon': bytes.fromhex('1B 07 52 00 AA C2 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 54 79 6D 6F 6E 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 2D 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),

        'lane1': bytes.fromhex('1B 08 E8 00 E8 71 00 00 01 00 00 00 00 00 00 00 01 00 0A 00 00 00 00 00 00 00 00 00 5B 00 54 4F 52 20 31 20 20 20 30 29 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 0D 0A'.replace(' ', '')),

        'lane2': bytes.fromhex('1B 08 E8 00 F8 77 00 00 01 00 00 00 00 00 00 00 02 00 0A 00 00 00 10 00 00 00 00 00 38 00 54 4F 52 20 32 20 20 20 30 29 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 0D 0A'.replace(' ', '')),

        'time_7sec': bytes.fromhex('1B 07 3A 00 51 8B 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 34 36 37 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),

        'time_7sec_tor1': bytes.fromhex('1B 07 3E 00 A1 2A 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 37 38 37 20 54 4F 52 20 31 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),

        'time_10sec_tor2': bytes.fromhex('1B 07 3E 00 8F 5C 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 30 30 27 31 30 22 2E 33 36 32 20 54 4F 52 20 32 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),

        # PAKIET CZYSZCZĄCY LINIĘ 2 (długi tekst spacjami)
        'clear_line2': bytes.fromhex('1B 08 E8 00 00 00 00 00 01 00 00 00 00 00 00 00 02 00 0A 00 00 00 10 00 00 00 00 00 00 00 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),
    }

    def __init__(self, port='COM5', baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.connected = False
        self.debug = False  # Ustaw True dla debugowania

    def connect(self):
        """Łączy z tablicą"""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )
            self.connected = True
            time.sleep(0.3)
            print(f"✅ Połączono: {self.port}")
            return True
        except Exception as e:
            print(f"❌ Błąd: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """Rozłącza"""
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.connected = False

    def _calculate_crc16(self, data):
        """
        Oblicza CRC16 dla pakietu LED
        Używa wielomianu 0x8005 (CRC16-IBM/ANSI)
        """
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc

    def _send_raw(self, packet_name):
        """Wysyła surowy pakiet (bez modyfikacji)"""
        if not self.connected:
            return False

        packet = self.PACKETS.get(packet_name)
        if not packet:
            return False

        try:
            if self.debug:
                print(f"📤 Wysyłam: {packet.hex(' ')}")

            self.ser.write(packet)
            self.ser.flush()
            time.sleep(0.3)
            return True
        except Exception as e:
            if self.debug:
                print(f"❌ Błąd wysyłania: {e}")
            return False

    def _parse_time(self, time_input):
        """
        Parsuje czas z różnych formatów:
        - float sekundy: 7.5
        - MM:SS.mmm: 01:52.31
        - MM:SS: 01:52

        Zwraca: float sekund
        """
        time_input = str(time_input).strip()

        # Jeśli to float/int
        try:
            return float(time_input)
        except:
            pass

        # Format MM:SS.mmm lub MM:SS
        if ':' in time_input:
            parts = time_input.split(':')
            if len(parts) == 2:
                minutes = int(parts[0])
                seconds = float(parts[1])
                return minutes * 60 + seconds

        return 0.0

    def _format_time(self, seconds):
        """Konwertuje sekundy na format MM'SS".mmm jako bajty ASCII"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        # Format: "00'07".467" jako string ASCII
        time_str = f"{minutes:02d}'{secs:02d}\".{millis:03d}"
        return time_str

    def _build_time_packet(self, seconds, lane_name=None):
        """
        Buduje pakiet czasu z poprawną checksumą CRC16

        Struktura pakietu:
        [0]    1B - Start byte
        [1]    07 - Command
        [2-3]  Length (little endian)
        [4-5]  CRC16 (little endian) - OBLICZANE!
        [6-21] Header (16 bajtów)
        [22+]  Text data (ASCII)
        [-2:]  0D 0A - End bytes
        """
        # Formatuj czas
        time_str = self._format_time(seconds)

        # Wybierz bazowy pakiet
        if lane_name:
            if "1" in str(lane_name):
                base = bytearray(self.PACKETS['time_7sec_tor1'])
                text = f"{time_str} {lane_name}".ljust(38)
            else:
                base = bytearray(self.PACKETS['time_10sec_tor2'])
                text = f"{time_str} {lane_name}".ljust(38)
        else:
            base = bytearray(self.PACKETS['time_7sec'])
            text = f"{time_str}  - ".ljust(34)

        # Zamień tekst (od bajtu 22 do końca -2)
        text_bytes = text.encode('ascii')
        for i, byte in enumerate(text_bytes):
            if 22 + i < len(base) - 2:
                base[22 + i] = byte

        # Oblicz CRC16 dla danych od bajtu 6 do końca (bez 0D 0A)
        data_for_crc = base[6:-2]
        crc = self._calculate_crc16(data_for_crc)

        # Wstaw CRC (little endian)
        base[4] = crc & 0xFF
        base[5] = (crc >> 8) & 0xFF

        # Przelicz długość pakietu (od bajtu 6 do końca bez 0D 0A)
        length = len(base) - 8  # Bez 1B 07 Length(2) CRC(2) i 0D 0A
        base[2] = length & 0xFF
        base[3] = (length >> 8) & 0xFF

        return bytes(base)

    def show_time(self, seconds, lane_name=None, clear_line2=True):
        """
        Wyświetla czas na tablicy

        Args:
            seconds: Czas w sekundach (float) lub format MM:SS.mmm
            lane_name: Nazwa toru (np. "TOR 1") - opcjonalne
            clear_line2: Czy wyczyścić linię 2 po wyświetleniu (domyślnie True)

        Returns:
            bool: True jeśli sukces
        """
        if not self.connected:
            return False

        # Parsuj czas jeśli to string
        if isinstance(seconds, str):
            seconds = self._parse_time(seconds)

        # Buduj pakiet z CRC
        packet = self._build_time_packet(seconds, lane_name)

        try:
            if self.debug:
                print(f"📤 Wysyłam pakiet czasu: {packet.hex(' ')}")

            self.ser.write(packet)
            self.ser.flush()
            time.sleep(0.3)

            # Wyczyść linię 2 jeśli potrzeba
            if clear_line2:
                time.sleep(0.2)
                self._send_raw('clear_line2')

            return True
        except Exception as e:
            if self.debug:
                print(f"❌ Błąd: {e}")
            return False

    def show_name(self, name):
        """
        Wyświetla nazwę zawodnika

        NA RAZIE: Używa hardcoded "Tymon"
        TODO: Implementacja zmiany nazwy z CRC
        """
        if not self.connected:
            return False

        # TYMCZASOWO - zawsze wysyła "Tymon"
        return self._send_raw('name_tymon')

    def show_lane_info(self, lane_number):
        """Wyświetla informację o torze"""
        if not self.connected:
            return False

        if lane_number == 1:
            return self._send_raw('lane1')
        elif lane_number == 2:
            return self._send_raw('lane2')

        return False

    def clear_display(self):
        """Czyści całą tablicę (obie linie)"""
        if not self.connected:
            return False

        # Wyślij pusty czas na linię 1
        self.show_time(0.0, clear_line2=False)
        time.sleep(0.2)
        # Wyczyść linię 2
        self._send_raw('clear_line2')
        return True

    def test_all(self):
        """Testuje wszystkie działające pakiety"""
        print("\n🧪 TEST PAKIETÓW LED")
        print("="*60)

        tests = [
            ('name_tymon', "1. Nazwa: Tymon"),
            ('time_7sec', "2. Czas 7.467s (bez toru)"),
            ('time_7sec_tor1', "3. Czas 7.787s TOR 1"),
            ('time_10sec_tor2', "4. Czas 10.362s TOR 2"),
        ]

        for packet_name, desc in tests:
            print(f"\n📤 {desc}")
            self._send_raw(packet_name)
            time.sleep(2.0)

        print("\n✅ Test zakończony")


def test_interactive():
    """Test interaktywny"""
    print("="*70)
    print("LED DISPLAY DRIVER - YO&GO Events")
    print("Driver dla tablicy LED Color-LED")
    print("="*70)

    port = input("\nPort (Enter = COM5): ").strip() or "COM5"

    led = LEDDisplay(port, 9600)

    if not led.connect():
        return

    print("\n📋 KOMENDY:")
    print("  test         - test 4 pakietów (Tymon, czasy)")
    print("  stopwatch    - dynamiczny stoper")
    print("  time:7.5     - pokaż czas (sekundy)")
    print("  time:1:22.52 - pokaż czas (MM:SS.mmm)")
    print("  lane:1       - info TOR 1")
    print("  lane:2       - info TOR 2")
    print("  name         - pokaż 'Tymon'")
    print("  clear        - wyczyść tablicę")
    print("  debug        - włącz/wyłącz debug")
    print("  quit         - wyjście")

    try:
        while True:
            cmd = input("\n> ").strip()

            if not cmd or cmd == 'quit':
                break

            elif cmd == 'test':
                led.test_all()

            elif cmd == 'debug':
                led.debug = not led.debug
                print(f"🔧 Debug: {'ON' if led.debug else 'OFF'}")

            elif cmd == 'clear':
                led.clear_display()
                print("✅ Wyczyszczono tablicę")

            elif cmd == 'stopwatch':
                print("\n⏱️  STOPER - aktualizuje co 1.0 sek")
                print("   Ctrl+C aby przerwać\n")

                start_time = time.time()
                try:
                    while True:
                        elapsed = time.time() - start_time
                        led.show_time(elapsed, clear_line2=True)
                        print(f"\r⏱️  {elapsed:.3f}s", end='', flush=True)
                        time.sleep(1.0)
                except KeyboardInterrupt:
                    print("\n\n⏸️  Stoper zatrzymany")

            elif cmd == 'name':
                led.show_name("Tymon")
                print("✅ Wysłano: Tymon")

            elif cmd.startswith('time:'):
                time_str = cmd[5:].strip()
                t = led._parse_time(time_str)
                if t > 0:
                    led.show_time(t, clear_line2=True)
                    print(f"✅ Wysłano: {t}s")
                else:
                    print("❌ Nieprawidłowy format czasu")

            elif cmd.startswith('lane:'):
                try:
                    lane = int(cmd[5:])
                    led.show_lane_info(lane)
                    print(f"✅ Wysłano: TOR {lane}")
                except:
                    print("❌ Nieprawidłowy numer toru")

            else:
                print("❌ Nieznana komenda - wpisz 'help' aby zobaczyć listę")

    except KeyboardInterrupt:
        print("\n⏸️  Przerwano")
    finally:
        led.disconnect()
        print("\n👋 Rozłączono")


if __name__ == "__main__":
    test_interactive()
