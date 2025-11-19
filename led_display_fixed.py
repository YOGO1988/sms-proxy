#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LED Display Module - FIXED dla Twojej tablicy
Oparty na FAKTYCZNYM protokole wykrytym z oryginalnego programu

YO&GO Events - 2025
"""

import serial
import serial.tools.list_ports
import time
import threading
from datetime import datetime
from typing import List, Optional, Tuple


class LEDDisplayProtocol:
    """Klasa obsługująca protokół Twojej tablicy LED"""

    # Kody komend
    CMD_INIT = bytes([0x1B, 0x09])
    CMD_DISPLAY_LINE = bytes([0x1B, 0x07])
    CMD_SET_LINE = bytes([0x1B, 0x08])

    @staticmethod
    def calculate_checksum(data: bytes) -> int:
        """
        Oblicz checksum (na podstawie analizy - może być suma, XOR, CRC)
        TODO: Może wymagać dostosowania po testach
        """
        return sum(data) & 0xFF

    @staticmethod
    def build_init_command() -> bytes:
        """
        Komenda inicjalizacyjna (Set9600)
        Na podstawie: 1B 09 0A 00 A4 EB 00 00 0D 0A
        """
        return bytes([0x1B, 0x09, 0x0A, 0x00, 0xA4, 0xEB, 0x00, 0x00, 0x0D, 0x0A])

    @staticmethod
    def build_display_command(text: str, line: int = 0) -> bytes:
        """
        Zbuduj komendę wyświetlenia tekstu

        Args:
            text: Tekst do wyświetlenia (format: "00'02".043" lub "00'02".043 TOR 1")
            line: Numer linii (0 = pierwsza, 1 = druga)

        Returns:
            Bajty komendy gotowe do wysłania
        """
        # Konwertuj tekst na bajty ASCII
        text_bytes = text.encode('ascii', errors='replace')

        # Długość danych (przykładowo - może wymagać korekty)
        data_len = len(text_bytes)

        # Buduj komendę według wzorca:
        # 1B 07 3A 00 [kontrolne] ... 0A 00 [TEKST] 0D 0A

        # Dla uproszczenia - kopiuj strukturę z oryginalnego programu
        # Linia określona przez bajt w pozycji 18-19
        line_offset = 0x00 if line == 0 else 0x10

        command = bytearray([
            0x1B, 0x07,  # Nagłówek
            0x3A, 0x00,  # Długość/typ?
            0x00, 0x00, 0x00, 0x00,  # Kontrolne
            0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # Kontrolne
            0x00, 0x00,  # Kontrolne
            line_offset, 0x00,  # Linia (0x00 = linia 1, 0x10 = linia 2)
            0x0A, 0x00,  # Separator?
        ])

        # Dodaj tekst
        command.extend(text_bytes)

        # Dopełnij spacjami do stałej długości (jak w oryginale - ~35 znaków)
        while len(command) < 56:
            command.append(0x20)  # Spacja

        # Dodaj końcówkę
        command.extend([0x0D, 0x0A])

        return bytes(command)

    @staticmethod
    def build_clear_command() -> bytes:
        """
        Komenda wyczyszczenia tablicy
        Na podstawie: 1B 08 E8 00 ... [puste dane] ... 0D 0A
        """
        command = bytearray([
            0x1B, 0x08,  # Nagłówek CLEAR
            0xE8, 0x00,
            0x00, 0x00, 0x00, 0x00,
            0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x01, 0x00,
            0x0A, 0x00,
            0x00, 0x00,
        ])

        # Dopełnij pustymi bajtami
        for _ in range(180):
            command.append(0x00)

        # Końcówka
        command.extend([0x0D, 0x0A])

        return bytes(command)


class LEDDisplay:
    """Klasa do obsługi wyświetlacza LED - FIXED VERSION"""

    def __init__(self, port: Optional[str] = None, baudrate: int = 9600):
        """
        Inicjalizacja wyświetlacza LED

        Args:
            port: Port COM (np. 'COM5'). Jeśli None, zostanie wykryty automatycznie
            baudrate: Prędkość transmisji (domyślnie 9600)
        """
        self.port = port or self._auto_detect_port()
        self.baudrate = baudrate
        self.serial_conn = None
        self.is_connected = False
        self.rotation_thread = None
        self.stop_rotation = False
        self.protocol = LEDDisplayProtocol()

        print(f"LED Display - Konfiguracja: {self.port} @ {baudrate} baud")

    def _auto_detect_port(self) -> str:
        """Automatyczne wykrywanie portu COM"""
        ports = serial.tools.list_ports.comports()
        if not ports:
            raise Exception("Nie znaleziono żadnych portów COM!")

        port = ports[0].device
        print(f"Auto-detect: Wykryto port {port}")
        return port

    def connect(self) -> bool:
        """
        Nawiązanie połączenia z tablicą

        Returns:
            True jeśli połączono pomyślnie
        """
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

            time.sleep(0.3)  # Czekaj na stabilizację

            # Wyślij komendę inicjalizacyjną (Set9600)
            print("📤 Wysyłam komendę inicjalizacyjną...")
            init_cmd = self.protocol.build_init_command()
            self.serial_conn.write(init_cmd)
            self.serial_conn.flush()
            time.sleep(0.5)

            self.is_connected = True
            print(f"✅ Połączono z tablicą LED na {self.port}")
            return True

        except Exception as e:
            print(f"❌ Błąd połączenia z tablicą: {e}")
            self.is_connected = False
            return False

    def disconnect(self):
        """Rozłączenie z tablicą"""
        self.stop_rotation = True
        if self.rotation_thread and self.rotation_thread.is_alive():
            self.rotation_thread.join(timeout=2)

        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            self.is_connected = False
            print("✅ Rozłączono z tablicą LED")

    def _send_command(self, command: bytes):
        """
        Wysłanie komendy do tablicy

        Args:
            command: Bajty komendy
        """
        if not self.is_connected or not self.serial_conn:
            print("⚠️  Tablica nie jest połączona!")
            return

        try:
            self.serial_conn.write(command)
            self.serial_conn.flush()
            time.sleep(0.05)  # Krótka przerwa między komendami

        except Exception as e:
            print(f"❌ Błąd wysyłania do tablicy: {e}")

    def clear(self):
        """Wyczyszczenie tablicy (zgaszenie)"""
        print("🔴 Czyszczenie tablicy...")
        clear_cmd = self.protocol.build_clear_command()
        self._send_command(clear_cmd)

        # Wyślij 3 razy dla pewności (jak w oryginalnym programie)
        time.sleep(0.1)
        self._send_command(clear_cmd)
        time.sleep(0.1)
        self._send_command(clear_cmd)

    def show_text(self, text: str, line: int = 0):
        """
        Wyświetlenie tekstu na określonej linii

        Args:
            text: Tekst do wyświetlenia
            line: Numer linii (0 = pierwsza, 1 = druga)
        """
        print(f"📺 Wyświetlam na linii {line + 1}: {text}")
        cmd = self.protocol.build_display_command(text, line)
        self._send_command(cmd)

    def show_time(self, time_str: str, lane: int = 0, line: int = 0):
        """
        Wyświetlenie czasu (format jak w oryginalnym programie)

        Args:
            time_str: Czas w formacie "MM:SS.mmm"
            lane: Numer toru (0 = bez etykiety, 1+ = "TOR X")
            line: Numer linii (0 lub 1)
        """
        # Konwertuj format czasu na format tablicy: "00'02".043"
        # Z "01:23.456" na "00'23".456" lub z "02:34.567" na "02'34".567"

        parts = time_str.replace(":", "'").split(".")
        if len(parts) == 2:
            time_formatted = f"{parts[0]}\"{parts[1]}"
        else:
            time_formatted = time_str

        # Dodaj oznaczenie toru jeśli podane
        if lane > 0:
            display_text = f"{time_formatted} TOR {lane}"
        else:
            display_text = f"{time_formatted}  -"

        self.show_text(display_text, line)

    def show_single_time(self, time_str: str, lane: int = 1):
        """
        Wyświetlenie pojedynczego czasu

        Args:
            time_str: Czas w formacie "MM:SS.mmm"
            lane: Numer toru
        """
        print(f"📺 1 TOR: {time_str}")
        self.show_time(time_str, lane, line=0)

    def show_two_times(self, time1: str, time2: str, lane1: int = 1, lane2: int = 2):
        """
        Wyświetlenie dwóch czasów (2 linie)

        Args:
            time1: Czas pierwszego zawodnika
            time2: Czas drugiego zawodnika
            lane1: Numer toru pierwszego
            lane2: Numer toru drugiego
        """
        print(f"📺 2 TORY:")
        print(f"   TOR {lane1}: {time1}")
        print(f"   TOR {lane2}: {time2}")

        self.show_time(time1, lane1, line=0)
        time.sleep(0.1)
        self.show_time(time2, lane2, line=1)

    def show_times_rotation(self, times: List[Tuple[int, str]], interval: float = 3.0):
        """
        Wyświetlenie czasów z rotacją (dla więcej niż 2 zawodników)

        Args:
            times: Lista krotek (numer_toru, czas)
            interval: Czas wyświetlania każdej pary (w sekundach)
        """
        if not times:
            return

        # Zatrzymaj poprzednią rotację
        self.stop_rotation = True
        if self.rotation_thread and self.rotation_thread.is_alive():
            self.rotation_thread.join(timeout=1)

        # Uruchom nową rotację
        self.stop_rotation = False
        self.rotation_thread = threading.Thread(
            target=self._rotation_worker,
            args=(times, interval),
            daemon=True
        )
        self.rotation_thread.start()

    def _rotation_worker(self, times: List[Tuple[int, str]], interval: float):
        """
        Wątek wykonujący rotację czasów

        Args:
            times: Lista krotek (numer_toru, czas)
            interval: Czas wyświetlania każdej pary
        """
        print(f"🔄 Rotacja {len(times)} czasów (po 2 naraz, co {interval}s)")

        index = 0
        while not self.stop_rotation:
            # Pobierz aktualną parę czasów
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

            # Czekaj
            time.sleep(interval)

            # Następna para
            index += 2
            if index >= len(times):
                index = 0
                print("  🔄 Powrót do początku rotacji")

    def stop_rotation_display(self):
        """Zatrzymanie rotacji czasów"""
        print("⏹️  Zatrzymywanie rotacji...")
        self.stop_rotation = True
        if self.rotation_thread and self.rotation_thread.is_alive():
            self.rotation_thread.join(timeout=2)


class LEDDisplayManager:
    """Manager do zarządzania wyświetlaczem LED - FIXED VERSION"""

    def __init__(self, port: Optional[str] = None, baudrate: int = 9600):
        self.display = LEDDisplay(port, baudrate)
        self.current_race_times: List[Tuple[int, str]] = []
        self.is_active = False

    def initialize(self) -> bool:
        """Inicjalizacja połączenia z tablicą"""
        if self.display.connect():
            self.is_active = True
            time.sleep(0.5)
            return True
        return False

    def shutdown(self):
        """Wyłączenie tablicy"""
        self.display.clear()
        self.display.disconnect()
        self.is_active = False

    def show_event_name(self, event_name: str, duration: float = 5.0):
        """Wyświetlenie nazwy wydarzenia"""
        if not self.is_active:
            return

        self.display.show_text(event_name, line=0)
        time.sleep(duration)

    def update_race_results(self, race_data: dict):
        """
        Aktualizacja wyników biegu na tablicy

        Args:
            race_data: Słownik z danymi biegu
        """
        if not self.is_active:
            return

        results = race_data.get('results', [])
        results_sorted = sorted(results, key=lambda x: x['lane'])
        times = [(r['lane'], r['time']) for r in results_sorted if r.get('time')]

        if not times:
            print("⚠️  Brak czasów do wyświetlenia")
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
        """Wyczyszczenie tablicy"""
        if not self.is_active:
            return

        print("🔴 Nowy bieg - czyszczenie tablicy")
        self.display.stop_rotation_display()
        self.display.clear()
        self.current_race_times = []


# === FUNKCJE POMOCNICZE ===

def find_available_ports() -> List[str]:
    """Znajduje wszystkie dostępne porty COM"""
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]


def format_time_for_display(seconds: float) -> str:
    """
    Formatowanie czasu z sekund na format MM:SS.mmm (do przekazania do show_time)

    Args:
        seconds: Czas w sekundach

    Returns:
        Sformatowany string czasu
    """
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes:02d}:{secs:06.3f}"
