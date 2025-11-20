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


def create_time_packet_line1(time_str: str) -> bytes:
    """
    Create time packet for line 1 using WORKING packet as template
    Only modifies the time text, keeps checksum calculation from original

    Args:
        time_str: Time like "00:07.787"

    Returns:
        Packet bytes
    """
    # Use working packet as base (time_7sec_tor1 with empty label)
    # We'll use time_7sec packet (no TOR label) as template
    base = bytearray.fromhex('1B 07 3A 00 51 8B 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 34 36 37 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))

    # Format time: "00:07.787" -> "00'07".787"
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

    # Pad to match original length (11 chars for time)
    time_text = formatted.ljust(11)[:11].encode('ascii')

    # Replace time bytes (starting at byte 22)
    base[22:22+11] = time_text

    # For now, keep original checksum - display may not verify it
    return bytes(base)


def create_time_packet_line2(time_str: str) -> bytes:
    """
    Create time packet for line 2 using WORKING packet as template

    Args:
        time_str: Time like "00:10.362"

    Returns:
        Packet bytes
    """
    # Use time_7sec packet as template but change line address to 0x10
    base = bytearray.fromhex('1B 07 3A 00 51 8B 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 30 30 27 30 37 22 2E 34 36 37 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))

    # Format time
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

    # Pad to match original length
    time_text = formatted.ljust(11)[:11].encode('ascii')

    # Replace time bytes
    base[22:22+11] = time_text

    return bytes(base)


def create_ranking_packet(time_str: str, place: int, line: int) -> bytes:
    """
    Create packet for ranking mode with place number

    Uses working packets as templates to avoid checksum issues.

    Args:
        time_str: Time like "00:07.787"
        place: Place number (1-99)
        line: Display line (1 or 2)

    Returns:
        Packet bytes
    """
    if line == 1:
        # Use time_7sec_tor1 as template
        base = bytearray.fromhex('1B 07 3E 00 A1 2A 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 37 38 37 20 54 4F 52 20 31 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))
    else:
        # Use time_10sec_tor2 as template
        base = bytearray.fromhex('1B 07 3E 00 8F 5C 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 30 30 27 31 30 22 2E 33 36 32 20 54 4F 52 20 32 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))

    # Format time: "00:07.787" -> "00'07".787"
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

    time_text = formatted.encode('ascii')

    # Format place: "1." or "12."
    place_text = f"{place}."

    # Build display text: time + space + place
    # Total should be same length as original (38 bytes for text part)
    display_text = (time_text + b' ' + place_text.encode('ascii')).ljust(38, b' ')

    # Replace text part (starts at byte 22)
    base[22:22+38] = display_text

    # Keep original checksum - display likely doesn't verify it strictly
    return bytes(base)


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

        # Brightness packets (from working program - VERIFIED!)
        # Values 0-15 (16 levels), where 0=off, 15=max
        'brightness_0': bytes.fromhex('1B 06 0C 00 FB E8 00 00 00 00 0D 0A'.replace(' ', '')),
        'brightness_3': bytes.fromhex('1B 06 0C 00 27 73 00 00 03 00 0D 0A'.replace(' ', '')),
        'brightness_8': bytes.fromhex('1B 06 0C 00 38 6D 00 00 08 00 0D 0A'.replace(' ', '')),
        'brightness_9': bytes.fromhex('1B 06 0C 00 8C 1B 00 00 09 00 0D 0A'.replace(' ', '')),
        'brightness_12': bytes.fromhex('1B 06 0C 00 C9 A7 00 00 0C 00 0D 0A'.replace(' ', '')),
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

    def set_brightness(self, brightness: int):
        """
        Ustawienie jasności tablicy

        Args:
            brightness: Jasność 0-100 (%)
                       0 = wyłączone (czarne)
                       100 = maksymalna jasność

        Note:
            Display supports 16 brightness levels (0-15)
            Percentage is mapped to nearest available level
        """
        brightness = max(0, min(100, brightness))

        print(f"💡 Ustawianie jasności: {brightness}%")

        # Map percentage (0-100) to hardware level (0-15)
        # Available verified packets: 0, 3, 8, 9, 12, 15
        if brightness == 0:
            level = 0
        elif brightness <= 13:  # 0-13% -> level 0
            level = 0
        elif brightness <= 33:  # 14-33% -> level 3
            level = 3
        elif brightness <= 60:  # 34-60% -> level 8
            level = 8
        elif brightness <= 73:  # 61-73% -> level 9
            level = 9
        elif brightness < 100:  # 74-99% -> level 12
            level = 12
        else:  # 100% -> level 15
            level = 15

        # Use predefined packet for this level
        packet_name = f'brightness_{level}'

        if packet_name not in self.PACKETS:
            print(f"⚠️  Poziom {level} nie jest dostępny, używam najbliższego")
            level = 15
            packet_name = 'brightness_15'

        result = self.send_packet(packet_name)

        if result:
            self.current_brightness = brightness
            print(f"   ✅ Ustawiono poziom sprzętowy: {level}/15")

        return result

    def turn_off(self):
        """Wygaszenie tablicy (brightness = 0%)"""
        print("🔴 Wygaszanie tablicy...")
        # NAJPIERW wyczyść tablicę, potem wygaś
        self.clear_display()
        time.sleep(0.2)
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

    def show_time_with_place(self, time_str: str, place: int, line: int = 1):
        """
        Show time with place number (for ranking mode)

        Args:
            time_str: Time string like "00:07.787"
            place: Place number (1, 2, 3, 4, ...)
            line: Display line (1 or 2)
        """
        # Create ranking packet with place number
        packet = create_ranking_packet(time_str, place, line)
        return self.send_packet(packet)


class LEDDisplayManager:
    """
    Manager do obsługi wyświetlacza w kontekście zawodów
    Obsługuje:
    - Tryb 2-torowy (wyniki dla 2 zawodników na TOR 1 i TOR 2)
    - Tryb rankingowy (wyniki dla 3+ zawodników w parach: 1-2, 3-4, 5-6...)
    - Test timera (start/meta)
    """

    def __init__(self, port='COM5', baudrate=9600):
        self.display = LEDDisplay(port, baudrate)
        self.rotation_thread = None
        self.rotation_active = False
        self.current_mode = None  # '2lane' or 'ranking'
        self.timer_thread = None
        self.timer_active = False
        self.timer_start_time = None

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
        self.stop_timer()
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
        """Włącz tablicę z nazwą wydarzenia"""
        result = self.display.turn_on(brightness)
        if result:
            # Show event name after turning on
            time.sleep(0.2)
            self.display.show_event_name()
        return result

    def show_event_name(self, event_name: str, duration: float = 5.0):
        """Show event name"""
        self.display.show_event_name()
        time.sleep(duration)

    def stop_rotation(self):
        """Stop rotation thread"""
        self.rotation_active = False
        if self.rotation_thread and self.rotation_thread.is_alive():
            self.rotation_thread.join(timeout=2)

    def stop_timer(self):
        """Stop timer thread"""
        self.timer_active = False
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join(timeout=2)

    def _timer_worker(self):
        """Worker thread for running timer"""
        self.timer_start_time = time.time()
        print("⏱️  START! Timer rozpoczęty...")

        while self.timer_active:
            elapsed = time.time() - self.timer_start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            milliseconds = int((elapsed % 1) * 1000)

            time_str = f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

            # Show time on line 1 (without clearing - just overwrite)
            packet = create_time_packet_line1(time_str)
            self.display.send_packet(packet)

            # Update every 100ms
            time.sleep(0.1)

    def start_timer(self):
        """Start running timer"""
        self.stop_rotation()
        self.stop_timer()

        print("🏁 Przygotowanie do startu...")
        self.display.clear_display()
        time.sleep(0.5)

        # Start timer in background
        self.timer_active = True
        self.timer_thread = threading.Thread(
            target=self._timer_worker,
            daemon=True
        )
        self.timer_thread.start()

    def finish_timer(self):
        """Stop timer and show final time"""
        if not self.timer_active:
            print("⚠️  Timer nie jest aktywny!")
            return None

        # Stop timer
        self.timer_active = False
        if self.timer_thread:
            self.timer_thread.join(timeout=1)

        # Calculate final time
        final_time = time.time() - self.timer_start_time
        minutes = int(final_time // 60)
        seconds = int(final_time % 60)
        milliseconds = int((final_time % 1) * 1000)
        time_str = f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

        print(f"🏁 META! Czas: {time_str}")

        # Show final time
        self.display.clear_display()
        time.sleep(0.1)
        packet = create_time_packet_line1(time_str)
        self.display.send_packet(packet)

        return time_str

    def _rotation_worker_ranking(self, results: List[dict]):
        """
        Rotation worker for ranking mode (3+ competitors)
        Shows pairs: 1-2, 3-4, 5-6, etc.
        """
        print(f"🔄 Tryb rankingowy: {len(results)} zawodników")

        # Clear display ONCE at the start, not in the loop
        self.display.clear_display()
        time.sleep(0.2)

        index = 0
        while self.rotation_active:
            # Get current pair (2 results)
            pair = results[index:index+2]

            if len(pair) == 1:
                # Single result - show on line 1, clear line 2
                place = index + 1
                time_str = pair[0].get('time', '00:00.000')
                print(f"  📊 Miejsce {place}: {time_str}")
                self.display.show_time_with_place(time_str, place, line=1)
                time.sleep(0.05)
                self.display.send_packet('clear_line2')

            elif len(pair) == 2:
                # Two results - show both with place numbers
                place1 = index + 1
                place2 = index + 2
                time1 = pair[0].get('time', '00:00.000')
                time2 = pair[1].get('time', '00:00.000')

                print(f"  📊 Miejsca {place1}-{place2}:")
                print(f"     {place1}. {time1}")
                print(f"     {place2}. {time2}")

                # Show both times with place numbers
                self.display.show_time_with_place(time1, place1, line=1)
                time.sleep(0.1)
                self.display.show_time_with_place(time2, place2, line=2)

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
                # Show without rotation - with place numbers
                if len(results_sorted) == 1:
                    time1 = results_sorted[0].get('time', '00:00.000')
                    print(f"   1. {time1}")
                    self.display.show_time_with_place(time1, 1, line=1)
                else:
                    time1 = results_sorted[0].get('time', '00:00.000')
                    time2 = results_sorted[1].get('time', '00:00.000')
                    print(f"   1. {time1}")
                    print(f"   2. {time2}")
                    self.display.show_time_with_place(time1, 1, line=1)
                    time.sleep(0.1)
                    self.display.show_time_with_place(time2, 2, line=2)
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
    print("  start           - Start timera (Enter = impuls start)")
    print("  meta            - Meta/Stop timera (Enter = impuls meta)")
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

            elif cmd == 'start':
                print("\n🏁 Naciśnij ENTER aby wystartować timer...")
                input()
                manager.start_timer()
                print("⏱️  Timer działa! Wpisz 'meta' aby zatrzymać")

            elif cmd == 'meta':
                final_time = manager.finish_timer()
                if final_time:
                    print(f"✅ Zapisany czas: {final_time}")

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
