#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COM Port Packet Recorder
Nasłuchuje port COM i zapisuje wszystkie pakiety do pliku
"""

import serial
import time
from datetime import datetime
import sys


class PacketRecorder:
    """Recorder for COM port packets"""

    def __init__(self, port='COM5', baudrate=9600, output_file='packets_log.txt'):
        self.port = port
        self.baudrate = baudrate
        self.output_file = output_file
        self.ser = None
        self.packet_count = 0

    def connect(self):
        """Connect to COM port"""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.1
            )
            print(f"✅ Połączono z {self.port}")
            return True
        except Exception as e:
            print(f"❌ Błąd połączenia: {e}")
            return False

    def record(self):
        """Start recording packets"""
        print("\n" + "="*70)
        print("NAGRYWANIE PAKIETÓW")
        print("="*70)
        print(f"Port: {self.port}")
        print(f"Plik wyjściowy: {self.output_file}")
        print()
        print("🔴 NAGRYWANIE...")
        print("   Uruchom teraz oryginalny program i włącz zegar!")
        print("   Naciśnij Ctrl+C aby zatrzymać nagrywanie")
        print()

        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write(f"COM Port Packet Log - {datetime.now()}\n")
            f.write(f"Port: {self.port}, Baudrate: {self.baudrate}\n")
            f.write("="*70 + "\n\n")

            try:
                buffer = bytearray()
                last_packet_time = time.time()

                while True:
                    # Read available data
                    if self.ser.in_waiting > 0:
                        data = self.ser.read(self.ser.in_waiting)
                        buffer.extend(data)
                        last_packet_time = time.time()

                    # If no data for 0.5s, consider packet complete
                    if len(buffer) > 0 and (time.time() - last_packet_time) > 0.5:
                        self._save_packet(f, buffer)
                        buffer = bytearray()

                    time.sleep(0.01)

            except KeyboardInterrupt:
                print("\n\n⏹️  Zatrzymano nagrywanie")

                # Save remaining buffer
                if len(buffer) > 0:
                    self._save_packet(f, buffer)

                print(f"\n✅ Zapisano {self.packet_count} pakietów do: {self.output_file}")

    def _save_packet(self, file, packet_data):
        """Save packet to file"""
        self.packet_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        # Write to file
        file.write(f"Packet #{self.packet_count} - {timestamp}\n")
        file.write("-"*70 + "\n")

        # HEX format
        hex_str = " ".join(f"{b:02X}" for b in packet_data)
        file.write(f"HEX ({len(packet_data)} bytes):\n")
        file.write(f"  {hex_str}\n")

        # ASCII (gdzie możliwe)
        ascii_str = ""
        for b in packet_data:
            if 32 <= b < 127:
                ascii_str += chr(b)
            else:
                ascii_str += f"[{b:02X}]"
        file.write(f"ASCII:\n")
        file.write(f"  {ascii_str}\n")

        # Try to decode time if it's a time packet
        if b'\x1B\x07' in packet_data:
            # This looks like a time display packet
            try:
                # Time is around position 22-32
                if len(packet_data) > 32:
                    time_bytes = packet_data[22:35]
                    time_str = time_bytes.decode('ascii', errors='ignore').strip()
                    if "'" in time_str and '"' in time_str:
                        file.write(f"TIME DETECTED: {time_str}\n")
            except:
                pass

        file.write("\n")
        file.flush()

        # Print to console
        print(f"📦 Pakiet #{self.packet_count}: {len(packet_data)} bajtów - {timestamp}")

    def disconnect(self):
        """Disconnect"""
        if self.ser and self.ser.is_open:
            self.ser.close()


def main():
    print("╔" + "═"*68 + "╗")
    print("║" + " "*20 + "PACKET RECORDER" + " "*33 + "║")
    print("║" + " "*15 + "Nagrywanie pakietów z portu COM" + " "*23 + "║")
    print("╚" + "═"*68 + "╝")
    print()

    port = input("Port COM (Enter = COM5): ").strip() or "COM5"
    output = input("Plik wyjściowy (Enter = packets_log.txt): ").strip() or "packets_log.txt"

    recorder = PacketRecorder(port, 9600, output)

    if not recorder.connect():
        return

    print()
    print("⚠️  WAŻNE INSTRUKCJE:")
    print()
    print("1. Za chwilę rozpocznie się nagrywanie")
    print("2. Uruchom oryginalny program chronometru")
    print("3. Włącz zegar i pozwól mu odliczać")
    print("4. Poczekaj kilka minut (im więcej pakietów tym lepiej!)")
    print("5. Naciśnij Ctrl+C aby zatrzymać")
    print()

    input("Naciśnij Enter aby rozpocząć nagrywanie...")

    try:
        recorder.record()
    finally:
        recorder.disconnect()

    print()
    print("="*70)
    print("GOTOWE!")
    print("="*70)
    print(f"Plik: {output}")
    print(f"Pakiety: {recorder.packet_count}")
    print()
    print("📧 Teraz możesz:")
    print("   1. Otworzyć plik w Notatniku")
    print("   2. Skopiować zawartość")
    print("   3. Wysłać mi pakiety")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPrzerwano")
    except Exception as e:
        print(f"\n❌ Błąd: {e}")
        import traceback
        traceback.print_exc()
