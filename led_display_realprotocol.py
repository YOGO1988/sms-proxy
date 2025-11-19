#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LED Display Module - NAPRAWIONA WERSJA
Oparty na RZECZYWISTYCH danych HEX z działającego programu

YO&GO Events - 2025
"""

import serial
import serial.tools.list_ports
import time
import threading
from datetime import datetime
from typing import List, Optional, Tuple


class LEDDisplayProtocol:
    """Protokół DOKŁADNIE jak w oryginalnym programie"""

    @staticmethod
    def build_init_command() -> bytes:
        """
        Komenda Set9600 - inicjalizacja
        Oryginalnie: 1B 09 0A 00 A4 EB 00 00 0D 0A
        """
        return bytes([0x1B, 0x09, 0x0A, 0x00, 0xA4, 0xEB, 0x00, 0x00, 0x0D, 0x0A])

    @staticmethod
    def build_clear_command_1b06() -> bytes:
        """
        Komenda czyszczenia 1B 06
        Przykład z logów: 1B 06 0C 00 C9 A7 00 00 0C 00 0D 0A
        """
        return bytes([0x1B, 0x06, 0x0C, 0x00, 0xC9, 0xA7, 0x00, 0x00, 0x0C, 0x00, 0x0D, 0x0A])

    @staticmethod
    def build_set_tor_command(tor_number: int, line: int = 0) -> bytes:
        """
        Komenda 1B 08 - ustawienie toru
        Przykład: 1B 08 E8 00 E4 92 00 00 01 00 00 00 00 00 00 00 01 00 0A 00 00 00 00 00 00 00 00 00 00 00
                  54 4F 52 20 31 20 20 20 30 29 [zera] 0D 0A
        """
        text = f"TOR {tor_number}    0)"

        # Określ offset linii
        line_offset = 0x00 if line == 0 else 0x10

        # Bajty kontrolne różnią się dla każdego toru
        if tor_number == 1:
            checksum = bytes([0xE4, 0x92])
            tor_byte = 0x01
            offset_byte = 0x00
        else:  # tor 2
            checksum = bytes([0xF8, 0x77])
            tor_byte = 0x02
            offset_byte = 0x38

        command = bytearray([
            0x1B, 0x08,  # Nagłówek
            0xE8, 0x00,  # Typ
        ])
        command.extend(checksum)
        command.extend([
            0x00, 0x00,
            0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            tor_byte, 0x00,  # Numer toru
            0x0A, 0x00,
            0x00, 0x00,
            line_offset, 0x00,  # Linia
            0x00, 0x00, 0x00, 0x00,
            offset_byte, 0x00,  # Offset dla toru 2
        ])

        # Dodaj tekst
        command.extend(text.encode('ascii'))

        # Dopełnij zerami do długości 232 bajty (przed 0D 0A)
        while len(command) < 232:
            command.append(0x00)

        # Końcówka
        command.extend([0x0D, 0x0A])

        return bytes(command)

    @staticmethod
    def build_clear_tor_command(tor_number: int) -> bytes:
        """
        Komenda czyszczenia konkretnego toru (1B 08 z zerami)
        """
        line_offset = 0x00 if tor_number == 1 else 0x10

        if tor_number == 1:
            checksum = bytes([0x22, 0x71])
        else:
            checksum = bytes([0x23, 0xE6])

        command = bytearray([
            0x1B, 0x08,
            0xE8, 0x00,
        ])
        command.extend(checksum)
        command.extend([
            0x00, 0x00,
            0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            tor_number, 0x00,
            0x0A, 0x00,
            0x00, 0x00,
            line_offset, 0x00,
            0x00, 0x00, 0x00, 0x00,
        ])

        if tor_number == 2:
            command.append(0x38)
            command.append(0x00)
        else:
            command.append(0x00)
            command.append(0x00)

        # Reszta zer
        while len(command) < 232:
            command.append(0x00)

        command.extend([0x0D, 0x0A])
        return bytes(command)

    @staticmethod
    def build_display_time_command(time_text: str, line: int = 0, with_tor: bool = False) -> bytes:
        """
        Komenda wyświetlenia czasu

        Format czasu: "00'02".023  -" (bez TOR)
        Format z TOR: "00'13".679 TOR 2 "

        Typ komendy:
        - 1B 07 3A (58 bajtów) - bez TOR
        - 1B 07 3E (62 bajty) - z TOR
        """
        line_offset = 0x00 if line == 0 else 0x10

        if with_tor:
            cmd_type = 0x3E
            target_len = 60  # przed 0D 0A
        else:
            cmd_type = 0x3A
            target_len = 56  # przed 0D 0A

        command = bytearray([
            0x1B, 0x07,  # Nagłówek
            cmd_type, 0x00,  # Typ
            0x00, 0x00, 0x00, 0x00,  # Checksum (możemy użyć zer dla testu)
            0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00,
            line_offset, 0x00,  # Linia
            0x0A, 0x00,
        ])

        # Dodaj tekst
        command.extend(time_text.encode('ascii'))

        # Dopełnij spacjami
        while len(command) < target_len:
            command.append(0x20)

        # Końcówka
        command.extend([0x0D, 0x0A])

        return bytes(command)

    @staticmethod
    def build_display_text_command(text: str, line: int = 0) -> bytes:
        """
        Komenda wyświetlenia tekstu (np. nazwa wydarzenia)
        Przykład: "Tymon" używa 1B 07 52 (82 bajty)
        """
        line_offset = 0x00 if line == 0 else 0x10

        command = bytearray([
            0x1B, 0x07,
            0x52, 0x00,  # Typ dla tekstu
            0xAA, 0xC2, 0x00, 0x00,  # Checksum (z przykładu "Tymon")
            0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00,
            line_offset, 0x00,
            0x0A, 0x00,
        ])

        # Dodaj tekst
        command.extend(text.encode('ascii', errors='replace'))

        # Dopełnij spacjami i "--"
        while len(command) < 54:
            command.append(0x20)

        # Dodaj "--" jak w oryginale
        command.extend([0x2D, 0x2D, 0x20])

        # Więcej spacjów
        while len(command) < 80:
            command.append(0x20)

        command.extend([0x0D, 0x0A])

        return bytes(command)


class LEDDisplay:
    """Klasa do obsługi wyświetlacza LED - NAPRAWIONA"""

    def __init__(self, port: Optional[str] = None, baudrate: int = 9600):
        self.port = port or self._auto_detect_port()
        self.baudrate = baudrate
        self.serial_conn = None
        self.is_connected = False
        self.rotation_thread = None
        self.stop_rotation = False
        self.protocol = LEDDisplayProtocol()

        print(f"LED Display - {self.port} @ {baudrate} baud")

    def _auto_detect_port(self) -> str:
        ports = serial.tools.list_ports.comports()
        if not ports:
            raise Exception("Nie znaleziono portów COM!")
        return ports[0].device

    def connect(self) -> bool:
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1,
                write_timeout=2
            )

            time.sleep(0.3)

            # Wyślij Set9600 (3x jak w oryginale)
            print("📤 Wysyłam komendę Set9600...")
            init_cmd = self.protocol.build_init_command()
            for i in range(3):
                self.serial_conn.write(init_cmd)
                self.serial_conn.flush()
                time.sleep(0.1)

            self.is_connected = True
            print(f"✅ Połączono z tablicą LED")
            return True

        except Exception as e:
            print(f"❌ Błąd: {e}")
            self.is_connected = False
            return False

    def disconnect(self):
        self.stop_rotation = True
        if self.rotation_thread and self.rotation_thread.is_alive():
            self.rotation_thread.join(timeout=2)

        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            self.is_connected = False
            print("✅ Rozłączono")

    def _send_command(self, command: bytes):
        if not self.is_connected or not self.serial_conn:
            print("⚠️  Nie połączono!")
            return

        try:
            self.serial_conn.write(command)
            self.serial_conn.flush()
            time.sleep(0.05)
        except Exception as e:
            print(f"❌ Błąd wysyłania: {e}")

    def clear(self):
        """Wyczyszczenie tablicy"""
        print("🔴 Czyszczenie tablicy...")

        # Komenda 1B 06
        clear_cmd = self.protocol.build_clear_command_1b06()
        self._send_command(clear_cmd)
        time.sleep(0.1)

        # Wyczyść oba tory komendami 1B 08
        for tor in [1, 2]:
            clear_tor = self.protocol.build_clear_tor_command(tor)
            self._send_command(clear_tor)
            time.sleep(0.1)

    def init_tors(self):
        """Inicjalizacja torów (TOR 1  0) i (TOR 2  0))"""
        print("📤 Inicjalizacja torów...")
        for tor in [1, 2]:
            line = 0 if tor == 1 else 1
            cmd = self.protocol.build_set_tor_command(tor, line)
            self._send_command(cmd)
            time.sleep(0.1)

    def show_text(self, text: str, line: int = 0):
        """Wyświetl tekst (np. nazwa wydarzenia)"""
        print(f"📺 Tekst na linii {line + 1}: {text}")
        cmd = self.protocol.build_display_text_command(text, line)
        self._send_command(cmd)

    def show_time(self, time_str: str, lane: int = 0, line: int = 0):
        """
        Wyświetl czas
        time_str: format "00:02.023" lub "01:23.456"
        """
        # Konwertuj na format tablicy: "00'02".023"
        parts = time_str.split(":")
        if len(parts) == 2:
            minutes = parts[0]
            seconds = parts[1]
            time_formatted = f"{minutes}'{seconds}"
        else:
            time_formatted = time_str

        # Dodaj oznaczenie toru lub "-"
        if lane > 0:
            display_text = f"{time_formatted} TOR {lane} "
            with_tor = True
        else:
            display_text = f"{time_formatted}  - "
            with_tor = False

        cmd = self.protocol.build_display_time_command(display_text, line, with_tor)
        self._send_command(cmd)

    def show_single_time(self, time_str: str, lane: int = 1):
        print(f"📺 1 TOR: {time_str}")
        self.show_time(time_str, lane, line=0)

    def show_two_times(self, time1: str, time2: str, lane1: int = 1, lane2: int = 2):
        print(f"📺 2 TORY:")
        print(f"   TOR {lane1}: {time1}")
        print(f"   TOR {lane2}: {time2}")

        self.show_time(time1, lane1, line=0)
        time.sleep(0.1)
        self.show_time(time2, lane2, line=1)

    def show_times_rotation(self, times: List[Tuple[int, str]], interval: float = 3.0):
        if not times:
            return

        self.stop_rotation = True
        if self.rotation_thread and self.rotation_thread.is_alive():
            self.rotation_thread.join(timeout=1)

        self.stop_rotation = False
        self.rotation_thread = threading.Thread(
            target=self._rotation_worker,
            args=(times, interval),
            daemon=True
        )
        self.rotation_thread.start()

    def _rotation_worker(self, times: List[Tuple[int, str]], interval: float):
        print(f"🔄 Rotacja {len(times)} czasów (co {interval}s)")

        index = 0
        while not self.stop_rotation:
            current_times = times[index:index + 2]

            if len(current_times) == 1:
                lane, time_str = current_times[0]
                print(f"  [{datetime.now().strftime('%H:%M:%S')}] TOR {lane}: {time_str}")
                self.show_single_time(time_str, lane)

            elif len(current_times) == 2:
                lane1, time1 = current_times[0]
                lane2, time2 = current_times[1]
                print(f"  [{datetime.now().strftime('%H:%M:%S')}] TOR {lane1}: {time1} | TOR {lane2}: {time2}")
                self.show_two_times(time1, time2, lane1, lane2)

            time.sleep(interval)

            index += 2
            if index >= len(times):
                index = 0
                print("  🔄 Powrót")

    def stop_rotation_display(self):
        self.stop_rotation = True
        if self.rotation_thread and self.rotation_thread.is_alive():
            self.rotation_thread.join(timeout=2)


class LEDDisplayManager:
    """Manager - kompatybilny z poprzednim API"""

    def __init__(self, port: Optional[str] = None, baudrate: int = 9600):
        self.display = LEDDisplay(port, baudrate)
        self.current_race_times: List[Tuple[int, str]] = []
        self.is_active = False

    def initialize(self) -> bool:
        if self.display.connect():
            self.is_active = True
            # Inicjalizuj tory
            self.display.init_tors()
            time.sleep(0.5)
            return True
        return False

    def shutdown(self):
        self.display.clear()
        self.display.disconnect()
        self.is_active = False

    def show_event_name(self, event_name: str, duration: float = 5.0):
        if not self.is_active:
            return
        self.display.show_text(event_name, line=0)
        time.sleep(duration)

    def update_race_results(self, race_data: dict):
        if not self.is_active:
            return

        results = race_data.get('results', [])
        results_sorted = sorted(results, key=lambda x: x['lane'])
        times = [(r['lane'], r['time']) for r in results_sorted if r.get('time')]

        if not times:
            return

        if len(times) == 1:
            lane, time_str = times[0]
            self.display.show_single_time(time_str, lane)

        elif len(times) == 2:
            self.display.show_two_times(
                times[0][1], times[1][1],
                times[0][0], times[1][0]
            )

        else:
            self.display.show_times_rotation(times, interval=3.0)

        self.current_race_times = times

    def clear_display(self):
        if not self.is_active:
            return

        print("🔴 Nowy bieg - czyszczenie")
        self.display.stop_rotation_display()
        self.display.clear()
        time.sleep(0.5)
        # Ponownie zainicjalizuj tory
        self.display.init_tors()
        self.current_race_times = []


def find_available_ports() -> List[str]:
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]


def format_time_for_display(seconds: float) -> str:
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes:02d}:{secs:06.3f}"
