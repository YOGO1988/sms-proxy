#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LED Display Driver - FINAL WORKING VERSION
Uses VERIFIED packets from working chronometer program
For race timing integration
"""

import serial
import time
import threading


class LEDDisplay:
    """
    Driver for Color-LED display
    Uses ONLY working packets - NO modifications!
    """

    # WORKING PACKETS - DO NOT MODIFY!
    PACKETS = {
        'name_tymon': bytes.fromhex('1B 07 52 00 AA C2 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 54 79 6D 6F 6E 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 2D 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),

        'lane1': bytes.fromhex('1B 08 E8 00 E8 71 00 00 01 00 00 00 00 00 00 00 01 00 0A 00 00 00 00 00 00 00 00 00 5B 00 54 4F 52 20 31 20 20 20 30 29 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 0D 0A'.replace(' ', '')),

        'lane2': bytes.fromhex('1B 08 E8 00 F8 77 00 00 01 00 00 00 00 00 00 00 02 00 0A 00 00 00 10 00 00 00 00 00 38 00 54 4F 52 20 32 20 20 20 30 29 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 0D 0A'.replace(' ', '')),

        'time_7sec': bytes.fromhex('1B 07 3A 00 51 8B 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 34 36 37 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),

        'time_7sec_tor1': bytes.fromhex('1B 07 3E 00 A1 2A 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 37 38 37 20 54 4F 52 20 31 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),

        'time_10sec_tor2': bytes.fromhex('1B 07 3E 00 8F 5C 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 30 30 27 31 30 22 2E 33 36 32 20 54 4F 52 20 32 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),
    }

    def __init__(self, port='COM5', baudrate=9600):
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
        """Disconnect"""
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.connected = False

    def send_packet(self, packet_name):
        """Send raw packet by name"""
        if not self.connected:
            return False

        packet = self.PACKETS.get(packet_name)
        if not packet:
            return False

        try:
            self.ser.write(packet)
            self.ser.flush()
            time.sleep(0.3)
            return True
        except:
            return False

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

    def test_all(self):
        """Test all packets"""
        print("\n🧪 TEST ALL PACKETS")
        print("="*60)

        tests = [
            ('name_tymon', "Event name: Tymon"),
            ('time_7sec', "Time 7.467s (no TOR)"),
            ('time_7sec_tor1', "Time 7.787s TOR 1"),
            ('time_10sec_tor2', "Time 10.362s TOR 2"),
            ('lane1', "Lane info TOR 1"),
            ('lane2', "Lane info TOR 2"),
        ]

        for packet_name, desc in tests:
            print(f"📤 {desc}")
            self.send_packet(packet_name)
            time.sleep(2.0)

        print("\n✅ Test complete")


class LEDDisplayManager:
    """
    High-level manager for race timing
    Uses predefined packets - shows example times
    """

    def __init__(self, port='COM5', baudrate=9600):
        self.display = LEDDisplay(port, baudrate)
        self.rotation_thread = None
        self.rotation_active = False

    def initialize(self):
        """Connect to display"""
        return self.display.connect()

    def shutdown(self):
        """Disconnect"""
        self.stop_rotation()
        self.display.disconnect()

    def clear_display(self):
        """Clear display - shows event name as 'clear' signal"""
        return self.display.show_event_name()

    def show_event_name(self, event_name, duration=5.0):
        """Show event name"""
        self.display.show_event_name()
        time.sleep(duration)

    def stop_rotation(self):
        """Stop rotation thread"""
        self.rotation_active = False
        if self.rotation_thread and self.rotation_thread.is_alive():
            self.rotation_thread.join()

    def _rotation_worker(self):
        """Rotate between two results"""
        while self.rotation_active:
            # Show TOR 1
            self.display.show_time_7sec_tor1()
            time.sleep(3.0)

            if not self.rotation_active:
                break

            # Show TOR 2
            self.display.show_time_10sec_tor2()
            time.sleep(3.0)

    def update_race_results(self, race_data):
        """
        Update display with race results

        NOTE: This version uses EXAMPLE packets!
        Always shows ~7s for TOR 1 and ~10s for TOR 2

        To show real times, you need to:
        1. Record more packets from working program with different times
        2. OR calculate correct checksum algorithm

        Args:
            race_data: Dict with 'results' list
        """
        self.stop_rotation()

        results = race_data.get('results', [])

        if len(results) == 0:
            self.clear_display()

        elif len(results) == 1:
            # Single competitor - show on line 1
            self.display.show_time_7sec_tor1()

        elif len(results) == 2:
            # Two competitors
            self.display.show_time_7sec_tor1()
            time.sleep(0.3)
            self.display.show_time_10sec_tor2()

        else:
            # 3+ competitors - rotation
            self.rotation_active = True
            self.rotation_thread = threading.Thread(target=self._rotation_worker)
            self.rotation_thread.start()


def main():
    """Interactive test"""
    print("="*70)
    print("LED DISPLAY - FINAL WORKING VERSION")
    print("="*70)
    print("\nUses VERIFIED packets from working program")
    print("Shows EXAMPLE times (~7s, ~10s)")

    port = input("\nPort (Enter = COM5): ").strip() or "COM5"

    led = LEDDisplay(port, 9600)

    if not led.connect():
        print("❌ Failed to connect")
        return

    print("✅ Connected!")
    print("\nCOMMANDS:")
    print("  test     - Test all packets")
    print("  name     - Show event name")
    print("  tor1     - Show TOR 1 time (~7s)")
    print("  tor2     - Show TOR 2 time (~10s)")
    print("  both     - Show both TORs")
    print("  race     - Simulate race with manager")
    print("  quit     - Exit")

    manager = None

    try:
        while True:
            cmd = input("\n> ").strip().lower()

            if not cmd or cmd == 'quit':
                break

            elif cmd == 'test':
                led.test_all()

            elif cmd == 'name':
                led.show_event_name()
                print("✅ Sent: Event name")

            elif cmd == 'tor1':
                led.show_time_7sec_tor1()
                print("✅ Sent: ~7s TOR 1")

            elif cmd == 'tor2':
                led.show_time_10sec_tor2()
                print("✅ Sent: ~10s TOR 2")

            elif cmd == 'both':
                led.show_time_7sec_tor1()
                time.sleep(0.3)
                led.show_time_10sec_tor2()
                print("✅ Sent: Both TORs")

            elif cmd == 'race':
                if not manager:
                    manager = LEDDisplayManager(port, 9600)
                    manager.display = led  # Reuse connection
                    manager.display.connected = True

                print("\nSimulating race...")
                print("1. Clear display")
                manager.clear_display()
                time.sleep(2)

                print("2. Show results (2 competitors)")
                manager.update_race_results({
                    'race_number': 1,
                    'lanes': 2,
                    'results': [
                        {'lane': 1, 'time': '00:07.787'},
                        {'lane': 2, 'time': '00:10.362'}
                    ]
                })

                print("\n✅ Race simulation done")
                print("   (Shows example times ~7s and ~10s)")

            else:
                print("❌ Unknown command")

    except KeyboardInterrupt:
        print("\n\nInterrupted")
    finally:
        if manager:
            manager.shutdown()
        led.disconnect()


if __name__ == "__main__":
    main()
