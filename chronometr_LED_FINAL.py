#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=====================================================
CHRONOMETR Z TABLICĄ LED - WERSJA FINALNA
=====================================================

Program chronometru lekkoatletycznego z pełną integracją tablicy LED

Funkcje:
- Chronometr dla wielu zawodników
- Automatyczne wyświetlanie czasów na tablicy LED
- Ranking z rotacją wyników
- Konfiguracja portu LED z GUI
- Ustawianie jasności tablicy
- Obsługa 1 lub 2 linii czasów

Autor: YO&GO Events 2025
"""

import tkinter as tk
from tkinter import messagebox, ttk
import serial
import time
import threading
from datetime import datetime
from typing import List, Tuple, Optional


# ============================================================================
# OBSŁUGA TABLICY LED - WSZYSTKIE FUNKCJE
# ============================================================================

def calculate_crc16(data: bytes) -> int:
    """CRC-16-CCITT dla protokołu tablicy LED"""
    crc = 0x0000
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc


def create_time_packet_line1(time_str: str) -> bytes:
    """
    Pakiet czasu dla linii 1

    Args:
        time_str: Czas w formacie "MM:SS.mmm"

    Returns:
        Pakiet bajtów do wysłania na tablicę
    """
    base = bytearray.fromhex('1B 07 3A 00 51 8B 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 34 36 37 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))

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

    text_padded = (formatted + "  - ").ljust(34)[:34]
    base[22:56] = text_padded.encode('ascii', errors='replace')

    base[4] = 0
    base[5] = 0
    crc = calculate_crc16(bytes(base))
    base[4] = crc & 0xFF
    base[5] = (crc >> 8) & 0xFF

    return bytes(base)


def create_time_packet_line2(time_str: str) -> bytes:
    """
    Pakiet czasu dla linii 2

    Args:
        time_str: Czas w formacie "MM:SS.mmm"

    Returns:
        Pakiet bajtów do wysłania na tablicę
    """
    base = bytearray.fromhex('1B 07 3A 00 51 8B 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 30 30 27 30 37 22 2E 34 36 37 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))

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

    text_padded = (formatted + "  - ").ljust(34)[:34]
    base[22:56] = text_padded.encode('ascii', errors='replace')

    base[4] = 0
    base[5] = 0
    crc = calculate_crc16(bytes(base))
    base[4] = crc & 0xFF
    base[5] = (crc >> 8) & 0xFF

    return bytes(base)


def create_ranking_packet(time_str: str, place: int, line: int) -> bytes:
    """
    Pakiet rankingowy (miejsce + czas)

    Args:
        time_str: Czas w formacie "MM:SS.mmm"
        place: Numer miejsca (1, 2, 3, ...)
        line: Numer linii (1 lub 2)

    Returns:
        Pakiet bajtów do wysłania na tablicę
    """
    if line == 1:
        base = bytearray.fromhex('1B 07 3E 00 A1 2A 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 37 38 37 20 54 4F 52 20 31 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))
    else:
        base = bytearray.fromhex('1B 07 3E 00 8F 5C 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 30 30 27 31 30 22 2E 33 36 32 20 54 4F 52 20 32 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))

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

    place_text = f"{place}."
    display_text = f"{place_text} {formatted}".ljust(38)[:38]
    base[22:60] = display_text.encode('ascii', errors='replace')

    base[4] = 0
    base[5] = 0
    crc = calculate_crc16(bytes(base))
    base[4] = crc & 0xFF
    base[5] = (crc >> 8) & 0xFF

    return bytes(base)


class LEDDisplay:
    """
    Driver tablicy LED
    Obsługuje komunikację z tablicą przez port szeregowy
    """

    PACKETS = {
        'clear_line1': bytes.fromhex('1B 07 54 00 14 75 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 2D 2D 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),
        'clear_line2': bytes.fromhex('1B 07 54 00 60 FC 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 2D 2D 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),
        'brightness_0': bytes.fromhex('1B 06 0C 00 FB E8 00 00 00 00 0D 0A'.replace(' ', '')),
        'brightness_3': bytes.fromhex('1B 06 0C 00 27 73 00 00 03 00 0D 0A'.replace(' ', '')),
        'brightness_8': bytes.fromhex('1B 06 0C 00 38 6D 00 00 08 00 0D 0A'.replace(' ', '')),
        'brightness_9': bytes.fromhex('1B 06 0C 00 8C 1B 00 00 09 00 0D 0A'.replace(' ', '')),
        'brightness_12': bytes.fromhex('1B 06 0C 00 C9 A7 00 00 0C 00 0D 0A'.replace(' ', '')),
        'brightness_15': bytes.fromhex('1B 06 0C 00 15 3C 00 00 0F 00 0D 0A'.replace(' ', '')),
        'name_event': bytes.fromhex('1B 07 52 00 AA C2 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 59 4F 26 47 4F 20 5A 41 57 4F 44 59 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 2D 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),
    }

    def __init__(self, port='COM5', baudrate=9600):
        """
        Inicjalizacja drivera tablicy LED

        Args:
            port: Port szeregowy (np. 'COM5', '/dev/ttyUSB0')
            baudrate: Prędkość transmisji (domyślnie 9600)
        """
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.connected = False
        self.current_brightness = 100

    def connect(self):
        """Połączenie z tablicą LED"""
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
        """Rozłączenie z tablicą LED"""
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.connected = False
        print("✅ Rozłączono z tablicą LED")

    def send_packet(self, packet_data, delay=0.1):
        """
        Wysłanie pakietu do tablicy

        Args:
            packet_data: Dane pakietu (bytes) lub nazwa pakietu (str)
            delay: Opóźnienie po wysłaniu w sekundach (0 dla timera)

        Returns:
            True jeśli wysłano pomyślnie, False w przeciwnym razie
        """
        if not self.connected:
            return False

        if isinstance(packet_data, str):
            packet_data = self.PACKETS.get(packet_data)
            if not packet_data:
                return False

        try:
            self.ser.write(packet_data)
            self.ser.flush()
            if delay > 0:
                time.sleep(delay)
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
        """
        brightness = max(0, min(100, brightness))

        # Mapowanie procentowe na poziomy sprzętowe (0-15)
        if brightness == 0:
            level = 0
        elif brightness <= 13:
            level = 0
        elif brightness <= 33:
            level = 3
        elif brightness <= 60:
            level = 8
        elif brightness <= 73:
            level = 9
        elif brightness < 100:
            level = 12
        else:
            level = 15

        packet_name = f'brightness_{level}'

        if packet_name not in self.PACKETS:
            level = 15
            packet_name = 'brightness_15'

        result = self.send_packet(packet_name)

        if result:
            self.current_brightness = brightness
            print(f"💡 Jasność tablicy: {brightness}% (poziom {level}/15)")

        return result

    def turn_off(self):
        """Wygaszenie tablicy (brightness = 0%)"""
        print("🔴 Wygaszanie tablicy...")
        self.clear_display()
        time.sleep(0.2)
        return self.set_brightness(0)

    def turn_on(self, brightness: int = 100):
        """Włączenie tablicy z określoną jasnością"""
        print(f"✅ Włączanie tablicy (jasność {brightness}%)...")
        return self.set_brightness(brightness)

    def clear_display(self):
        """Czyszczenie obu linii tablicy"""
        self.send_packet('clear_line1')
        time.sleep(0.05)
        self.send_packet('clear_line2')
        return True

    def show_event_name(self):
        """Wyświetlenie nazwy wydarzenia"""
        return self.send_packet('name_event')

    def show_time_with_place(self, time_str: str, place: int, line: int = 1):
        """
        Wyświetlenie czasu z numerem miejsca (dla rankingu)

        Args:
            time_str: Czas w formacie "MM:SS.mmm"
            place: Numer miejsca (1, 2, 3, ...)
            line: Numer linii (1 lub 2)
        """
        packet = create_ranking_packet(time_str, place, line)
        return self.send_packet(packet)


