#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LED Display Module - Moduł do obsługi tablicy LED przez port COM
YO&GO Events - 2025

Funkcje:
- Wyświetlanie czasów w biegach (1 tor, 2 tory, rotacja dla więcej zawodników)
- Czyszczenie tablicy
- Wyświetlanie nazwy wydarzenia
- Automatyczna rotacja czasów
"""

import serial
import serial.tools.list_ports
import time
import threading
from datetime import datetime
from typing import List, Optional, Tuple


class LEDDisplay:
    """Klasa do obsługi wyświetlacza LED"""

    def __init__(self, port: Optional[str] = None, baudrate: int = 9600,
                 line_ending: str = "\r\n", protocol: str = "ascii"):
        """
        Inicjalizacja wyświetlacza LED

        Args:
            port: Port COM (np. 'COM3' lub '/dev/ttyUSB0'). Jeśli None, zostanie wykryty automatycznie
            baudrate: Prędkość transmisji (9600, 19200, 38400, 57600, 115200)
            line_ending: Końcówka linii ("\r\n", "\n", "\r" lub "")
            protocol: Protokół komunikacji ("ascii", "hex", "stx_etx")
        """
        self.port = port or self._auto_detect_port()
        self.baudrate = baudrate
        self.line_ending = line_ending
        self.protocol = protocol
        self.serial_conn = None
        self.is_connected = False
        self.rotation_thread = None
        self.stop_rotation = False

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
                timeout=1
            )
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

    def _send_command(self, text: str):
        """
        Wysłanie komendy do tablicy

        Args:
            text: Tekst do wysłania
        """
        if not self.is_connected or not self.serial_conn:
            print("⚠️  Tablica nie jest połączona!")
            return

        try:
            if self.protocol == "ascii":
                # Prosty tekst ASCII
                data = (text + self.line_ending).encode('utf-8')
                self.serial_conn.write(data)

            elif self.protocol == "hex":
                # Konwersja tekstu na bajty HEX
                data = text.encode('utf-8')
                self.serial_conn.write(data)

            elif self.protocol == "stx_etx":
                # Format STX + DATA + ETX
                STX = 0x02
                ETX = 0x03
                data = bytes([STX]) + text.encode('utf-8') + bytes([ETX])
                self.serial_conn.write(data)

            # Debug info
            # print(f"📤 Wysłano: {text}")

        except Exception as e:
            print(f"❌ Błąd wysyłania do tablicy: {e}")

    def clear(self):
        """Wyczyszczenie tablicy (zgaszenie)"""
        print("🔴 Czyszczenie tablicy...")

        # Różne komendy czyszczące w zależności od protokołu
        if self.protocol == "ascii":
            # Puste linie lub specjalne znaki
            self._send_command("")
            time.sleep(0.1)
            self._send_command(" ")
            time.sleep(0.1)
            # Spróbuj także escape sequences
            self._send_command("\x0C")  # Form Feed

        elif self.protocol == "hex":
            # Zerowe bajty
            if self.serial_conn:
                self.serial_conn.write(bytes([0x00, 0x00, 0x00]))
                time.sleep(0.1)
                self.serial_conn.write(bytes([0xFF, 0xFF, 0xFF]))

        elif self.protocol == "stx_etx":
            # Pusta komenda w STX/ETX
            if self.serial_conn:
                self.serial_conn.write(bytes([0x02, 0x03]))

    def show_text(self, text: str, duration: Optional[float] = None):
        """
        Wyświetlenie dowolnego tekstu (np. nazwa wydarzenia)

        Args:
            text: Tekst do wyświetlenia
            duration: Czas wyświetlania w sekundach (None = bez limitu)
        """
        print(f"📺 Wyświetlam tekst: {text}")
        self._send_command(text)

        if duration:
            time.sleep(duration)

    def show_time(self, time_str: str, line: int = 1):
        """
        Wyświetlenie czasu na określonej linii

        Args:
            time_str: Czas w formacie "MM.SS" lub "MM:SS.mmm"
            line: Numer linii (1 lub 2)
        """
        if line == 1:
            self._send_command(f"L1:{time_str}")
        else:
            self._send_command(f"L2:{time_str}")

    def show_single_time(self, time_str: str):
        """
        Wyświetlenie pojedynczego czasu (1 zawodnik, 1 linia)

        Args:
            time_str: Czas w formacie "MM.SS.mmm" lub "MM:SS.mmm"
        """
        print(f"📺 1 TOR: {time_str}")
        self._send_command(time_str)

    def show_two_times(self, time1: str, time2: str):
        """
        Wyświetlenie dwóch czasów (2 zawodników, 2 linie)

        Args:
            time1: Czas pierwszego zawodnika
            time2: Czas drugiego zawodnika
        """
        print(f"📺 2 TORY:")
        print(f"   TOR 1: {time1}")
        print(f"   TOR 2: {time2}")

        # W zależności od możliwości tablicy:
        # Opcja 1: Dwie osobne komendy
        self._send_command(f"1:{time1}")
        time.sleep(0.1)
        self._send_command(f"2:{time2}")

        # Opcja 2: Jedna komenda z separatorem (jeśli tablica obsługuje)
        # self._send_command(f"{time1}|{time2}")

    def show_times_rotation(self, times: List[Tuple[int, str]],
                          interval: float = 3.0,
                          pairs: int = 2):
        """
        Wyświetlenie czasów z rotacją (dla więcej niż 2 zawodników)
        Pokazuje po 2 czasy naraz, potem przełącza na kolejne 2, itd.

        Args:
            times: Lista krotek (numer_toru, czas) np. [(1, "01:23.45"), (2, "01:24.12"), ...]
            interval: Czas wyświetlania każdej pary (w sekundach)
            pairs: Ile czasów wyświetlać jednocześnie (domyślnie 2)
        """
        if not times:
            return

        # Zatrzymaj poprzednią rotację jeśli była
        self.stop_rotation = True
        if self.rotation_thread and self.rotation_thread.is_alive():
            self.rotation_thread.join(timeout=1)

        # Uruchom nową rotację w osobnym wątku
        self.stop_rotation = False
        self.rotation_thread = threading.Thread(
            target=self._rotation_worker,
            args=(times, interval, pairs),
            daemon=True
        )
        self.rotation_thread.start()

    def _rotation_worker(self, times: List[Tuple[int, str]],
                        interval: float, pairs: int):
        """
        Wątek wykonujący rotację czasów

        Args:
            times: Lista krotek (numer_toru, czas)
            interval: Czas wyświetlania każdej pary
            pairs: Ile czasów wyświetlać jednocześnie
        """
        print(f"🔄 Rotacja {len(times)} czasów (po {pairs} na raz, co {interval}s)")

        index = 0
        while not self.stop_rotation:
            # Pobierz aktualną parę/grupę czasów
            current_times = times[index:index + pairs]

            if len(current_times) == 1:
                # Jeden czas - wyświetl w jednej linii
                tor, time_str = current_times[0]
                print(f"  [{datetime.now().strftime('%H:%M:%S')}] TOR {tor}: {time_str}")
                self.show_single_time(f"TOR {tor}: {time_str}")

            elif len(current_times) == 2:
                # Dwa czasy - wyświetl w dwóch liniach
                tor1, time1 = current_times[0]
                tor2, time2 = current_times[1]
                print(f"  [{datetime.now().strftime('%H:%M:%S')}] TOR {tor1}: {time1} | TOR {tor2}: {time2}")
                self.show_two_times(f"TOR {tor1}: {time1}", f"TOR {tor2}: {time2}")

            # Czekaj określony interwał
            time.sleep(interval)

            # Przejdź do następnej grupy
            index += pairs

            # Jeśli doszliśmy do końca, wróć na początek
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
    """Manager do zarządzania wyświetlaczem LED w kontekście zawodów"""

    def __init__(self, port: Optional[str] = None, baudrate: int = 9600):
        """
        Inicjalizacja managera

        Args:
            port: Port COM
            baudrate: Prędkość transmisji
        """
        self.display = LEDDisplay(port, baudrate)
        self.current_race_times: List[Tuple[int, str]] = []
        self.is_active = False

    def initialize(self) -> bool:
        """
        Inicjalizacja połączenia z tablicą

        Returns:
            True jeśli połączono pomyślnie
        """
        if self.display.connect():
            self.is_active = True
            # Wyświetl powitanie
            self.display.show_text("YO&GO EVENTS", duration=2)
            self.display.clear()
            return True
        return False

    def shutdown(self):
        """Wyłączenie tablicy"""
        self.display.clear()
        self.display.disconnect()
        self.is_active = False

    def show_event_name(self, event_name: str, duration: float = 5.0):
        """
        Wyświetlenie nazwy wydarzenia

        Args:
            event_name: Nazwa wydarzenia
            duration: Czas wyświetlania w sekundach
        """
        if not self.is_active:
            return

        self.display.show_text(event_name, duration)

    def update_race_results(self, race_data: dict):
        """
        Aktualizacja wyników biegu na tablicy

        Args:
            race_data: Słownik z danymi biegu:
                {
                    'race_number': int,
                    'lanes': int,  # liczba torów
                    'results': [
                        {'lane': 1, 'time': '01:23.456'},
                        {'lane': 2, 'time': '01:24.123'},
                        ...
                    ]
                }
        """
        if not self.is_active:
            return

        lanes = race_data.get('lanes', 1)
        results = race_data.get('results', [])

        # Sortuj wyniki po torze
        results_sorted = sorted(results, key=lambda x: x['lane'])

        # Przygotuj listę czasów
        times = [(r['lane'], r['time']) for r in results_sorted if r.get('time')]

        if not times:
            print("⚠️  Brak czasów do wyświetlenia")
            return

        # Wyświetl w zależności od liczby zawodników
        if len(times) == 1:
            # Jeden zawodnik - jedna linia
            lane, time_str = times[0]
            self.display.show_single_time(f"TOR {lane}: {time_str}")

        elif len(times) == 2:
            # Dwóch zawodników - dwie linie
            time1 = f"TOR {times[0][0]}: {times[0][1]}"
            time2 = f"TOR {times[1][0]}: {times[1][1]}"
            self.display.show_two_times(time1, time2)

        else:
            # Więcej niż 2 zawodników - rotacja
            self.display.show_times_rotation(times, interval=3.0, pairs=2)

        self.current_race_times = times

    def clear_display(self):
        """
        Wyczyszczenie tablicy (np. przy rozpoczęciu nowego biegu)
        Sygnalizuje że system działa
        """
        if not self.is_active:
            return

        print("🔴 Nowy bieg - czyszczenie tablicy")
        self.display.stop_rotation_display()
        self.display.clear()
        self.current_race_times = []


# === FUNKCJE POMOCNICZE ===

def find_available_ports() -> List[str]:
    """
    Znajduje wszystkie dostępne porty COM

    Returns:
        Lista nazw portów
    """
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]


def test_display_connection(port: str, baudrate: int = 9600) -> bool:
    """
    Test połączenia z tablicą

    Args:
        port: Port COM
        baudrate: Prędkość transmisji

    Returns:
        True jeśli test się powiódł
    """
    try:
        display = LEDDisplay(port, baudrate)
        if display.connect():
            display.show_text("TEST OK", duration=2)
            display.clear()
            display.disconnect()
            return True
        return False
    except Exception as e:
        print(f"❌ Test nieudany: {e}")
        return False


def format_time(seconds: float) -> str:
    """
    Formatowanie czasu z sekund na format MM:SS.mmm

    Args:
        seconds: Czas w sekundach

    Returns:
        Sformatowany string czasu
    """
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes:02d}:{secs:06.3f}"


# === PRZYKŁAD UŻYCIA ===

if __name__ == "__main__":
    print("=" * 60)
    print("LED Display Module - Test")
    print("=" * 60)

    # Znajdź dostępne porty
    ports = find_available_ports()
    print(f"\nDostępne porty: {ports}")

    if not ports:
        print("❌ Brak dostępnych portów COM!")
        exit(1)

    # Użyj pierwszego portu
    port = ports[0]
    print(f"\n📍 Testuję port: {port}")

    # Test połączenia
    print("\n1️⃣ Test połączenia...")
    if test_display_connection(port):
        print("✅ Test połączenia OK")
    else:
        print("❌ Test połączenia FAILED")
        exit(1)

    # Test podstawowych funkcji
    print("\n2️⃣ Test funkcji wyświetlania...")
    manager = LEDDisplayManager(port)

    if manager.initialize():
        print("✅ Manager zainicjalizowany")

        # Test 1: Nazwa wydarzenia
        print("\n   Test: Nazwa wydarzenia")
        manager.show_event_name("TURNIEJ 2025", duration=3)

        # Test 2: Jeden zawodnik
        print("\n   Test: Jeden zawodnik")
        manager.update_race_results({
            'race_number': 1,
            'lanes': 1,
            'results': [
                {'lane': 1, 'time': '01:23.456'}
            ]
        })
        time.sleep(4)

        # Test 3: Dwóch zawodników
        print("\n   Test: Dwóch zawodników")
        manager.clear_display()
        time.sleep(1)
        manager.update_race_results({
            'race_number': 2,
            'lanes': 2,
            'results': [
                {'lane': 1, 'time': '01:23.456'},
                {'lane': 2, 'time': '01:24.789'}
            ]
        })
        time.sleep(4)

        # Test 4: Czterech zawodników (rotacja)
        print("\n   Test: Czterech zawodników (rotacja)")
        manager.clear_display()
        time.sleep(1)
        manager.update_race_results({
            'race_number': 3,
            'lanes': 4,
            'results': [
                {'lane': 1, 'time': '01:23.456'},
                {'lane': 2, 'time': '01:24.789'},
                {'lane': 3, 'time': '01:25.123'},
                {'lane': 4, 'time': '01:26.456'}
            ]
        })

        # Czekaj 15 sekund żeby zobaczyć rotację
        print("   (rotacja przez 15 sekund...)")
        time.sleep(15)

        # Zakończ
        print("\n✅ Wszystkie testy zakończone")
        manager.shutdown()
    else:
        print("❌ Nie udało się zainicjalizować managera")

    print("\n" + "=" * 60)
    print("Koniec testu")
    print("=" * 60)
