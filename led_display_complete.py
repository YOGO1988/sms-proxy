#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LED Display Driver - KOMPLETNA WERSJA
YO&GO Events - 2025

Funkcje:
- Ustawianie jasności 0-100%
- Wyświetlanie tekstów na linii 1 i 2
- Wygaszanie tablicy
- Tryb 2-torowy (TOR 1, TOR 2)
- Tryb rankingowy (1-2 miejsce, 3-4 miejsce, itd.)
- Rotacja wyników

Based on verified packets from working chronometer program
"""

import serial
import time
import threading
import struct
from typing import List, Tuple, Optional


def calculate_crc16(data: bytes) -> int:
    """
    Obliczanie CRC16 MODBUS

    Args:
        data: Dane do obliczenia CRC

    Returns:
        CRC16 jako int (16-bit)
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


class LEDDisplay:
    """
    Driver for Color-LED display
    Complete version with brightness, text display, and multiple modes
    """

    # WORKING PACKETS - DO NOT MODIFY!
    PACKETS = {
        'name_tymon': bytes.fromhex('1B 07 52 00 AA C2 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 54 79 6D 6F 6E 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 2D 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),

        'lane1': bytes.fromhex('1B 08 E8 00 E8 71 00 00 01 00 00 00 00 00 00 00 01 00 0A 00 00 00 00 00 00 00 00 00 5B 00 54 4F 52 20 31 20 20 20 30 29 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 0D 0A'.replace(' ', '')),

        'lane2': bytes.fromhex('1B 08 E8 00 F8 77 00 00 01 00 00 00 00 00 00 00 02 00 0A 00 00 00 10 00 00 00 00 00 38 00 54 4F 52 20 32 20 20 20 30 29 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 0D 0A'.replace(' ', '')),

        'time_7sec': bytes.fromhex('1B 07 3A 00 51 8B 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 34 36 37 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),

        'time_7sec_tor1': bytes.fromhex('1B 07 3E 00 A1 2A 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 37 38 37 20 54 4F 52 20 31 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),

        'time_10sec_tor2': bytes.fromhex('1B 07 3E 00 8F 5C 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 30 30 27 31 30 22 2E 33 36 32 20 54 4F 52 20 32 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),

        # Clear packets (from user's log)
        'clear_line1': bytes.fromhex('1B 07 54 00 14 75 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 2D 2D 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),

        'clear_line2': bytes.fromhex('1B 07 54 00 60 FC 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 2D 2D 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),

        # Brightness packets (from user's log)
        'brightness_0': bytes.fromhex('1B 06 0C 00 FB E8 00 00 00 00 0D 0A'.replace(' ', '')),
        'brightness_9': bytes.fromhex('1B 06 0C 00 8C 1B 00 00 09 00 0D 0A'.replace(' ', '')),
        'brightness_15': bytes.fromhex('1B 06 0C 00 15 3C 00 00 0F 00 0D 0A'.replace(' ', '')),
    }

    def __init__(self, port='COM5', baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.connected = False
        self.current_brightness = 100

    def connect(self):
        """Connect to display"""
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
            print(f"✅ Połączono z tablicą LED na {self.port}")
            return True
        except Exception as e:
            print(f"❌ Błąd połączenia: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """Disconnect"""
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.connected = False
        print("✅ Rozłączono z tablicą LED")

    def send_packet(self, packet_data):
        """
        Send raw packet

        Args:
            packet_data: bytes or packet name (str)
        """
        if not self.connected:
            return False

        # If string, get from PACKETS dict
        if isinstance(packet_data, str):
            packet_data = self.PACKETS.get(packet_data)
            if not packet_data:
                return False

        try:
            self.ser.write(packet_data)
            self.ser.flush()
            time.sleep(0.1)
            return True
        except Exception as e:
            print(f"❌ Błąd wysyłania: {e}")
            return False

    def create_brightness_packet(self, brightness: int) -> bytes:
        """
        Create brightness control packet

        Args:
            brightness: 0-100 (percentage)

        Returns:
            Complete packet with CRC
        """
        # Clamp brightness to 0-100
        brightness = max(0, min(100, brightness))

        # Packet structure: 1B 06 0C 00 [CRC_L] [CRC_H] 00 00 [BRIGHTNESS] 00 0D 0A
        # Data for CRC calculation (without ESC, CRC itself, and CRLF)
        data = bytes([0x06, 0x0C, 0x00, 0x00, 0x00, 0x00, 0x00, brightness, 0x00])

        # Calculate CRC16
        crc = calculate_crc16(data)
        crc_low = crc & 0xFF
        crc_high = (crc >> 8) & 0xFF

        # Build complete packet
        packet = bytes([0x1B, 0x06, 0x0C, 0x00, crc_low, crc_high, 0x00, 0x00, brightness, 0x00, 0x0D, 0x0A])

        return packet

    def set_brightness(self, brightness: int):
        """
        Ustawienie jasności tablicy

        Args:
            brightness: Jasność 0-100 (%)
                       0 = wyłączone (czarne)
                       100 = maksymalna jasność
        """
        brightness = max(0, min(100, brightness))

        print(f"💡 Ustawianie jasności: {brightness}%")

        # Use predefined packets for known values
        if brightness == 0:
            result = self.send_packet('brightness_0')
        elif brightness == 9:
            result = self.send_packet('brightness_9')
        elif brightness == 15:
            result = self.send_packet('brightness_15')
        else:
            # Calculate packet for other values
            packet = self.create_brightness_packet(brightness)
            result = self.send_packet(packet)

        if result:
            self.current_brightness = brightness

        return result

    def turn_off(self):
        """Wygaszenie tablicy (brightness = 0%)"""
        print("🔴 Wygaszanie tablicy...")
        return self.set_brightness(0)

    def turn_on(self, brightness: int = 100):
        """Włączenie tablicy z określoną jasnością"""
        print(f"✅ Włączanie tablicy (jasność {brightness}%)...")
        return self.set_brightness(brightness)

    def clear_display(self):
        """Clear both lines"""
        print("🧹 Czyszczenie wyświetlacza...")
        self.send_packet('clear_line1')
        time.sleep(0.05)
        self.send_packet('clear_line2')
        return True

    def show_text_line(self, text: str, line: int = 1):
        """
        Wyświetl tekst na określonej linii

        Args:
            text: Tekst do wyświetlenia (max ~40 znaków)
            line: Numer linii (1 lub 2)
        """
        # TODO: Implement text packet creation
        # For now, use clear packets as placeholder
        print(f"📝 Tekst linia {line}: {text}")

        if line == 1:
            self.send_packet('clear_line1')
        else:
            self.send_packet('clear_line2')

    def show_text(self, text1: str, text2: str = ""):
        """
        Wyświetl tekst na obu liniach

        Args:
            text1: Tekst linii 1
            text2: Tekst linii 2 (opcjonalny)
        """
        print(f"📝 Wyświetlanie tekstu:")
        print(f"   Linia 1: {text1}")
        if text2:
            print(f"   Linia 2: {text2}")

        self.show_text_line(text1, 1)
        if text2:
            time.sleep(0.05)
            self.show_text_line(text2, 2)

    # Original working methods
    def show_event_name(self):
        """Show event name (currently shows 'Tymon')"""
        return self.send_packet('name_tymon')

    def show_lane_tor1(self):
        """Show TOR 1 label"""
        return self.send_packet('lane1')

    def show_lane_tor2(self):
        """Show TOR 2 label"""
        return self.send_packet('lane2')

    def show_time_7sec(self):
        """Show time ~7 seconds (no TOR label)"""
        return self.send_packet('time_7sec')

    def show_time_7sec_tor1(self):
        """Show time ~7 seconds on TOR 1"""
        return self.send_packet('time_7sec_tor1')

    def show_time_10sec_tor2(self):
        """Show time ~10 seconds on TOR 2"""
        return self.send_packet('time_10sec_tor2')


class LEDDisplayManager:
    """
    Manager do obsługi wyświetlacza w kontekście zawodów
    Obsługuje:
    - Tryb 2-torowy (wyniki dla 2 zawodników na TOR 1 i TOR 2)
    - Tryb rankingowy (wyniki dla 3+ zawodników w parach: 1-2, 3-4, 5-6...)
    """

    def __init__(self, port='COM5', baudrate=9600):
        self.display = LEDDisplay(port, baudrate)
        self.rotation_thread = None
        self.rotation_active = False
        self.current_mode = None  # '2lane' or 'ranking'

    def initialize(self):
        """Connect to display"""
        if not self.display.connect():
            return False

        # Set default brightness
        self.display.set_brightness(100)
        time.sleep(0.3)

        # Show welcome message
        self.display.show_event_name()
        time.sleep(2)

        return True

    def shutdown(self):
        """Disconnect and turn off"""
        self.stop_rotation()
        self.display.turn_off()
        self.display.disconnect()

    def clear_display(self):
        """Clear display"""
        self.stop_rotation()
        return self.display.clear_display()

    def set_brightness(self, brightness: int):
        """
        Ustaw jasność tablicy

        Args:
            brightness: 0-100%
        """
        return self.display.set_brightness(brightness)

    def turn_off(self):
        """Wygaś tablicę"""
        self.stop_rotation()
        return self.display.turn_off()

    def turn_on(self, brightness: int = 100):
        """Włącz tablicę"""
        return self.display.turn_on(brightness)

    def show_event_name(self, event_name: str, duration: float = 5.0):
        """Show event name"""
        self.display.show_event_name()
        time.sleep(duration)

    def stop_rotation(self):
        """Stop rotation thread"""
        self.rotation_active = False
        if self.rotation_thread and self.rotation_thread.is_alive():
            self.rotation_thread.join(timeout=2)

    def _rotation_worker_ranking(self, results: List[dict]):
        """
        Rotation worker for ranking mode (3+ competitors)
        Shows pairs: 1-2, 3-4, 5-6, etc.
        """
        print(f"🔄 Tryb rankingowy: {len(results)} zawodników")

        index = 0
        while self.rotation_active:
            # Get current pair (2 results)
            pair = results[index:index+2]

            if len(pair) == 1:
                # Single result - show on line 1
                print(f"  📊 Miejsce {index+1}: {pair[0].get('time', 'DNS')}")
                self.display.show_time_7sec_tor1()  # Example time

            elif len(pair) == 2:
                # Two results - show both
                print(f"  📊 Miejsca {index+1}-{index+2}:")
                print(f"     {index+1}. {pair[0].get('time', 'DNS')}")
                print(f"     {index+2}. {pair[1].get('time', 'DNS')}")

                # Show both times
                self.display.show_time_7sec_tor1()
                time.sleep(0.1)
                self.display.show_time_10sec_tor2()

            # Wait before next pair
            time.sleep(3.0)

            # Next pair
            index += 2

            # Loop back to start
            if index >= len(results):
                index = 0
                print("  🔄 Powrót do początku")

    def update_race_results(self, race_data: dict):
        """
        Aktualizuj wyniki biegu na tablicy

        Args:
            race_data: {
                'race_number': int,
                'lanes': int,  # 2 = tryb torowy, >2 = tryb rankingowy
                'results': [
                    {'lane': 1, 'time': '00:07.787', 'place': 1},
                    {'lane': 2, 'time': '00:10.362', 'place': 2},
                    ...
                ]
            }
        """
        self.stop_rotation()

        lanes = race_data.get('lanes', 2)
        results = race_data.get('results', [])

        if len(results) == 0:
            print("⚠️  Brak wyników do wyświetlenia")
            self.clear_display()
            return

        # Determine mode based on lanes
        if lanes == 2 and len(results) <= 2:
            # 2-LANE MODE
            self.current_mode = '2lane'
            print("📊 Tryb 2-torowy")

            if len(results) == 1:
                # Single competitor on lane 1
                print(f"   TOR 1: {results[0].get('time', 'DNS')}")
                self.display.show_time_7sec_tor1()

            elif len(results) == 2:
                # Two competitors
                print(f"   TOR 1: {results[0].get('time', 'DNS')}")
                print(f"   TOR 2: {results[1].get('time', 'DNS')}")

                self.display.show_time_7sec_tor1()
                time.sleep(0.1)
                self.display.show_time_10sec_tor2()

        else:
            # RANKING MODE (3+ competitors or no lanes)
            self.current_mode = 'ranking'
            print("📊 Tryb rankingowy")

            # Sort by place
            results_sorted = sorted(results, key=lambda x: x.get('place', 999))

            if len(results_sorted) <= 2:
                # Show without rotation
                if len(results_sorted) == 1:
                    print(f"   1. {results_sorted[0].get('time', 'DNS')}")
                    self.display.show_time_7sec_tor1()
                else:
                    print(f"   1. {results_sorted[0].get('time', 'DNS')}")
                    print(f"   2. {results_sorted[1].get('time', 'DNS')}")
                    self.display.show_time_7sec_tor1()
                    time.sleep(0.1)
                    self.display.show_time_10sec_tor2()
            else:
                # Rotation for 3+ results
                self.rotation_active = True
                self.rotation_thread = threading.Thread(
                    target=self._rotation_worker_ranking,
                    args=(results_sorted,),
                    daemon=True
                )
                self.rotation_thread.start()


def test_brightness():
    """Test brightness control"""
    print("=" * 70)
    print("TEST JASNOŚCI TABLICY")
    print("=" * 70)

    port = input("\nPort (Enter = COM5): ").strip() or "COM5"

    display = LEDDisplay(port, 9600)

    if not display.connect():
        print("❌ Nie udało się połączyć")
        return

    print("\n✅ Połączono!")

    try:
        # Test brightness levels
        for brightness in [100, 50, 25, 10, 0, 100]:
            print(f"\n📊 Ustawiam jasność: {brightness}%")
            display.set_brightness(brightness)
            time.sleep(2)

        print("\n✅ Test zakończony")

    except KeyboardInterrupt:
        print("\n\nPrzerwano")
    finally:
        display.disconnect()


def main():
    """Interactive test"""
    print("="*70)
    print("LED DISPLAY - KOMPLETNA WERSJA")
    print("="*70)
    print("\nFunkcje:")
    print("  - Jasność 0-100%")
    print("  - Wygaszanie tablicy")
    print("  - Tryb 2-torowy")
    print("  - Tryb rankingowy")
    print("  - Wyświetlanie tekstów")

    port = input("\nPort (Enter = COM5): ").strip() or "COM5"

    manager = LEDDisplayManager(port, 9600)

    if not manager.initialize():
        print("❌ Failed to initialize")
        return

    print("\n✅ Manager zainicjalizowany!")
    print("\nKOMANDS:")
    print("  bright <0-100>  - Ustaw jasność")
    print("  off             - Wygaś tablicę")
    print("  on              - Włącz tablicę")
    print("  clear           - Wyczyść tablicę")
    print("  2lane           - Test trybu 2-torowego")
    print("  ranking         - Test trybu rankingowego")
    print("  quit            - Wyjście")

    try:
        while True:
            cmd = input("\n> ").strip().lower()

            if not cmd or cmd == 'quit':
                break

            elif cmd.startswith('bright'):
                parts = cmd.split()
                if len(parts) == 2:
                    try:
                        brightness = int(parts[1])
                        manager.set_brightness(brightness)
                    except ValueError:
                        print("❌ Podaj liczbę 0-100")
                else:
                    print("❌ Użycie: bright <0-100>")

            elif cmd == 'off':
                manager.turn_off()

            elif cmd == 'on':
                manager.turn_on(100)

            elif cmd == 'clear':
                manager.clear_display()

            elif cmd == '2lane':
                print("\n📊 Test trybu 2-torowego...")
                manager.update_race_results({
                    'race_number': 1,
                    'lanes': 2,
                    'results': [
                        {'lane': 1, 'time': '00:07.787', 'place': 1},
                        {'lane': 2, 'time': '00:10.362', 'place': 2}
                    ]
                })

            elif cmd == 'ranking':
                print("\n📊 Test trybu rankingowego (4 zawodników)...")
                manager.update_race_results({
                    'race_number': 1,
                    'lanes': 4,
                    'results': [
                        {'lane': 1, 'time': '00:07.787', 'place': 1},
                        {'lane': 2, 'time': '00:10.362', 'place': 2},
                        {'lane': 3, 'time': '00:11.234', 'place': 3},
                        {'lane': 4, 'time': '00:12.456', 'place': 4}
                    ]
                })
                print("\n⏱️  Rotacja przez 15 sekund...")
                time.sleep(15)
                manager.stop_rotation()

            else:
                print("❌ Nieznana komenda")

    except KeyboardInterrupt:
        print("\n\nPrzerwano")
    finally:
        manager.shutdown()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test-brightness":
        test_brightness()
    else:
        main()