class LEDDisplayManager:
    """
    Manager do obsługi wyświetlacza w kontekście zawodów
    Obsługuje:
    - Tryb 2-torowy (wyniki dla 2 zawodników na TOR 1 i TOR 2)
    - Tryb rankingowy (wyniki dla 3+ zawodników w parach: 1-2, 3-4, 5-6...)
    - Rotację wyników
    """

    def __init__(self, port='COM5', baudrate=9600):
        """
        Inicjalizacja managera tablicy LED

        Args:
            port: Port szeregowy
            baudrate: Prędkość transmisji
        """
        self.display = LEDDisplay(port, baudrate)
        self.rotation_thread = None
        self.rotation_active = False
        self.current_mode = None
        self.timer_thread = None
        self.timer_active = False
        self.timer_start_time = None

    def initialize(self):
        """Inicjalizacja połączenia z tablicą"""
        if not self.display.connect():
            return False

        self.display.set_brightness(100)
        time.sleep(0.3)
        self.display.show_event_name()
        time.sleep(2)
        self.display.clear_display()
        return True

    def shutdown(self):
        """Wyłączenie i rozłączenie tablicy"""
        self.stop_rotation()
        self.display.clear_display()
        self.display.disconnect()

    def stop_rotation(self):
        """Zatrzymanie rotacji wyników"""
        self.rotation_active = False
        if self.rotation_thread and self.rotation_thread.is_alive():
            self.rotation_thread.join(timeout=2)

    def _rotation_worker_ranking(self, results: List[dict]):
        """
        Worker rotacji rankingu
        Wyświetla pary wyników: 1-2, 3-4, 5-6, itd.

        Args:
            results: Lista wyników (każdy ma 'time' i 'place')
        """
        print(f"🔄 Tryb rankingowy: {len(results)} zawodników")

        self.display.clear_display()
        time.sleep(0.2)

        index = 0
        while self.rotation_active:
            para = results[index:index+2]

            if len(para) == 1:
                # Pojedynczy wynik
                miejsce = index + 1
                czas = para[0]['time']
                pakiet = create_ranking_packet(czas, miejsce, line=1)
                self.display.send_packet(pakiet)
                time.sleep(0.05)
                self.display.send_packet('clear_line2')

            elif len(para) == 2:
                # Para wyników
                miejsce1 = index + 1
                miejsce2 = index + 2
                czas1 = para[0]['time']
                czas2 = para[1]['time']

                print(f"  📊 Miejsca {miejsce1}-{miejsce2}:")
                print(f"     {miejsce1}. {czas1}")
                print(f"     {miejsce2}. {czas2}")

                pakiet1 = create_ranking_packet(czas1, miejsce1, line=1)
                self.display.send_packet(pakiet1)
                time.sleep(0.05)

                pakiet2 = create_ranking_packet(czas2, miejsce2, line=2)
                self.display.send_packet(pakiet2)

            time.sleep(3.0)

            index += 2
            if index >= len(results):
                index = 0
                print("  🔄 Powrót do początku")

    def update_race_results(self, race_data: dict):
        """
        Aktualizacja wyników biegu na tablicy

        Args:
            race_data: {
                'race_number': int,
                'lanes': int,
                'results': [
                    {'lane': 1, 'time': '00:07.787', 'place': 1},
                    {'lane': 2, 'time': '00:10.362', 'place': 2},
                    ...
                ]
            }
        """
        self.stop_rotation()

        results = race_data.get('results', [])
        if len(results) == 0:
            self.display.clear_display()
            return

        if len(results) <= 2:
            # Bez rotacji
            if len(results) == 1:
                pakiet = create_ranking_packet(results[0]['time'], 1, line=1)
                self.display.send_packet(pakiet)
            else:
                pakiet1 = create_ranking_packet(results[0]['time'], 1, line=1)
                self.display.send_packet(pakiet1)
                time.sleep(0.05)
                pakiet2 = create_ranking_packet(results[1]['time'], 2, line=2)
                self.display.send_packet(pakiet2)
        else:
            # Z rotacją
            self.rotation_active = True
            self.rotation_thread = threading.Thread(
                target=self._rotation_worker_ranking,
                args=(results,),
                daemon=True
            )
            self.rotation_thread.start()


