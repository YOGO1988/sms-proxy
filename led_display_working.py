#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LED Display Driver - WORKING VERSION
Based on verified packets from working chronometer program

This module uses TEMPLATE PACKETS with correct checksums
and only replaces the TEXT portion to display new content.
"""

import serial
import time
import threading


class LEDDisplay:
    """
    Driver for Color-LED display board
    Uses working packet templates with correct checksums
    """

    # TEMPLATE PACKETS - These have CORRECT CHECKSUMS from working program
    # We will ONLY replace text, NOT touch checksums!
    TEMPLATES = {
        # Display time on line 1 with TOR label (62 bytes)
        'time_tor1': bytes.fromhex('1B 07 3E 00 A1 2A 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 37 38 37 20 54 4F 52 20 31 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),

        # Display time on line 2 with TOR label (62 bytes)
        'time_tor2': bytes.fromhex('1B 07 3E 00 8F 5C 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 30 30 27 31 30 22 2E 33 36 32 20 54 4F 52 20 32 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),

        # Display name/text on line 1 (82 bytes)
        'text_line1': bytes.fromhex('1B 07 52 00 AA C2 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 54 79 6D 6F 6E 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 2D 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),
    }

    # Text positions in templates (where ASCII text starts)
    TEXT_POSITIONS = {
        'time_tor1': 22,   # Position where "00'07".787 TOR 1" starts
        'time_tor2': 22,   # Position where "00'10".362 TOR 2" starts
        'text_line1': 22,  # Position where "Tymon" starts
    }

    # Text lengths (how many bytes can be replaced)
    TEXT_LENGTHS = {
        'time_tor1': 38,   # Length of time display text with TOR
        'time_tor2': 38,   # Length of time display text with TOR
        'text_line1': 58,  # Length of name/event text
    }

    def __init__(self, port='COM5', baudrate=9600):
        """
        Initialize LED display driver

        Args:
            port: COM port (default: COM5)
            baudrate: Always 9600 for this display
        """
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.connected = False

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
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """Disconnect from display"""
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.connected = False

    def _send_packet(self, packet):
        """Send packet to display"""
        if not self.connected or not self.ser:
            return False

        try:
            self.ser.write(packet)
            self.ser.flush()
            time.sleep(0.2)
            return True
        except:
            return False

    def _format_time(self, seconds):
        """
        Convert seconds to display format: MM'SS".mmm

        Args:
            seconds: Time in seconds (float)

        Returns:
            str: Formatted time string
        """
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        return f"{minutes:02d}'{secs:02d}\".{millis:03d}"

    def _parse_time(self, time_input):
        """
        Parse time from various formats to seconds

        Supports:
        - Float seconds: 7.5
        - MM:SS.mmm: 01:52.310
        - MM:SS: 01:52

        Args:
            time_input: Time in various formats

        Returns:
            float: Time in seconds
        """
        time_str = str(time_input).strip()

        # Try as float/int
        try:
            return float(time_str)
        except:
            pass

        # Parse MM:SS.mmm or MM:SS
        if ':' in time_str:
            parts = time_str.split(':')
            if len(parts) == 2:
                minutes = int(parts[0])
                seconds = float(parts[1])
                return minutes * 60 + seconds

        return 0.0

    def _build_packet_from_template(self, template_name, text):
        """
        Build packet from template by replacing text only
        DOES NOT touch checksum - uses working checksum from template!

        Args:
            template_name: Name of template to use
            text: Text to insert (will be padded/truncated to fit)

        Returns:
            bytes: Complete packet ready to send
        """
        template = bytearray(self.TEMPLATES[template_name])
        start_pos = self.TEXT_POSITIONS[template_name]
        max_len = self.TEXT_LENGTHS[template_name]

        # Pad or truncate text to exact length
        text_padded = text.ljust(max_len)[:max_len]
        text_bytes = text_padded.encode('ascii', errors='replace')

        # Replace text in packet (keeping checksum intact!)
        for i, byte in enumerate(text_bytes):
            if start_pos + i < len(template) - 2:  # Don't touch 0D 0A at end
                template[start_pos + i] = byte

        return bytes(template)

    def show_time(self, time_input, lane=1):
        """
        Display time on specified lane

        Args:
            time_input: Time in seconds (float) or string format "MM:SS.mmm"
            lane: Lane number (1 or 2)

        Returns:
            bool: True if successful
        """
        if not self.connected:
            return False

        # Parse and format time
        seconds = self._parse_time(time_input)
        time_str = self._format_time(seconds)

        # Build display text with TOR label
        display_text = f"{time_str} TOR {lane}"

        # Select template based on lane
        template_name = 'time_tor1' if lane == 1 else 'time_tor2'

        # Build and send packet
        packet = self._build_packet_from_template(template_name, display_text)
        return self._send_packet(packet)

    def show_text(self, text):
        """
        Display custom text on line 1

        Args:
            text: Text to display (will be truncated if too long)

        Returns:
            bool: True if successful
        """
        if not self.connected:
            return False

        packet = self._build_packet_from_template('text_line1', text)
        return self._send_packet(packet)

    def clear(self):
        """
        Clear display (turn off)
        Note: We don't have a verified clear packet yet,
        so we just send empty text
        """
        return self.show_text("")


class LEDDisplayManager:
    """
    High-level manager for race timing integration
    Handles multiple competitors with automatic rotation
    """

    def __init__(self, port='COM5', baudrate=9600):
        """
        Initialize display manager

        Args:
            port: COM port
            baudrate: Baud rate (always 9600)
        """
        self.display = LEDDisplay(port, baudrate)
        self.rotation_thread = None
        self.rotation_active = False
        self.current_results = []

    def initialize(self):
        """
        Connect to display

        Returns:
            bool: True if successful
        """
        return self.display.connect()

    def shutdown(self):
        """Stop rotation and disconnect"""
        self.stop_rotation()
        self.display.disconnect()

    def clear_display(self):
        """Clear display"""
        return self.display.clear()

    def show_event_name(self, event_name, duration=5.0):
        """
        Show event name for specified duration

        Args:
            event_name: Name to display
            duration: How long to show (seconds)
        """
        self.display.show_text(event_name)
        time.sleep(duration)

    def stop_rotation(self):
        """Stop rotation if active"""
        self.rotation_active = False
        if self.rotation_thread and self.rotation_thread.is_alive():
            self.rotation_thread.join()

    def _rotation_worker(self, results):
        """Worker thread for rotating display"""
        while self.rotation_active:
            # Show pairs: 1-2, then 3-4, then 5-6, etc.
            for i in range(0, len(results), 2):
                if not self.rotation_active:
                    break

                # Show first result on line 1
                if i < len(results):
                    result = results[i]
                    self.display.show_time(result['time'], lane=result['lane'])

                # Show second result on line 2 (if exists)
                if i + 1 < len(results):
                    result = results[i + 1]
                    time.sleep(0.3)  # Small delay between lines
                    self.display.show_time(result['time'], lane=result['lane'])

                # Wait before showing next pair
                time.sleep(3.0)

    def update_race_results(self, race_data):
        """
        Update display with race results

        Automatically handles:
        - 1 competitor: single line
        - 2 competitors: two lines
        - 3+ competitors: rotation every 3 seconds

        Args:
            race_data: Dict with keys 'race_number', 'lanes', 'results'
                      results is list of {'lane': int, 'time': str}
        """
        self.stop_rotation()

        results = race_data.get('results', [])

        if len(results) == 0:
            self.clear_display()

        elif len(results) == 1:
            # Single competitor - show on line 1
            result = results[0]
            self.display.show_time(result['time'], lane=result['lane'])

        elif len(results) == 2:
            # Two competitors - show both
            self.display.show_time(results[0]['time'], lane=results[0]['lane'])
            time.sleep(0.3)
            self.display.show_time(results[1]['time'], lane=results[1]['lane'])

        else:
            # 3+ competitors - start rotation
            self.rotation_active = True
            self.rotation_thread = threading.Thread(
                target=self._rotation_worker,
                args=(results,)
            )
            self.rotation_thread.start()


def main():
    """Simple test"""
    print("="*70)
    print("LED Display - Working Version")
    print("="*70)

    port = input("\nPort (Enter = COM5): ").strip() or "COM5"

    led = LEDDisplayManager(port, 9600)

    if not led.initialize():
        print("Failed to connect!")
        return

    print("✅ Connected!")
    print("\nCommands:")
    print("  time:7.5      - Show time 7.5s on lane 1")
    print("  time:1:22.52  - Show time 1:22.52")
    print("  text:Hello    - Show text")
    print("  clear         - Clear display")
    print("  test          - Test sequence")
    print("  quit          - Exit")

    try:
        while True:
            cmd = input("\n> ").strip()

            if not cmd or cmd == 'quit':
                break

            elif cmd == 'test':
                print("Test 1: Time 7.5s lane 1")
                led.display.show_time(7.5, lane=1)
                time.sleep(2)

                print("Test 2: Time 10.5s lane 2")
                led.display.show_time(10.5, lane=2)
                time.sleep(2)

                print("Test 3: Event name")
                led.show_event_name("MISTRZOSTWA 2025", duration=3)

            elif cmd == 'clear':
                led.clear_display()
                print("✅ Cleared")

            elif cmd.startswith('text:'):
                text = cmd[5:]
                led.display.show_text(text)
                print(f"✅ Sent: {text}")

            elif cmd.startswith('time:'):
                time_str = cmd[5:]
                led.display.show_time(time_str, lane=1)
                print(f"✅ Sent: {time_str}")

            else:
                print("❌ Unknown command")

    except KeyboardInterrupt:
        print("\n\nInterrupted")
    finally:
        led.shutdown()


if __name__ == "__main__":
    main()