# ============================================================================
# GŁÓWNA APLIKACJA CHRONOMETRU
# ============================================================================

class ChronometerManager:
    """
    Manager chronometru z integracją LED
    Główna klasa aplikacji obsługująca chronometr i tablicę LED
    """

    def __init__(self, root):
        """
        Inicjalizacja managera chronometru

        Args:
            root: Główne okno Tkinter
        """
        self.root = root
        self.root.title("⏱️ CHRONOMETR LEKKOATLETYCZNY - YO&GO")
        self.root.geometry("900x700")

        # LED Display - zmienne
        self.led_manager = None
        self.led_enabled = False
        self.led_port = 'COM6'
        self.led_num_lanes = 1
        self.led_brightness = 100
        self.led_timer_thread = None
        self.led_timer_running = False

        # Chronometr - zmienne
        self.la_race_active = False
        self.la_race_number = 1
        self.la_results = []  # Lista czasów w sekundach
        self.la_start_absolute_time = None

        # GUI
        self.setup_la_tab()

    def setup_la_tab(self):
        """Tworzenie interfejsu użytkownika"""

        # Główna ramka
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Nagłówek
        header = tk.Label(main_frame, text="⏱️ CHRONOMETR LEKKOATLETYCZNY",
                         font=('Arial', 18, 'bold'), bg='white', fg='#2c3e50')
        header.pack(pady=10)

        # === KONFIGURACJA TABLICY LED ===
        led_config_frame = tk.LabelFrame(main_frame, text=" 📺 TABLICA LED ",
                                        font=('Arial', 9, 'bold'), bg='white',
                                        relief=tk.RIDGE, bd=2)
        led_config_frame.pack(fill=tk.X, padx=10, pady=3)

        # Rząd 1: Port LED
        led_row1 = tk.Frame(led_config_frame, bg='white')
        led_row1.pack(fill=tk.X, padx=10, pady=3)

        tk.Label(led_row1, text="Port LED:", font=('Arial', 9, 'bold'), bg='white').pack(side=tk.LEFT, padx=3)

        self.led_port_var = tk.StringVar(value='COM6')
        self.led_port_entry = tk.Entry(led_row1, textvariable=self.led_port_var, width=8, font=('Arial', 9))
        self.led_port_entry.pack(side=tk.LEFT, padx=3)

        self.led_connect_btn = tk.Button(led_row1, text="🔌 Połącz LED",
                                         command=self.led_connect,
                                         font=('Arial', 8), bg='#2196F3', fg='white', padx=10, pady=2)
        self.led_connect_btn.pack(side=tk.LEFT, padx=5)

        self.led_status_label = tk.Label(led_row1, text="● Rozłączone",
                                         font=('Arial', 8), fg='red', bg='white')
        self.led_status_label.pack(side=tk.LEFT, padx=10)

        # Rząd 2: Liczba linii
        led_row2 = tk.Frame(led_config_frame, bg='white')
        led_row2.pack(fill=tk.X, padx=10, pady=3)

        tk.Label(led_row2, text="Liczba torów/linii:", font=('Arial', 9), bg='white').pack(side=tk.LEFT, padx=3)

        self.led_lanes_var = tk.IntVar(value=1)
        tk.Radiobutton(led_row2, text="1 linia", variable=self.led_lanes_var, value=1,
                      font=('Arial', 9), bg='white').pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(led_row2, text="2 linie", variable=self.led_lanes_var, value=2,
                      font=('Arial', 9), bg='white').pack(side=tk.LEFT, padx=5)

        # Rząd 3: Jasność
        led_row3 = tk.Frame(led_config_frame, bg='white')
        led_row3.pack(fill=tk.X, padx=10, pady=3)

        tk.Label(led_row3, text="Jasność:", font=('Arial', 9), bg='white').pack(side=tk.LEFT, padx=3)

        self.led_brightness_var = tk.IntVar(value=100)
        self.led_brightness_scale = tk.Scale(led_row3, from_=0, to=100, orient=tk.HORIZONTAL,
                                             variable=self.led_brightness_var, length=150,
                                             command=self.led_set_brightness)
        self.led_brightness_scale.pack(side=tk.LEFT, padx=5)

        tk.Label(led_row3, textvariable=self.led_brightness_var, font=('Arial', 9), bg='white').pack(side=tk.LEFT)
        tk.Label(led_row3, text="%", font=('Arial', 9), bg='white').pack(side=tk.LEFT)

        # === KONTROLA BIEGU ===
        race_frame = tk.LabelFrame(main_frame, text=" 🏃 KONTROLA BIEGU ",
                                   font=('Arial', 9, 'bold'), bg='white',
                                   relief=tk.RIDGE, bd=2)
        race_frame.pack(fill=tk.X, padx=10, pady=5)

        race_buttons = tk.Frame(race_frame, bg='white')
        race_buttons.pack(pady=10)

        self.start_btn = tk.Button(race_buttons, text="▶ START BIEGU",
                                   command=self.la_manual_start,
                                   font=('Arial', 12, 'bold'), bg='#27ae60', fg='white',
                                   width=15, height=2)
        self.start_btn.grid(row=0, column=0, padx=5)

        self.finish_btn = tk.Button(race_buttons, text="🏁 META (zapisz czas)",
                                    command=self.la_manual_finish,
                                    font=('Arial', 12, 'bold'), bg='#e74c3c', fg='white',
                                    width=18, height=2, state=tk.DISABLED)
        self.finish_btn.grid(row=0, column=1, padx=5)

        self.ranking_btn = tk.Button(race_buttons, text="📊 RANKING",
                                     command=self.led_show_ranking,
                                     font=('Arial', 12, 'bold'), bg='#9b59b6', fg='white',
                                     width=12, height=2)
        self.ranking_btn.grid(row=1, column=0, padx=5, pady=5)

        self.clear_btn = tk.Button(race_buttons, text="🧹 WYCZYŚĆ",
                                   command=self.la_reset_race,
                                   font=('Arial', 12, 'bold'), bg='#95a5a6', fg='white',
                                   width=12, height=2)
        self.clear_btn.grid(row=1, column=1, padx=5, pady=5)

        # Timer display
        self.timer_label = tk.Label(main_frame, text="00:00.000",
                                    font=('Courier', 48, 'bold'), bg='white', fg='#3498db')
        self.timer_label.pack(pady=20)

        # === WYNIKI ===
        results_frame = tk.LabelFrame(main_frame, text=" 🏆 WYNIKI ",
                                     font=('Arial', 9, 'bold'), bg='white',
                                     relief=tk.RIDGE, bd=2)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        scrollbar = tk.Scrollbar(results_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.results_listbox = tk.Listbox(results_frame,
                                          font=('Courier', 11),
                                          yscrollcommand=scrollbar.set)
        self.results_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.results_listbox.yview)

    # ========================================================================
    # METODY LED
    # ========================================================================

    def led_connect(self):
        """Połączenie/rozłączenie z tablicą LED"""
        port = self.led_port_var.get()
        if not port:
            messagebox.showwarning("Błąd", "Podaj port LED!")
            return

        if self.led_enabled:
            # Rozłącz
            if self.led_manager:
                self.led_manager.shutdown()
                self.led_manager = None
            self.led_enabled = False
            self.led_status_label.config(text="● Rozłączone", fg='red')
            self.led_connect_btn.config(text="🔌 Połącz LED", bg='#2196F3')
            print("🔴 [LED] Rozłączono tablicę LED")
        else:
            # Połącz
            try:
                self.led_manager = LEDDisplayManager(port, 9600)
                if self.led_manager.initialize():
                    self.led_enabled = True
                    self.led_num_lanes = self.led_lanes_var.get()
                    self.led_brightness = self.led_brightness_var.get()
                    self.led_status_label.config(text="● Połączone", fg='green')
                    self.led_connect_btn.config(text="🔌 Rozłącz LED", bg='#f44336')
                    print(f"✅ [LED] Połączono tablicę LED na {port}")

                    # Ustaw jasność
                    self.led_manager.display.set_brightness(self.led_brightness)
                else:
                    messagebox.showerror("Błąd", f"Nie udało się połączyć z tablicą LED na {port}")
                    self.led_manager = None
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie udało się połączyć z tablicą LED:\n{e}")
                self.led_manager = None

    def led_set_brightness(self, value):
        """Ustawienie jasności tablicy LED"""
        if self.led_enabled and self.led_manager:
            brightness = int(value)
            self.led_manager.display.set_brightness(brightness)

    def led_update_timer_worker(self):
        """Wątek aktualizacji timera na tablicy LED"""
        while self.led_timer_running and self.la_start_absolute_time:
            elapsed = time.time() - self.la_start_absolute_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            milliseconds = int((elapsed % 1) * 1000)

            time_str = f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

            # Wyślij na tablicę
            num_lanes = self.led_lanes_var.get()

            if num_lanes == 1:
                # Jedna linia
                packet = create_time_packet_line1(time_str)
                self.led_manager.display.send_packet(packet, delay=0)
            else:
                # Dwie linie - ten sam czas na obu
                packet1 = create_time_packet_line1(time_str)
                packet2 = create_time_packet_line2(time_str)
                self.led_manager.display.send_packet(packet1, delay=0)
                time.sleep(0.05)
                self.led_manager.display.send_packet(packet2, delay=0)

            time.sleep(0.1)  # Aktualizacja co 100ms

    def led_start_timer(self):
        """Uruchomienie timera na tablicy LED"""
        if not self.led_enabled or not self.led_manager:
            return

        # Zatrzymaj poprzedni timer jeśli był
        self.led_stop_timer()

        # Uruchom nowy wątek
        self.led_timer_running = True
        self.led_timer_thread = threading.Thread(target=self.led_update_timer_worker, daemon=True)
        self.led_timer_thread.start()
        print("⏱️ [LED] Timer uruchomiony na tablicy")

    def led_stop_timer(self):
        """Zatrzymanie timera na tablicy LED"""
        self.led_timer_running = False
        if self.led_timer_thread and self.led_timer_thread.is_alive():
            self.led_timer_thread.join(timeout=1)
        print("⏹️ [LED] Timer zatrzymany na tablicy")

    def led_show_ranking(self):
        """Wyświetlenie rankingu na tablicy LED"""
        if not self.led_enabled or not self.led_manager:
            messagebox.showwarning("Uwaga", "Tablica LED nie jest połączona!")
            return

        if not self.la_results:
            print("⚠️ [LED] Brak wyników do rankingu")
            messagebox.showinfo("Info", "Brak wyników do wyświetlenia!")
            return

        # Posortuj wyniki
        sorted_results = sorted(self.la_results)

        # Przygotuj dane rankingu
        results = []
        for i, time_val in enumerate(sorted_results, 1):
            minutes = int(time_val // 60)
            seconds = time_val % 60
            time_str = f"{minutes:02d}:{seconds:06.3f}"
            results.append({
                'lane': i,
                'time': time_str,
                'place': i
            })

        # Uruchom rotację rankingu
        race_data = {
            'race_number': self.la_race_number,
            'lanes': len(results),
            'results': results
        }

        self.led_manager.update_race_results(race_data)
        print(f"🏆 [LED] Uruchomiono ranking ({len(results)} zawodników)")

    def led_clear(self):
        """Czyszczenie tablicy LED"""
        if self.led_enabled and self.led_manager:
            self.led_manager.stop_rotation()
            self.led_manager.display.clear_display()
            print("🧹 [LED] Wyczyszczono tablicę")

    # ========================================================================
    # METODY CHRONOMETRU
    # ========================================================================

    def update_timer_display(self):
        """Aktualizacja wyświetlacza czasu w GUI"""
        if self.la_race_active and self.la_start_absolute_time:
            elapsed = time.time() - self.la_start_absolute_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            milliseconds = int((elapsed % 1) * 1000)

            time_str = f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
            self.timer_label.config(text=time_str, fg='#27ae60')

            self.root.after(50, self.update_timer_display)

    def la_next_race(self):
        """Przejście do następnego biegu"""
        # LED: Wyczyść tablicę
        self.led_clear()

        self.la_race_number += 1
        print(f"➡️ Następny bieg: #{self.la_race_number}")

    def la_manual_start(self):
        """Manualny start biegu"""
        if self.la_race_active:
            messagebox.showwarning("Uwaga", "Bieg już trwa!")
            return

        # LED: Wyczyść tablicę
        self.led_clear()

        # Start biegu
        self.la_race_active = True
        self.la_start_absolute_time = time.time()
        self.start_btn.config(state=tk.DISABLED)
        self.finish_btn.config(state=tk.NORMAL)

        print(f"🏁 START biegu #{self.la_race_number}")

        # LED: Uruchom timer
        self.led_start_timer()

        # Aktualizacja GUI
        self.update_timer_display()

    def la_manual_finish(self):
        """Manualny zapis czasu (META)"""
        if not self.la_race_active:
            return

        # Oblicz czas
        finish_time = time.time() - self.la_start_absolute_time
        self.la_results.append(finish_time)

        # Formatuj i wyświetl
        minutes = int(finish_time // 60)
        seconds = finish_time % 60
        time_str = f"{minutes:02d}:{seconds:06.3f}"

        miejsce = len(self.la_results)
        self.results_listbox.insert(tk.END, f"  {miejsce}. {time_str}")
        self.results_listbox.see(tk.END)

        print(f"🏁 META #{miejsce}: {time_str}")

    def process_la_crossing(self, channel):
        """
        Przetworzenie przejścia przez linię (dla fotokomórek)

        Args:
            channel: Numer kanału (1 = START, 2+ = META)
        """
        if channel == 1:
            # START
            if not self.la_race_active:
                self.la_race_active = True
                self.la_start_absolute_time = time.time()
                print(f"🏁 START biegu #{self.la_race_number}")

                # LED: Uruchom timer
                self.led_start_timer()

                self.update_timer_display()
        else:
            # META
            if self.la_race_active and self.la_start_absolute_time:
                finish_time = time.time() - self.la_start_absolute_time
                self.la_results.append(finish_time)

                minutes = int(finish_time // 60)
                seconds = finish_time % 60
                time_str = f"{minutes:02d}:{seconds:06.3f}"

                miejsce = len(self.la_results)
                print(f"🏁 META #{miejsce}: {time_str}")

                # Sprawdź czy wszyscy zawodnicy skończyli
                # (Tutaj można dodać logikę sprawdzania liczby zawodników)
                # Dla przykładu - po ostatnim zawodniku:
                if True:  # Warunek - ostatni zawodnik
                    self.led_stop_timer()
                    time.sleep(0.5)
                    self.led_show_ranking()

    def la_reset_race(self):
        """Reset biegu"""
        # LED: Wyczyść tablicę i zatrzymaj timer
        self.led_stop_timer()
        self.led_clear()

        # Reset zmiennych
        self.la_race_active = False
        self.la_start_absolute_time = None
        self.la_results.clear()
        self.la_race_number += 1

        # Reset GUI
        self.timer_label.config(text="00:00.000", fg='#3498db')
        self.start_btn.config(state=tk.NORMAL)
        self.finish_btn.config(state=tk.DISABLED)
        self.results_listbox.delete(0, tk.END)

        print(f"↻ RESET - Gotowy do biegu #{self.la_race_number}")


# ============================================================================
# URUCHOMIENIE PROGRAMU
# ============================================================================

def main():
    """Główna funkcja uruchamiająca aplikację"""
    root = tk.Tk()
    app = ChronometerManager(root)
    root.mainloop()


if __name__ == "__main__":
    main()
