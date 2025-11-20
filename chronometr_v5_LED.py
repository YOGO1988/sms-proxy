#!/usr/bin/env python3
"""
CHRONOMETR MANAGER v5.0 + TABLICA LED - KOMPLETNA INTEGRACJA
OSF + LA (Lekkoatletyka) z pełną funkcjonalnością + WYŚWIETLACZ LED

=== WERSJA 5.0 + LED ===

✅ WSZYSTKIE FUNKCJE OSF + LA
✅ TABLICA LED - automatyczne wyświetlanie wyników
✅ Konfiguracja portu LED przez GUI
✅ Ustawianie jasności LED
✅ Tryb rankingowy z rotacją dla 3+ zawodników
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import serial
import serial.tools.list_ports
import threading
import queue
import csv
from datetime import datetime
from enum import Enum
import time

# ============================================================================
# OBSŁUGA TABLICY LED - FUNKCJE I KLASY
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


def create_time_packet_line1(time_str: str, add_dash: bool = False) -> bytes:
    """
    Pakiet czasu dla linii 1
    Args:
        time_str: Czas w formacie "MM:SS.mmm"
        add_dash: Czy dodać myślnik na końcu (domyślnie False)
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

    # Dodaj myślnik tylko jeśli add_dash=True
    suffix = "  - " if add_dash else "  "
    text_padded = (formatted + suffix).ljust(34)[:34]
    base[22:56] = text_padded.encode('ascii', errors='replace')

    base[4] = 0
    base[5] = 0
    crc = calculate_crc16(bytes(base))
    base[4] = crc & 0xFF
    base[5] = (crc >> 8) & 0xFF

    return bytes(base)


def create_time_packet_line2(time_str: str, add_dash: bool = False) -> bytes:
    """
    Pakiet czasu dla linii 2
    Args:
        time_str: Czas w formacie "MM:SS.mmm"
        add_dash: Czy dodać myślnik na końcu (domyślnie False)
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

    # Dodaj myślnik tylko jeśli add_dash=True
    suffix = "  - " if add_dash else "  "
    text_padded = (formatted + suffix).ljust(34)[:34]
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
            print(f"✅ LED: Połączono z {self.port}")
            return True
        except Exception as e:
            print(f"❌ LED: Błąd połączenia - {e}")
            self.connected = False
            return False

    def disconnect(self):
        """Rozłączenie z tablicą LED"""
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.connected = False
        print("✅ LED: Rozłączono")

    def send_packet(self, packet_data, delay=0.1):
        """Wysłanie pakietu do tablicy"""
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
            print(f"❌ LED: Błąd wysyłania - {e}")
            return False

    def set_brightness(self, brightness: int):
        """Ustawienie jasności tablicy (0-100%)"""
        brightness = max(0, min(100, brightness))

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
            print(f"💡 LED: Jasność {brightness}% (poziom {level}/15)")

        return result

    def clear_display(self):
        """Czyszczenie obu linii tablicy"""
        self.send_packet('clear_line1')
        time.sleep(0.05)
        self.send_packet('clear_line2')
        return True

    def show_event_name(self):
        """Wyświetlenie nazwy wydarzenia"""
        return self.send_packet('name_event')


class LEDDisplayManager:
    """
    Manager do obsługi wyświetlacza w kontekście zawodów
    Obsługuje rotację wyników i tryby 1/2/3+ zawodników
    """

    def __init__(self, port='COM5', baudrate=9600):
        self.display = LEDDisplay(port, baudrate)
        self.rotation_thread = None
        self.rotation_active = False

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

    def _rotation_worker_ranking(self, results):
        """
        Worker rotacji rankingu
        Wyświetla pary wyników: 1-2, 3-4, 5-6, itd.
        """
        print(f"🔄 LED: Tryb rankingowy - {len(results)} zawodników")

        self.display.clear_display()
        time.sleep(0.2)

        index = 0
        while self.rotation_active:
            para = results[index:index+2]

            if len(para) == 1:
                miejsce = index + 1
                czas = para[0]['time']
                pakiet = create_ranking_packet(czas, miejsce, line=1)
                self.display.send_packet(pakiet)
                time.sleep(0.05)
                self.display.send_packet('clear_line2')

            elif len(para) == 2:
                miejsce1 = index + 1
                miejsce2 = index + 2
                czas1 = para[0]['time']
                czas2 = para[1]['time']

                print(f"  📊 LED: Miejsca {miejsce1}-{miejsce2}")

                pakiet1 = create_ranking_packet(czas1, miejsce1, line=1)
                self.display.send_packet(pakiet1)
                time.sleep(0.05)

                pakiet2 = create_ranking_packet(czas2, miejsce2, line=2)
                self.display.send_packet(pakiet2)

            time.sleep(3.0)

            index += 2
            if index >= len(results):
                index = 0
                print("  🔄 LED: Powrót do początku rotacji")

    def update_race_results(self, race_data):
        """
        Aktualizacja wyników biegu na tablicy
        Args:
            race_data: {
                'results': [
                    {'time': '00:07.787', 'place': 1},
                    {'time': '00:10.362', 'place': 2},
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
                print(f"📺 LED: Wyświetlono 1. miejsce: {results[0]['time']}")
            else:
                pakiet1 = create_ranking_packet(results[0]['time'], 1, line=1)
                self.display.send_packet(pakiet1)
                time.sleep(0.05)
                pakiet2 = create_ranking_packet(results[1]['time'], 2, line=2)
                self.display.send_packet(pakiet2)
                print(f"📺 LED: Wyświetlono 2 miejsca: {results[0]['time']}, {results[1]['time']}")
        else:
            # Z rotacją
            print(f"📺 LED: Start rotacji ({len(results)} zawodników)")
            self.rotation_active = True
            self.rotation_thread = threading.Thread(
                target=self._rotation_worker_ranking,
                args=(results,),
                daemon=True
            )
            self.rotation_thread.start()


# ============================================================================
# KLASY CHRONOMETRU (ORYGINALNE)
# ============================================================================

class MeasurementMode(Enum):
    """Tryby pomiaru OSF"""
    POJEDYNCZY = "POJEDYNCZY (Start-Meta)"
    OSF_DWA_TORY = "OSF - DWA TORY"
    OSF_DRUZYNA = "OSF DRUŻYNA (5 zawodników)"
    WACHADLO = "WACHADŁO (13 przecięć)"

class TimeFormat(Enum):
    """Formaty wyświetlania czasu"""
    THOUSANDTHS = ("Tysięczne (0.001s)", 3)
    HUNDREDTHS = ("Setne (0.01s)", 2)
    TENTHS = ("Dziesiąte (0.1s)", 1)
    SECONDS = ("Sekundy (1s)", 0)

class ChronometerManager:
    def __init__(self, root):
        self.root = root
        self.root.title("🏃 YO&GO Chronometr v5.0 + LED")
        self.root.geometry("1150x720")
        self.root.configure(bg='#f0f0f0')

        # PEŁNE LOGOWANIE DO PLIKU
        self.log_file = open('chronometr_RAW_LOG.txt', 'a', encoding='utf-8')
        self.log_file.write(f"\n{'='*80}\n")
        self.log_file.write(f"START LOGOWANIA: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.log_file.write(f"{'='*80}\n")

        # LOGOWANIE LA
        self.la_log_filename = f"LA_wyniki_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.la_log_file = None

        # ==============================
        # ZMIENNE LED
        # ==============================
        self.led_manager = None
        self.led_enabled = False
        self.led_port = 'COM6'
        self.led_brightness = 100

        # Zmienne chronometru
        self.serial_port = None
        self.serial_thread = None
        self.running = False
        self.data_queue = queue.Queue()

        # Dane pomiarowe OSF
        self.current_mode = MeasurementMode.POJEDYNCZY
        self.race_number = 0
        self.measurements = []

        # Format czasu
        self.time_format = TimeFormat.HUNDREDTHS

        # Stany pomiarów OSF
        self.start_time = None
        self.start_absolute_time = None
        self.left_lane_crossings = []
        self.right_lane_crossings = []

        # WSZYSTKIE PRZECIĘCIA OSF
        self.osf_all_left_crossings = []
        self.osf_all_right_crossings = []

        # KONTROLA STARTU OSF
        self.ready_for_start = True
        self.race_in_progress = False
        self.race_completed = False

        # Wyniki OSF
        self.left_lane_result = None
        self.right_lane_result = None
        self.left_lane_finished = False
        self.right_lane_finished = False

        # Live timer
        self.timer_running = False

        # STATUS TRACKING
        self.last_status_state = None
        self.pending_reset_id = None

        # BUFOR ODCZYTÓW
        self.last_crossing_time = {1: 0, 3: 0, 4: 0}
        self.debounce_interval = 0.8

        # ==============================
        # ZMIENNE DLA TRYBU LA
        # ==============================
        self.la_mode = False
        self.la_num_athletes = 2
        self.la_finish_channel = 4
        self.la_time_block = False
        self.la_race_active = False
        self.la_start_time = None
        self.la_start_absolute_time = None
        self.la_results = []
        self.la_all_crossings = []
        self.la_pending_results = []
        self.la_race_number = 0
        self.la_measurements = []

        # GUI
        self.setup_gui()

        # Timery
        self.check_queue()
        self.update_live_timer()
        self.update_status_indicator()

    def setup_gui(self):
        """Główny GUI z zakładkami"""

        # === GÓRNY PANEL (wspólny dla obu zakładek) ===
        top_frame = tk.Frame(self.root, bg='#e8e8e8', relief=tk.RAISED, bd=2)
        top_frame.pack(fill=tk.X, padx=5, pady=3)

        tk.Label(top_frame, text="Port:", font=('Arial', 9), bg='#e8e8e8').pack(side=tk.LEFT, padx=3)

        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(top_frame, textvariable=self.port_var, width=10, state='readonly', font=('Arial', 9))
        self.port_combo.pack(side=tk.LEFT, padx=3)

        self.refresh_btn = tk.Button(top_frame, text="🔄", command=self.refresh_ports,
                                     font=('Arial', 9), bg='#d0d0d0', width=3)
        self.refresh_btn.pack(side=tk.LEFT, padx=2)

        self.connect_btn = tk.Button(top_frame, text="POŁĄCZ", command=self.toggle_connection,
                                     font=('Arial', 9, 'bold'), bg='#4CAF50', fg='white', padx=10)
        self.connect_btn.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(top_frame, text="● ROZŁĄCZONY", font=('Arial', 9, 'bold'),
                                     fg='red', bg='#e8e8e8')
        self.status_label.pack(side=tk.LEFT, padx=10)

        # === PANEL LED (nowy!) ===
        tk.Label(top_frame, text="|", font=('Arial', 12), bg='#e8e8e8', fg='#ccc').pack(side=tk.LEFT, padx=10)

        tk.Label(top_frame, text="LED:", font=('Arial', 9, 'bold'), bg='#e8e8e8').pack(side=tk.LEFT, padx=3)

        self.led_port_var = tk.StringVar(value=self.led_port)
        self.led_port_combo = ttk.Combobox(top_frame, textvariable=self.led_port_var, width=8, state='readonly', font=('Arial', 9))
        self.led_port_combo.pack(side=tk.LEFT, padx=3)

        self.led_connect_btn = tk.Button(top_frame, text="WŁ", command=self.toggle_led,
                                         font=('Arial', 9, 'bold'), bg='#FF9800', fg='white', width=4)
        self.led_connect_btn.pack(side=tk.LEFT, padx=3)

        self.led_status_label = tk.Label(top_frame, text="○", font=('Arial', 9, 'bold'),
                                         fg='gray', bg='#e8e8e8')
        self.led_status_label.pack(side=tk.LEFT, padx=3)

        tk.Label(top_frame, text="Jasność:", font=('Arial', 8), bg='#e8e8e8').pack(side=tk.LEFT, padx=3)

        self.led_brightness_var = tk.IntVar(value=100)
        self.led_brightness_scale = tk.Scale(top_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                             variable=self.led_brightness_var, command=self.on_led_brightness_change,
                                             length=80, width=10, bg='#e8e8e8')
        self.led_brightness_scale.pack(side=tk.LEFT, padx=3)

        # === POLE TEKSTOWE STATYCZNE ===
        tk.Label(top_frame, text="Linia 1:", font=('Arial', 8), bg='#e8e8e8').pack(side=tk.LEFT, padx=(10, 3))

        self.led_text_var = tk.StringVar()
        self.led_text_entry = tk.Entry(top_frame, textvariable=self.led_text_var, font=('Arial', 9), width=15)
        self.led_text_entry.pack(side=tk.LEFT, padx=3)

        tk.Label(top_frame, text="Linia 2:", font=('Arial', 8), bg='#e8e8e8').pack(side=tk.LEFT, padx=(5, 3))

        self.led_text_var2 = tk.StringVar()
        self.led_text_entry2 = tk.Entry(top_frame, textvariable=self.led_text_var2, font=('Arial', 9), width=15)
        self.led_text_entry2.pack(side=tk.LEFT, padx=3)

        self.led_send_btn = tk.Button(top_frame, text="Wyślij", command=self.send_custom_text,
                                      font=('Arial', 8), bg='#2196F3', fg='white', padx=8)
        self.led_send_btn.pack(side=tk.LEFT, padx=3)

        # === NOTEBOOK (ZAKŁADKI) ===
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Zakładka 1: OSF
        self.osf_tab = tk.Frame(self.notebook, bg='#f0f0f0')
        self.notebook.add(self.osf_tab, text=" OSF - Zawody ")

        # Zakładka 2: LA
        self.la_tab = tk.Frame(self.notebook, bg='#f0f0f0')
        self.notebook.add(self.la_tab, text=" LA - Lekkoatletyka ")

        # Bind do zmiany zakładki
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_change)

        # Setup zakładek
        self.setup_osf_tab()
        self.setup_la_tab()

        # Inicjalizacja
        self.refresh_ports()
        self.refresh_led_ports()

    def refresh_led_ports(self):
        """Odświeżanie listy portów dla LED"""
        ports = serial.tools.list_ports.comports()
        port_list = [port.device for port in ports]
        self.led_port_combo['values'] = port_list
        if self.led_port in port_list:
            self.led_port_var.set(self.led_port)
        elif port_list:
            self.led_port_combo.current(0)

    def toggle_led(self):
        """Włącz/Wyłącz tablicę LED"""
        if not self.led_enabled:
            # Włącz LED
            self.led_port = self.led_port_var.get()
            if not self.led_port:
                messagebox.showwarning("Brak portu", "Wybierz port dla tablicy LED!")
                return

            self.led_manager = LEDDisplayManager(port=self.led_port, baudrate=9600)

            if self.led_manager.initialize():
                self.led_enabled = True
                self.led_connect_btn.config(text="WYŁ", bg='#4CAF50')
                self.led_status_label.config(text="●", fg='green')
                messagebox.showinfo("LED", f"Tablica LED połączona na {self.led_port}")

                # Ustaw jasność
                self.led_manager.display.set_brightness(self.led_brightness)
            else:
                messagebox.showerror("LED", "Nie udało się połączyć z tablicą LED!")
                self.led_manager = None
        else:
            # Wyłącz LED
            if self.led_manager:
                self.led_manager.shutdown()
                self.led_manager = None

            self.led_enabled = False
            self.led_connect_btn.config(text="WŁ", bg='#FF9800')
            self.led_status_label.config(text="○", fg='gray')
            messagebox.showinfo("LED", "Tablica LED rozłączona")

    def on_led_brightness_change(self, value):
        """Zmiana jasności LED"""
        self.led_brightness = int(value)
        if self.led_enabled and self.led_manager:
            self.led_manager.display.set_brightness(self.led_brightness)

    def send_custom_text(self):
        """Wysyła własny tekst na tablicę LED"""
        if not self.led_enabled or not self.led_manager:
            messagebox.showwarning("LED", "Tablica LED nie jest podłączona!")
            return

        text1 = self.led_text_var.get().strip()
        text2 = self.led_text_var2.get().strip()

        if not text1 and not text2:
            messagebox.showwarning("Brak tekstu", "Wpisz tekst do wysłania (przynajmniej jedna linia)!")
            return

        try:
            # Zatrzymaj rotację jeśli jest aktywna
            self.led_manager.stop_rotation()

            # Wyślij tekst na linię 1
            if text1:
                packet1 = create_time_packet_line1(text1)
                self.led_manager.display.send_packet(packet1, delay=0.1)  # Zwiększone opóźnienie
            else:
                # Jeśli puste, wyczyść linię 1
                self.led_manager.display.send_packet('clear_line1', delay=0.1)

            # Wyślij tekst na linię 2
            if text2:
                packet2 = create_time_packet_line2(text2)
                self.led_manager.display.send_packet(packet2, delay=0.1)  # Zwiększone opóźnienie
            else:
                # Jeśli puste, wyczyść linię 2
                self.led_manager.display.send_packet('clear_line2', delay=0.1)

            print(f"📺 LED: Wysłano tekst statyczny - Linia 1: '{text1}', Linia 2: '{text2}'")
            messagebox.showinfo("LED", f"Wysłano tekst:\nLinia 1: {text1 or '(puste)'}\nLinia 2: {text2 or '(puste)'}")

        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wysłać tekstu:\n{e}")

    def setup_osf_tab(self):
        """Zakładka OSF - interfejs użytkownika"""

        # DUŻY WSKAŹNIK STATUSU BIEGU
        status_frame = tk.Frame(self.osf_tab, bg='#f0f0f0')
        status_frame.pack(fill=tk.X, pady=3)

        self.race_status_label = tk.Label(status_frame, text="✅ GOTOWY",
                                         font=('Arial', 14, 'bold'),
                                         fg='white', bg='green',
                                         padx=15, pady=3, relief=tk.RAISED, bd=3)
        self.race_status_label.pack(pady=5)

        # === KONFIGURACJA ===
        config_frame = tk.Frame(self.osf_tab, bg='#e8e8e8', relief=tk.RAISED, bd=2)
        config_frame.pack(fill=tk.X, padx=5, pady=3)

        tk.Label(config_frame, text="Tryb:", font=('Arial', 9, 'bold'), bg='#e8e8e8').pack(side=tk.LEFT, padx=3)

        self.mode_var = tk.StringVar(value=MeasurementMode.POJEDYNCZY.value)
        self.mode_combo = ttk.Combobox(
            config_frame,
            textvariable=self.mode_var,
            values=[mode.value for mode in MeasurementMode],
            width=28,
            state='readonly',
            font=('Arial', 9)
        )
        self.mode_combo.pack(side=tk.LEFT, padx=3)
        self.mode_combo.bind('<<ComboboxSelected>>', self.on_mode_change)

        tk.Label(config_frame, text="Dokładność:", font=('Arial', 9, 'bold'), bg='#e8e8e8').pack(side=tk.LEFT, padx=(15, 3))

        self.format_var = tk.StringVar(value=TimeFormat.HUNDREDTHS.value[0])
        self.format_combo = ttk.Combobox(
            config_frame,
            textvariable=self.format_var,
            values=[fmt.value[0] for fmt in TimeFormat],
            width=18,
            state='readonly',
            font=('Arial', 9)
        )
        self.format_combo.pack(side=tk.LEFT, padx=3)
        self.format_combo.bind('<<ComboboxSelected>>', self.on_format_change)

        # Blokada czasów OSF
        self.osf_block_var = tk.BooleanVar(value=False)
        self.osf_block_check = tk.Checkbutton(config_frame,
                                              text="🚫 Blokada odczytów",
                                              variable=self.osf_block_var,
                                              font=('Arial', 9, 'bold'),
                                              bg='#e8e8e8',
                                              activebackground='#e8e8e8')
        self.osf_block_check.pack(side=tk.RIGHT, padx=10)

        # === AKTUALNY POMIAR ===
        display_frame = tk.LabelFrame(self.osf_tab, text=" 📊 AKTUALNY POMIAR ",
                                      font=('Arial', 10, 'bold'), bg='white',
                                      relief=tk.RIDGE, bd=2)
        display_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=3)

        # Kontener dla licznika i statusu
        timer_container = tk.Frame(display_frame, bg='white', height=120)
        timer_container.pack(fill=tk.X, pady=5)
        timer_container.pack_propagate(False)

        # Live licznik
        self.timer_label = tk.Label(timer_container, text="00:00.00",
                                    font=('Courier New', 36, 'bold'),
                                    fg='#2196F3', bg='white')
        self.timer_label.place(relx=0.5, rely=0.5, anchor='center')

        # OGROMNY STATUS NIE GOTOWY
        self.big_status_label = tk.Label(timer_container, text="❌ NIE GOTOWY\n\nKliknij KOLEJNY BIEG",
                                        font=('Arial', 24, 'bold'),
                                        fg='white', bg='red',
                                        relief=tk.RAISED, bd=5)

        # Status display
        self.display_text = tk.Text(display_frame, height=4, font=('Arial', 11),
                                   state='disabled', bg='#f9f9f9', relief=tk.FLAT, wrap=tk.WORD)
        self.display_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=3)

        # Przyciski
        action_frame = tk.Frame(display_frame, bg='white')
        action_frame.pack(fill=tk.X, pady=8)

        self.next_race_btn = tk.Button(action_frame, text="▶️ KOLEJNY BIEG",
                                       command=self.next_race,
                                       font=('Arial', 11, 'bold'), bg='#4CAF50',
                                       fg='white', padx=20, pady=8,
                                       state='disabled')
        self.next_race_btn.pack(side=tk.LEFT, padx=8)

        self.reset_btn = tk.Button(action_frame, text="🔄 RESET (DNF/DSQ)",
                                  command=self.reset_measurement,
                                  font=('Arial', 10), bg='#ff9800', fg='white',
                                  padx=15, pady=8)
        self.reset_btn.pack(side=tk.LEFT, padx=8)

        # Przyciski ręczne (mniejsze, drugorzędne)
        manual_frame = tk.Frame(display_frame, bg='white')
        manual_frame.pack(fill=tk.X, pady=2)

        self.osf_manual_start_btn = tk.Button(manual_frame, text="🖐️ START RĘCZNY",
                                              command=self.osf_manual_start,
                                              font=('Arial', 8), bg='#9C27B0',
                                              fg='white', padx=10, pady=3)
        self.osf_manual_start_btn.pack(side=tk.LEFT, padx=5)

        self.osf_manual_finish_btn = tk.Button(manual_frame, text="🖐️ META RĘCZNA",
                                               command=self.osf_manual_finish,
                                               font=('Arial', 8), bg='#9C27B0',
                                               fg='white', padx=10, pady=3,
                                               state='disabled')
        self.osf_manual_finish_btn.pack(side=tk.LEFT, padx=5)

        # === HISTORIA ===
        history_frame = tk.LabelFrame(self.osf_tab, text=" 📋 HISTORIA BIEGÓW ",
                                     font=('Arial', 10, 'bold'), bg='white',
                                     relief=tk.RIDGE, bd=2)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=3)

        columns = ('Bieg', 'Tryb', 'Tor', 'Czas', 'Godzina')
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=6)

        self.history_tree.heading('Bieg', text='Bieg')
        self.history_tree.heading('Tryb', text='Tryb')
        self.history_tree.heading('Tor', text='Tor')
        self.history_tree.heading('Czas', text='Czas [MM:SS]')
        self.history_tree.heading('Godzina', text='Godz')

        self.history_tree.column('Bieg', width=50)
        self.history_tree.column('Tryb', width=220)
        self.history_tree.column('Tor', width=100)
        self.history_tree.column('Czas', width=120)
        self.history_tree.column('Godzina', width=80)

        self.history_tree.tag_configure('race', background='#e3f2fd')

        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscroll=scrollbar.set)

        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # === ZARZĄDZANIE ODCZYTAMI ===
        manage_frame = tk.Frame(self.osf_tab, bg='#f0f0f0')
        manage_frame.pack(fill=tk.X, padx=5, pady=3)

        tk.Label(manage_frame, text="Zarządzanie odczytami:", font=('Arial', 9, 'bold'),
                bg='#f0f0f0').pack(side=tk.LEFT, padx=5)

        self.osf_delete_btn = tk.Button(manage_frame, text="🗑️ Usuń z historii",
                                        command=self.osf_delete_measurement,
                                        font=('Arial', 9), bg='#ff6b6b', fg='white', padx=8)
        self.osf_delete_btn.pack(side=tk.LEFT, padx=3)

        self.osf_manage_btn = tk.Button(manage_frame, text="📝 Zarządź odczytami",
                                        command=self.osf_manage_crossings,
                                        font=('Arial', 9), bg='#4ECDC4', fg='white', padx=8,
                                        state='disabled')
        self.osf_manage_btn.pack(side=tk.LEFT, padx=3)

        self.export_btn = tk.Button(manage_frame, text="💾 EKSPORT CSV",
                                    command=self.export_to_csv,
                                    font=('Arial', 9, 'bold'), bg='#2196F3',
                                    fg='white', padx=12, pady=4)
        self.export_btn.pack(side=tk.LEFT, padx=10)

        # === DOLNY PANEL ===
        bottom_frame = tk.Frame(self.osf_tab, bg='#e8e8e8', relief=tk.RAISED, bd=2)
        bottom_frame.pack(fill=tk.X, padx=5, pady=3)

        self.clear_btn = tk.Button(bottom_frame, text="🗑️ WYCZYŚĆ",
                                   command=self.clear_history,
                                   font=('Arial', 9), bg='#f44336', fg='white',
                                   padx=12, pady=4)
        self.clear_btn.pack(side=tk.LEFT, padx=3)

        tk.Label(bottom_frame, text="Biegi:", font=('Arial', 10, 'bold'), bg='#e8e8e8').pack(side=tk.LEFT, padx=(20, 3))
        self.count_label = tk.Label(bottom_frame, text="0", font=('Arial', 12, 'bold'), fg='#2196F3', bg='#e8e8e8')
        self.count_label.pack(side=tk.LEFT)

    def setup_la_tab(self):
        """Zakładka LA - Lekkoatletyka - interfejs użytkownika"""
        
        # === KONFIGURACJA ===
        config_frame = tk.LabelFrame(self.la_tab, text=" ⚙️ KONFIGURACJA ", 
                                    font=('Arial', 9, 'bold'), bg='white',
                                    relief=tk.RIDGE, bd=2)
        config_frame.pack(fill=tk.X, padx=10, pady=3)
        
        # Rząd 1: Liczba zawodników
        row1 = tk.Frame(config_frame, bg='white')
        row1.pack(fill=tk.X, padx=10, pady=3)
        
        tk.Label(row1, text="Zawodnicy:", font=('Arial', 10, 'bold'), bg='white').pack(side=tk.LEFT, padx=3)
        
        self.la_athletes_var = tk.IntVar(value=2)
        self.la_athletes_combo = ttk.Combobox(row1, textvariable=self.la_athletes_var, 
                                              values=list(range(2, 21)), width=4, state='readonly',
                                              font=('Arial', 10))
        self.la_athletes_combo.pack(side=tk.LEFT, padx=3)
        self.la_athletes_combo.bind('<<ComboboxSelected>>', self.on_la_config_change)
        
        tk.Label(row1, text="  Kanał mety: CZERWONY (4)", 
                font=('Arial', 9), bg='white', fg='#666').pack(side=tk.LEFT, padx=10)
        
        # Blokada czasów
        self.la_block_var = tk.BooleanVar(value=False)
        self.la_block_check = tk.Checkbutton(row1, 
                                            text="🚫 Blokada czasów",
                                            variable=self.la_block_var,
                                            command=self.on_la_block_change,
                                            font=('Arial', 9, 'bold'), 
                                            bg='white',
                                            activebackground='white')
        self.la_block_check.pack(side=tk.RIGHT, padx=10)
        
        # === STATUS BIEGU ===
        status_frame = tk.Frame(self.la_tab, bg='#f0f0f0')
        status_frame.pack(fill=tk.X, padx=10, pady=2)
        
        self.la_status_label = tk.Label(status_frame, text="✅ GOTOWY", 
                                       font=('Arial', 12, 'bold'),
                                       fg='white', bg='green', 
                                       padx=15, pady=3, relief=tk.RAISED, bd=3)
        self.la_status_label.pack(pady=2)
        
        # === LIVE TIMER LA ===
        la_timer_frame = tk.Frame(self.la_tab, bg='white', height=80)
        la_timer_frame.pack(fill=tk.X, padx=10, pady=2)
        la_timer_frame.pack_propagate(False)
        
        self.la_timer_label = tk.Label(la_timer_frame, text="00:00.00", 
                                       font=('Courier New', 28, 'bold'), 
                                       fg='#4CAF50', bg='white')
        self.la_timer_label.place(relx=0.5, rely=0.5, anchor='center')
        
        # === PRZYCISKI KONTROLI ===
        control_frame = tk.Frame(self.la_tab, bg='#f0f0f0')
        control_frame.pack(fill=tk.X, padx=10, pady=3)
        
        # Górny rząd
        btn_row1 = tk.Frame(control_frame, bg='#f0f0f0')
        btn_row1.pack(pady=2)
        
        self.la_next_btn = tk.Button(btn_row1, text="⏭️ KOLEJNY BIEG", 
                                     command=self.la_next_race,
                                     font=('Arial', 9, 'bold'), bg='#2196F3', 
                                     fg='white', padx=12, pady=4,
                                     state='normal')
        self.la_next_btn.pack(side=tk.LEFT, padx=3)
        
        self.la_reset_btn = tk.Button(btn_row1, text="🔄 RESET", 
                                      command=self.la_reset_race,
                                      font=('Arial', 9), bg='#ff9800', 
                                      fg='white', padx=12, pady=4)
        self.la_reset_btn.pack(side=tk.LEFT, padx=3)
        
        # Dolny rząd
        btn_row2 = tk.Frame(control_frame, bg='#f0f0f0')
        btn_row2.pack(pady=2)
        
        self.la_manual_start_btn = tk.Button(btn_row2, text="🖐️ START RĘCZNY", 
                                             command=self.la_manual_start,
                                             font=('Arial', 8), bg='#9C27B0', 
                                             fg='white', padx=10, pady=3)
        self.la_manual_start_btn.pack(side=tk.LEFT, padx=3)
        
        self.la_manual_finish_btn = tk.Button(btn_row2, text="🖐️ META RĘCZNA", 
                                              command=self.la_manual_finish,
                                              font=('Arial', 8), bg='#9C27B0', 
                                              fg='white', padx=10, pady=3,
                                              state='disabled')
        self.la_manual_finish_btn.pack(side=tk.LEFT, padx=3)
        
        self.la_manage_results_btn = tk.Button(btn_row2, text="📝 Zarządzaj odczytami", 
                                               command=self.la_manage_results,
                                               font=('Arial', 8), bg='#607D8B', 
                                               fg='white', padx=10, pady=3,
                                               state='disabled')
        self.la_manage_results_btn.pack(side=tk.LEFT, padx=3)
        
        # === CONTAINER DLA WYNIKÓW I HISTORII ===
        main_container = tk.Frame(self.la_tab, bg='#f0f0f0')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=3)
        
        # LEWA STRONA - WYNIKI
        results_frame = tk.LabelFrame(main_container, text=" 🏆 AKTUALNY BIEG ", 
                                     font=('Arial', 9, 'bold'), bg='white',
                                     relief=tk.RIDGE, bd=2, width=280)
        results_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))
        results_frame.pack_propagate(False)
        
        self.la_results_text = tk.Text(results_frame, height=8, font=('Courier New', 10, 'bold'),
                                      state='disabled', bg='#f9f9f9', relief=tk.FLAT)
        self.la_results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # PRAWA STRONA - HISTORIA
        la_history_frame = tk.LabelFrame(main_container, text=" 📋 HISTORIA BIEGÓW ", 
                                        font=('Arial', 9, 'bold'), bg='white',
                                        relief=tk.RIDGE, bd=2)
        la_history_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Ramka z przyciskiem
        hist_controls = tk.Frame(la_history_frame, bg='white')
        hist_controls.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Button(hist_controls, text="👁️ Pokaż szczegóły", 
                 command=self.la_show_details,
                 font=('Arial', 8), bg='#607D8B', fg='white', padx=8, pady=2).pack(side=tk.LEFT)
        
        # Tabela historii
        columns_la = ('Bieg', 'Zaw', 'Miejsce_1', 'Miejsce_2', 'Miejsce_3', 'Godz')
        self.la_history_tree = ttk.Treeview(la_history_frame, columns=columns_la, show='headings', height=8)
        
        self.la_history_tree.heading('Bieg', text='Bieg')
        self.la_history_tree.heading('Zaw', text='Zaw.')
        self.la_history_tree.heading('Miejsce_1', text='1. miejsce')
        self.la_history_tree.heading('Miejsce_2', text='2. miejsce')
        self.la_history_tree.heading('Miejsce_3', text='3. miejsce')
        self.la_history_tree.heading('Godz', text='Godz')
        
        self.la_history_tree.column('Bieg', width=40)
        self.la_history_tree.column('Zaw', width=35)
        self.la_history_tree.column('Miejsce_1', width=75)
        self.la_history_tree.column('Miejsce_2', width=75)
        self.la_history_tree.column('Miejsce_3', width=75)
        self.la_history_tree.column('Godz', width=60)
        
        self.la_history_tree.tag_configure('race', background='#e3f2fd')
        
        scrollbar_la = ttk.Scrollbar(la_history_frame, orient=tk.VERTICAL, command=self.la_history_tree.yview)
        self.la_history_tree.configure(yscroll=scrollbar_la.set)
        
        self.la_history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=2)
        scrollbar_la.pack(side=tk.RIGHT, fill=tk.Y)
        
        # === ZARZĄDZANIE ===
        la_manage_frame = tk.Frame(self.la_tab, bg='#f0f0f0')
        la_manage_frame.pack(fill=tk.X, padx=5, pady=3)
        
        tk.Label(la_manage_frame, text="Zarządzanie historią:", font=('Arial', 9, 'bold'), 
                bg='#f0f0f0').pack(side=tk.LEFT, padx=5)
        
        self.la_delete_btn = tk.Button(la_manage_frame, text="🗑️ Usuń bieg", 
                                        command=self.la_delete_race,
                                        font=('Arial', 9), bg='#ff6b6b', fg='white', padx=8)
        self.la_delete_btn.pack(side=tk.LEFT, padx=3)
        
        self.la_edit_btn = tk.Button(la_manage_frame, text="✏️ Edytuj czasy", 
                                      command=self.la_edit_race,
                                      font=('Arial', 9), bg='#4ECDC4', fg='white', padx=8)
        self.la_edit_btn.pack(side=tk.LEFT, padx=3)
        
        # === DOLNY PANEL ===
        la_bottom_frame = tk.Frame(self.la_tab, bg='#e8e8e8', relief=tk.RAISED, bd=2)
        la_bottom_frame.pack(fill=tk.X, padx=10, pady=3)
        
        self.la_save_btn = tk.Button(la_bottom_frame, text="💾 EKSPORT", 
                                     command=self.la_export_to_csv,
                                     font=('Arial', 9, 'bold'), bg='#2196F3', 
                                     fg='white', padx=12, pady=4,
                                     state='disabled')
        self.la_save_btn.pack(side=tk.LEFT, padx=3)
        
        self.la_clear_btn = tk.Button(la_bottom_frame, text="🗑️ WYCZYŚĆ", 
                                      command=self.la_clear_history,
                                      font=('Arial', 9), bg='#f44336', fg='white',
                                      padx=12, pady=4)
        self.la_clear_btn.pack(side=tk.LEFT, padx=3)
        
        tk.Label(la_bottom_frame, text="Biegi:", font=('Arial', 9, 'bold'), bg='#e8e8e8').pack(side=tk.LEFT, padx=(15, 3))
        self.la_count_label = tk.Label(la_bottom_frame, text="0", font=('Arial', 11, 'bold'), fg='#2196F3', bg='#e8e8e8')
        self.la_count_label.pack(side=tk.LEFT)
        
        # Inicjalizacja wyświetlania
        self.la_update_results_display()

    def on_tab_change(self, event):
        """Zmiana zakładki"""
        current_tab = self.notebook.index(self.notebook.select())
        if current_tab == 1:
            self.la_mode = True
        else:
            self.la_mode = False

    def on_la_config_change(self, event=None):
        """Zmiana konfiguracji LA"""
        self.la_num_athletes = self.la_athletes_var.get()
        self.la_update_results_display()

    def on_la_block_change(self):
        """Zmiana stanu blokady czasów"""
        if self.la_block_var.get():
            self.la_block_check.config(fg='red', selectcolor='red')
        else:
            self.la_block_check.config(fg='black', selectcolor='white')

    def la_update_results_display(self):
        """Aktualizacja wyświetlania wyników LA"""
        self.la_results_text.config(state='normal')
        self.la_results_text.delete(1.0, tk.END)
        
        self.la_results_text.insert(tk.END, "Nr  |  Czas [MM:SS.xx]\n")
        self.la_results_text.insert(tk.END, "=" * 30 + "\n\n")
        
        num_athletes = self.la_num_athletes
        for i in range(num_athletes):
            if i < len(self.la_results):
                time_str = self.format_time(self.la_results[i])
                self.la_results_text.insert(tk.END, f"{i+1:<3} |  {time_str}\n")
            else:
                self.la_results_text.insert(tk.END, f"{i+1:<3} |  ---.---\n")
        
        self.la_results_text.config(state='disabled')

    def la_reset_race(self):
        """RESET biegu LA"""
        if self.la_race_active:
            if not messagebox.askyesno("Reset", "Czy na pewno chcesz zresetować bieg?"):
                return
        
        self.la_results = []
        self.la_all_crossings = []
        self.la_race_active = False
        self.la_start_time = None
        self.la_start_absolute_time = None
        
        self.last_crossing_time = {1: 0, 3: 0, 4: 0}
        
        self.la_status_label.config(text="❌ NIE GOTOWY", bg='red')
        self.la_next_btn.config(state='normal')
        self.la_save_btn.config(state='disabled')
        self.la_manual_finish_btn.config(state='disabled')
        self.la_update_results_display()
        
        # Wyczyść LED
        if self.led_enabled and self.led_manager:
            self.led_manager.display.clear_display()

    def la_add_to_history(self):
        """Dodaj bieg LA do historii"""
        self.la_race_number += 1
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        measurement = {
            'race': self.la_race_number,
            'num_athletes': self.la_num_athletes,
            'times': self.la_results.copy(),
            'timestamp': timestamp
        }
        self.la_measurements.append(measurement)
        
        wynik_1 = self.format_time(self.la_results[0]) if len(self.la_results) > 0 else "-"
        wynik_2 = self.format_time(self.la_results[1]) if len(self.la_results) > 1 else "-"
        wynik_3 = self.format_time(self.la_results[2]) if len(self.la_results) > 2 else "-"
        
        self.la_history_tree.insert('', 0, values=(
            self.la_race_number,
            self.la_num_athletes,
            wynik_1,
            wynik_2,
            wynik_3,
            timestamp
        ), tags=('race',))
        
        self.la_count_label.config(text=str(self.la_race_number))
        self.la_save_btn.config(state='normal')
        
        # === INTEGRACJA LED DLA LA ===
        if self.led_enabled and self.led_manager:
            race_data = {
                'results': [
                    {'time': self.format_time(t), 'place': i+1} 
                    for i, t in enumerate(self.la_results)
                ]
            }
            self.led_manager.update_race_results(race_data)
            print(f"📺 LED: Wyświetlono wyniki LA - {len(self.la_results)} zawodników")

    def la_next_race(self):
        """KOLEJNY BIEG LA"""
        self.la_results = []
        self.la_all_crossings = []
        self.la_pending_results = []
        self.la_race_active = False
        self.la_start_time = None
        self.la_start_absolute_time = None

        self.last_crossing_time = {1: 0, 3: 0, 4: 0}

        self.la_status_label.config(text="✅ GOTOWY", bg='green')
        self.la_next_btn.config(state='disabled')
        self.la_manual_finish_btn.config(state='disabled')
        self.la_manage_results_btn.config(state='disabled')
        self.la_timer_label.config(text="00:00.00", fg='#4CAF50')
        self.la_update_results_display()

        # === ZATRZYMAJ ROTACJĘ RANKINGU I WYCZYŚĆ LED ===
        if self.led_enabled and self.led_manager:
            self.led_manager.stop_rotation()  # WAŻNE: zatrzymaj rotację PRZED czyszczeniem
            self.led_manager.display.clear_display()

        print("✅ [LA] KOLEJNY BIEG - gotowy")

    def la_manual_start(self):
        """START RĘCZNY LA"""
        if self.la_race_active:
            messagebox.showwarning("Uwaga", "Bieg już trwa!")
            return

        # === WYCZYŚĆ LED PRZY STARCIE ===
        if self.led_enabled and self.led_manager:
            self.led_manager.stop_rotation()
            self.led_manager.display.clear_display()

        if self.la_log_file is None:
            self.la_log_file = open(self.la_log_filename, 'a', encoding='utf-8')
            self.la_log_file.write(f"\n{'='*60}\n")
            self.la_log_file.write(f"BIEG LA - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.la_log_file.write(f"Liczba zawodników: {self.la_num_athletes}\n")
            self.la_log_file.write(f"{'='*60}\n")

        self.la_race_active = True
        self.la_start_time = None
        self.la_start_absolute_time = time.time()
        self.la_results = []
        self.la_all_crossings = []
        self.la_pending_results = []

        self.last_crossing_time = {1: 0, 3: 0, 4: 0}

        self.la_status_label.config(text="🏃 TRWA BIEG (RĘCZNY)", bg='orange')
        self.la_next_btn.config(state='disabled')
        self.la_manual_finish_btn.config(state='normal')
        self.la_manage_results_btn.config(state='normal')
        self.la_update_results_display()

        print("🖐️ [LA] START RĘCZNY")

    def la_manual_finish(self):
        """META RĘCZNA LA"""
        if not self.la_race_active:
            messagebox.showwarning("Uwaga", "Bieg nie trwa!")
            return
        
        if self.la_start_absolute_time is None:
            messagebox.showerror("Błąd", "Brak czasu startu!")
            return
        
        result_time = time.time() - self.la_start_absolute_time
        
        if len(self.la_results) < self.la_num_athletes:
            self.la_results.append(result_time)
            self.la_update_results_display()
            
            print(f"🖐️ [LA] META RĘCZNA #{len(self.la_results)}: {result_time:.3f}s")
            
            if len(self.la_results) == self.la_num_athletes:
                self.la_status_label.config(text="❌ NIE GOTOWY", bg='red')
                self.la_next_btn.config(state='normal')
                self.la_manual_finish_btn.config(state='disabled')
                self.la_add_to_history()
        else:
            messagebox.showinfo("Info", "Wszyscy zawodnicy już ukończyli bieg!")

    def la_manage_results(self):
        """Okno do zarządzania odczytami LA"""
        if not self.la_pending_results:
            messagebox.showinfo("Info", "Brak odczytów do zarządzania!")
            return
        
        manage_window = tk.Toplevel(self.root)
        manage_window.title("Zarządzanie odczytami LA")
        manage_window.geometry("600x500")
        manage_window.configure(bg='white')
        
        tk.Label(manage_window, text="📝 ZARZĄDZANIE ODCZYTAMI", 
                font=('Arial', 14, 'bold'), bg='white').pack(pady=10)
        
        tk.Label(manage_window, text=f"Zaakceptowanych: {len(self.la_results)}/{self.la_num_athletes}", 
                font=('Arial', 11), bg='white').pack(pady=5)
        
        tk.Label(manage_window, text=f"Wszystkich odczytów: {len(self.la_pending_results)}", 
                font=('Arial', 11), bg='white').pack(pady=5)
        
        lists_frame = tk.Frame(manage_window, bg='white')
        lists_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # LEWA STRONA
        left_frame = tk.LabelFrame(lists_frame, text="✅ Zaakceptowane", 
                                   font=('Arial', 10, 'bold'), bg='white')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        accepted_listbox = tk.Listbox(left_frame, font=('Courier New', 11), height=15)
        accepted_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        for i, time_val in enumerate(self.la_results, 1):
            accepted_listbox.insert(tk.END, f"{i}. {self.format_time(time_val)} s")
        
        def remove_accepted():
            selection = accepted_listbox.curselection()
            if selection:
                idx = selection[0]
                removed_time = self.la_results.pop(idx)
                self.la_update_results_display()
                print(f"🗑️ [LA] Usunięto: {self.format_time(removed_time)}")
                
                accepted_listbox.delete(0, tk.END)
                for i, time_val in enumerate(self.la_results, 1):
                    accepted_listbox.insert(tk.END, f"{i}. {self.format_time(time_val)} s")
                
                pending_listbox.delete(0, tk.END)
                for i, time_val in enumerate(self.la_pending_results, 1):
                    if time_val in self.la_results:
                        pending_listbox.insert(tk.END, f"{i}. {self.format_time(time_val)} s ✓")
                    else:
                        pending_listbox.insert(tk.END, f"{i}. {self.format_time(time_val)} s")
        
        tk.Button(left_frame, text="❌ Usuń zaznaczony", command=remove_accepted,
                 font=('Arial', 9), bg='#f44336', fg='white', padx=10, pady=5).pack(pady=5)
        
        # PRAWA STRONA
        right_frame = tk.LabelFrame(lists_frame, text="⏳ Wszystkie odczyty", 
                                    font=('Arial', 10, 'bold'), bg='white')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        pending_listbox = tk.Listbox(right_frame, font=('Courier New', 11), height=15)
        pending_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        for i, time_val in enumerate(self.la_pending_results, 1):
            if time_val in self.la_results:
                pending_listbox.insert(tk.END, f"{i}. {self.format_time(time_val)} s ✓")
            else:
                pending_listbox.insert(tk.END, f"{i}. {self.format_time(time_val)} s")
        
        def accept_pending():
            selection = pending_listbox.curselection()
            if selection:
                idx = selection[0]
                if len(self.la_results) < self.la_num_athletes:
                    time_val = self.la_pending_results[idx]
                    if time_val not in self.la_results:
                        self.la_results.append(time_val)
                        self.la_update_results_display()
                        
                        accepted_listbox.delete(0, tk.END)
                        for i, time_val_upd in enumerate(self.la_results, 1):
                            accepted_listbox.insert(tk.END, f"{i}. {self.format_time(time_val_upd)} s")
                        
                        pending_listbox.delete(0, tk.END)
                        for i, time_val_upd in enumerate(self.la_pending_results, 1):
                            if time_val_upd in self.la_results:
                                pending_listbox.insert(tk.END, f"{i}. {self.format_time(time_val_upd)} s ✓")
                            else:
                                pending_listbox.insert(tk.END, f"{i}. {self.format_time(time_val_upd)} s")
                    else:
                        messagebox.showwarning("Uwaga", "Ten odczyt jest już zaakceptowany!")
                else:
                    messagebox.showwarning("Uwaga", "Osiągnięto maksimum!")
        
        tk.Button(right_frame, text="✅ Akceptuj", command=accept_pending,
                 font=('Arial', 9), bg='#4CAF50', fg='white', padx=10, pady=5).pack(pady=5)
        
        tk.Button(manage_window, text="Zamknij", command=manage_window.destroy,
                 font=('Arial', 10), bg='#2196F3', fg='white', padx=20, pady=5).pack(pady=10)

    def la_show_details(self):
        """Pokaż szczegóły biegu"""
        selection = self.la_history_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Zaznacz bieg!")
            return
        
        item = self.la_history_tree.item(selection[0])
        race_number = item['values'][0]
        
        race_data = None
        for m in self.la_measurements:
            if m['race'] == race_number:
                race_data = m
                break
        
        if not race_data:
            messagebox.showerror("Błąd", "Nie znaleziono!")
            return
        
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Szczegóły biegu #{race_number}")
        details_window.geometry("400x300")
        details_window.configure(bg='white')
        
        tk.Label(details_window, text=f"🏃 BIEG #{race_number}", 
                font=('Arial', 14, 'bold'), bg='white').pack(pady=10)
        
        tk.Label(details_window, text=f"Zawodników: {race_data['num_athletes']}", 
                font=('Arial', 11), bg='white').pack(pady=5)
        
        tk.Label(details_window, text=f"Godzina: {race_data['timestamp']}", 
                font=('Arial', 11), bg='white').pack(pady=5)
        
        results_frame = tk.Frame(details_window, bg='white')
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(results_frame, text="WYNIKI:", font=('Arial', 12, 'bold'), 
                bg='white').pack(fill=tk.X)
        
        times_data = race_data.get('times', race_data.get('results', []))
        for i, result in enumerate(times_data, 1):
            tk.Label(results_frame, 
                    text=f"{i}.  {self.format_time(result)} s", 
                    font=('Courier New', 12, 'bold'),
                    bg='white').pack(fill=tk.X, pady=2)
        
        tk.Button(details_window, text="Zamknij", command=details_window.destroy,
                 font=('Arial', 10), bg='#2196F3', fg='white', padx=20, pady=5).pack(pady=10)

    def la_delete_race(self):
        """Usuń bieg z historii LA"""
        selected = self.la_history_tree.selection()
        if not selected:
            messagebox.showwarning("Brak zaznaczenia", "Zaznacz bieg!")
            return
        
        item = self.la_history_tree.item(selected[0])
        values = item['values']
        
        if messagebox.askyesno("Usuń", f"Usuń bieg #{values[0]}?"):
            self.la_history_tree.delete(selected[0])
            
            race_num = values[0]
            for i, m in enumerate(self.la_measurements):
                if m['race'] == race_num:
                    self.la_measurements.pop(i)
                    break
            
            self.la_count_label.config(text=str(len(self.la_measurements)))
            
            if not self.la_measurements:
                self.la_save_btn.config(state='disabled')

    def la_edit_race(self):
        """Edytuj bieg LA"""
        selected = self.la_history_tree.selection()
        if not selected:
            messagebox.showwarning("Brak zaznaczenia", "Zaznacz bieg!")
            return
        
        item = self.la_history_tree.item(selected[0])
        values = item['values']
        race_num = values[0]
        
        race_data = None
        for m in self.la_measurements:
            if m['race'] == race_num:
                race_data = m
                break
        
        if not race_data:
            messagebox.showerror("Błąd", "Nie znaleziono!")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edytuj bieg #{race_num}")
        dialog.geometry("400x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text=f"Edycja biegu #{race_num}", 
                font=('Arial', 12, 'bold')).pack(pady=10)
        
        times_frame = tk.Frame(dialog)
        times_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        time_entries = []
        for i, t in enumerate(race_data['times']):
            row = tk.Frame(times_frame)
            row.pack(fill=tk.X, padx=20, pady=2)
            
            tk.Label(row, text=f"Zaw. {i+1}:", font=('Arial', 9), width=8, anchor='e').pack(side=tk.LEFT, padx=5)
            entry = tk.Entry(row, font=('Arial', 10), width=12, justify='center')
            entry.insert(0, self.format_time(t))
            entry.pack(side=tk.LEFT, padx=5)
            time_entries.append(entry)
        
        def save_edit():
            new_times = []
            try:
                for entry in time_entries:
                    time_str = entry.get().strip()
                    parts = time_str.split(':')
                    if len(parts) == 2:
                        minutes = int(parts[0])
                        seconds = float(parts[1])
                        total_seconds = minutes * 60 + seconds
                        new_times.append(total_seconds)
                    else:
                        raise ValueError("Zły format")
                
                new_times.sort()
                race_data['times'] = new_times
                
                time_1 = self.format_time(new_times[0]) if len(new_times) > 0 else "-"
                time_2 = self.format_time(new_times[1]) if len(new_times) > 1 else "-"
                time_3 = self.format_time(new_times[2]) if len(new_times) > 2 else "-"
                
                self.la_history_tree.item(selected[0], values=(
                    race_num,
                    race_data['num_athletes'],
                    time_1,
                    time_2,
                    time_3,
                    race_data['timestamp']
                ))
                
                dialog.destroy()
            except:
                messagebox.showerror("Błąd", "Zły format! Użyj MM:SS.xxx")
        
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="💾 Zapisz", command=save_edit,
                 font=('Arial', 10, 'bold'), bg='#4CAF50', fg='white', padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="❌ Anuluj", command=dialog.destroy,
                 font=('Arial', 10), bg='#f44336', fg='white', padx=20, pady=5).pack(side=tk.LEFT, padx=5)

    def la_export_to_csv(self):
        """Eksport LA do CSV"""
        if not self.la_measurements:
            messagebox.showwarning("Brak danych", "Brak biegów!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"LA_historia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f, delimiter=';')
                    
                    max_athletes = max(m['num_athletes'] for m in self.la_measurements)
                    
                    header = ['Nr_Biegu', 'Liczba_Zawodników', 'Godzina']
                    for i in range(max_athletes):
                        header.append(f'Miejsce_{i+1}')
                    writer.writerow(header)
                    
                    for m in reversed(self.la_measurements):
                        row = [m['race'], m['num_athletes'], m['timestamp']]
                        for i in range(max_athletes):
                            if i < len(m.get('times', m.get('results', []))):
                                row.append(self.format_time(m.get('times', m.get('results', []))[i]))
                            else:
                                row.append('-')
                        writer.writerow(row)
                
                messagebox.showinfo("OK", f"Zapisano do:\n{filename}")
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie udało się:\n{e}")

    def la_clear_history(self):
        """Wyczyść historię LA"""
        if messagebox.askyesno("Wyczyść", "Czy na pewno?"):
            self.la_measurements.clear()
            self.la_history_tree.delete(*self.la_history_tree.get_children())
            self.la_race_number = 0
            self.la_count_label.config(text="0")
            self.la_save_btn.config(state='disabled')

    # ============================================================================
    # METODY POMOCNICZE I OSF
    # ============================================================================

    def format_time(self, seconds):
        """Formatuje czas"""
        precision = 2
        if hasattr(self, 'format_var'):
            fmt_text = self.format_var.get()
            if "Tysięczne" in fmt_text:
                precision = 3
            elif "Setne" in fmt_text:
                precision = 2
            elif "Dziesiąte" in fmt_text:
                precision = 1
            elif "Sekundy" in fmt_text:
                precision = 0

        minutes = int(seconds // 60)
        secs = seconds % 60

        if precision == 0:
            return f"{minutes:02d}:{int(round(secs)):02d}"
        else:
            width = 3 + precision
            return f"{minutes:02d}:{secs:0{width}.{precision}f}"

    def format_time_mmss(self, seconds):
        """Formatuje MM:SS.xx"""
        precision = 2
        if hasattr(self, 'format_var'):
            fmt_text = self.format_var.get()
            if "Tysięczne" in fmt_text:
                precision = 3
            elif "Setne" in fmt_text:
                precision = 2
            elif "Dziesiąte" in fmt_text:
                precision = 1
            elif "Sekundy" in fmt_text:
                precision = 0

        minutes = int(seconds // 60)
        secs = seconds % 60

        if precision == 0:
            return f"{minutes:02d}:{int(round(secs)):02d}"
        else:
            width = 3 + precision
            return f"{minutes:02d}:{secs:0{width}.{precision}f}"

    def refresh_ports(self):
        """Odświeżanie listy portów"""
        ports = serial.tools.list_ports.comports()
        port_list = [port.device for port in ports]
        self.port_combo['values'] = port_list
        if port_list:
            self.port_combo.current(0)

    def toggle_connection(self):
        """Połącz/Rozłącz"""
        if not self.running:
            self.connect()
        else:
            self.disconnect()

    def connect(self):
        """Połączenie z chronometrem"""
        port = self.port_var.get()
        if not port:
            messagebox.showwarning("Brak portu", "Wybierz port COM!")
            return

        try:
            self.serial_port = serial.Serial(
                port=port,
                baudrate=115200,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )

            self.running = True
            self.serial_thread = threading.Thread(target=self.read_serial, daemon=True)
            self.serial_thread.start()

            self.status_label.config(text=f"● POŁĄCZONY: {port}", fg='green')
            self.connect_btn.config(text="ROZŁĄCZ", bg='#f44336')

            if not self.la_mode:
                self.next_race_btn.config(state='normal')

            messagebox.showinfo("Połączono", f"Połączono z: {port}")

        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można połączyć:\n{e}")

    def disconnect(self):
        """Rozłączenie"""
        self.running = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()

        self.status_label.config(text="● ROZŁĄCZONY", fg='red')
        self.connect_btn.config(text="POŁĄCZ", bg='#4CAF50')
        self.next_race_btn.config(state='disabled')

    def read_serial(self):
        """Wątek odczytu danych"""
        buffer = ""
        print(">>> read_serial() STARTED")
        while self.running:
            try:
                if self.serial_port.in_waiting > 0:
                    chunk = self.serial_port.read(self.serial_port.in_waiting).decode('ascii', errors='ignore')

                    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                    self.log_file.write(f"[{timestamp}] CHUNK: {repr(chunk)}\n")
                    self.log_file.flush()

                    buffer += chunk

                    lines = buffer.split('\n')
                    buffer = lines[-1]

                    for line in lines[:-1]:
                        line = line.strip()

                        self.log_file.write(f"[{timestamp}] LINE: {repr(line)}\n")
                        self.log_file.flush()

                        if line.startswith('CZL'):
                            self.data_queue.put(line)
            except Exception as e:
                error_msg = f"Błąd odczytu: {e}"
                print(error_msg)
                timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                self.log_file.write(f"[{timestamp}] ERROR: {error_msg}\n")
                self.log_file.flush()
                break
        print(">>> read_serial() ENDED")

    def check_queue(self):
        """Sprawdzanie kolejki danych"""
        try:
            while not self.data_queue.empty():
                message = self.data_queue.get_nowait()
                self.process_message(message)
        except queue.Empty:
            pass
        finally:
            self.root.after(10, self.check_queue)

    def process_message(self, message):
        """Przetwarza wiadomość"""
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        self.log_file.write(f"[{timestamp}] PROCESS: {repr(message)}\n")
        self.log_file.flush()

        if len(message) < 6:
            return

        try:
            channel = int(message[3])
            event_type = int(message[4])
            time_raw_str = message[5:]
            time_raw = int(time_raw_str)
            time_seconds = time_raw / 1000.0

            log_line = f"DEBUG: {message} → kanał={channel}, typ={event_type}, czas={time_seconds:.3f}"
            print(log_line)
            self.log_file.write(f"[{timestamp}] {log_line}\n")
            self.log_file.flush()

            if channel == 0:
                return

            # Routing
            if self.la_mode:
                if not self.la_race_active and channel == 1:
                    # === WYCZYŚĆ LED PRZY AUTOMATYCZNYM STARCIE LA ===
                    if self.led_enabled and self.led_manager:
                        self.led_manager.stop_rotation()
                        self.led_manager.display.clear_display()

                    if self.la_log_file is None:
                        self.la_log_file = open(self.la_log_filename, 'a', encoding='utf-8')
                        self.la_log_file.write(f"\n{'='*60}\n")
                        self.la_log_file.write(f"BIEG LA - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        self.la_log_file.write(f"{'='*60}\n")

                    self.la_race_active = True
                    self.la_results = []
                    self.la_all_crossings = []
                    self.la_pending_results = []
                    self.la_status_label.config(text="🏃 TRWA BIEG", bg='orange')
                    self.la_next_btn.config(state='disabled')
                    self.la_manual_finish_btn.config(state='normal')
                    self.la_manage_results_btn.config(state='normal')
                    print("🏃 [LA] KANAŁ 1 - start")
                    self.process_la_crossing(channel, time_seconds)
                elif self.la_start_absolute_time is not None:
                    self.process_la_crossing(channel, time_seconds)
            else:
                self.process_osf_crossing(channel, time_seconds)

        except (ValueError, IndexError) as e:
            error_msg = f"Błąd parsowania: {e}"
            print(error_msg)
            self.log_file.write(f"[{timestamp}] ERROR: {error_msg}\n")
            self.log_file.flush()

    def process_la_crossing(self, channel, time_value):
        """Przetwarzanie przecięcia LA"""
        is_blocked = self.la_block_var.get()

        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        status = "⛔ BLOKOWANY" if is_blocked else "✅ WYNIK"

        if self.la_log_file:
            self.la_log_file.write(f"[{timestamp}] {status}: Kanał={channel}, Czas={time_value:.4f}s\n")
            self.la_log_file.flush()

        self.la_all_crossings.append((channel, time_value, is_blocked))

        # Kanał 1 = START
        if channel == 1:
            if self.la_start_time is None:
                self.la_start_time = time_value
                self.la_start_absolute_time = time.time()
                if self.la_log_file:
                    self.la_log_file.write(f"[{timestamp}] ✅ START\n")
                    self.la_log_file.flush()
                return

        # Kanał mety
        if channel == self.la_finish_channel:
            if self.la_start_absolute_time is None:
                return

            net_time = time.time() - self.la_start_absolute_time

            self.la_pending_results.append(net_time)
            print(f">>> [LA] Odczyt #{len(self.la_pending_results)}: {net_time:.3f}s {'🔒' if is_blocked else '✓'}")

            if not is_blocked and len(self.la_results) < self.la_num_athletes:
                self.la_results.append(net_time)
                self.la_update_results_display()

                if len(self.la_results) == self.la_num_athletes:
                    self.la_race_active = False  # ZATRZYMAJ TIMER NA LED
                    self.la_status_label.config(text="❌ NIE GOTOWY", bg='red')
                    self.la_next_btn.config(state='normal')
                    self.la_manual_finish_btn.config(state='disabled')

                    self.la_add_to_history()

                    if self.la_log_file:
                        self.la_log_file.write(f"\n{'='*60}\nZAKOŃCZONY\n{'='*60}\n\n")
                        self.la_log_file.flush()
                        self.la_log_file.close()
                        self.la_log_file = None

    def process_osf_crossing(self, channel, time_seconds):
        """Przetwarzanie przecięcia OSF"""
        mode = self.mode_var.get()

        if "POJEDYNCZY" in mode:
            self.handle_pojedynczy(channel, time_seconds)
        elif "DWA TORY" in mode:
            self.handle_osf_dwa_tory(channel, time_seconds)
        elif "DRUŻYNA" in mode:
            self.handle_osf_druzyna(channel, time_seconds)
        elif "WACHADŁO" in mode:
            self.handle_wachadlo(channel, time_seconds)

    def handle_pojedynczy(self, channel, time_seconds):
        """POJEDYNCZY"""
        if channel == 1:
            if not self.ready_for_start:
                return

            # === WYCZYŚĆ LED PRZY STARCIE ===
            if self.led_enabled and self.led_manager:
                self.led_manager.display.clear_display()

            self.start_time = time_seconds
            self.start_absolute_time = time.time()
            self.timer_running = True
            self.race_in_progress = True
            self.race_completed = False
            self.ready_for_start = False

            self.left_lane_crossings = []
            self.osf_all_left_crossings = []
            self.race_number += 1
            self.count_label.config(text=str(self.race_number))
            self.osf_manage_btn.config(state='normal')

            self.update_display("⏱️ START!\nOczekiwanie na META...")

        elif channel == 4 and self.race_in_progress:
            if self.start_time is not None:
                result_time = time.time() - self.start_absolute_time

                is_blocked = self.osf_block_var.get()
                self.osf_all_left_crossings.append((result_time, is_blocked))

                if not is_blocked and len(self.left_lane_crossings) < 1:
                    self.left_lane_crossings.append(result_time)

                    self.timer_running = False
                    self.race_completed = True
                    self.timer_label.config(text=self.format_time_mmss(result_time))
                    self.add_measurement("POJEDYNCZY", "-", result_time)
                    self.next_race_btn.config(state='normal')
                    self.update_display(f"✅ ZAKOŃCZONY!\n\nCzas: {self.format_time(result_time)} s")
                    
                    # === INTEGRACJA LED DLA OSF POJEDYNCZY ===
                    if self.led_enabled and self.led_manager:
                        race_data = {
                            'results': [
                                {'time': self.format_time(result_time), 'place': 1}
                            ]
                        }
                        self.led_manager.update_race_results(race_data)
                        print(f"📺 LED: Wyświetlono wynik OSF POJEDYNCZY")

    def handle_osf_dwa_tory(self, channel, time_seconds):
        """OSF DWA TORY"""
        if channel == 1:
            if not self.ready_for_start:
                return

            # === WYCZYŚĆ LED PRZY STARCIE ===
            if self.led_enabled and self.led_manager:
                self.led_manager.display.clear_display()

            self.start_time = time_seconds
            self.start_absolute_time = time.time()
            self.timer_running = True
            self.race_in_progress = True
            self.race_completed = False
            self.ready_for_start = False
            self.left_lane_result = None
            self.right_lane_result = None
            self.left_lane_finished = False
            self.right_lane_finished = False

            self.left_lane_crossings = []
            self.right_lane_crossings = []
            self.osf_all_left_crossings = []
            self.osf_all_right_crossings = []

            self.race_number += 1
            self.count_label.config(text=str(self.race_number))
            self.osf_manage_btn.config(state='normal')
            self.update_display("⏱️ START!\nOczekiwanie na mety...")

        elif channel == 3 and self.race_in_progress:
            if self.start_time is not None:
                result_time = time.time() - self.start_absolute_time

                is_blocked = self.osf_block_var.get()
                self.osf_all_left_crossings.append((result_time, is_blocked))

                if not is_blocked and len(self.left_lane_crossings) < 1:
                    self.left_lane_crossings.append(result_time)
                    self.left_lane_result = result_time
                    self.left_lane_finished = True

                    timestamp = datetime.now().strftime("%H:%M:%S")
                    self.measurements.append({
                        'race': self.race_number,
                        'mode': "OSF - DWA TORY",
                        'lane': "LEWY",
                        'time': result_time,
                        'timestamp': timestamp
                    })
                    self.history_tree.insert('', 0, values=(
                        self.race_number,
                        "OSF - DWA TORY",
                        "LEWY",
                        self.format_time(result_time),
                        timestamp
                    ), tags=('race',))

                self.update_osf_display()

        elif channel == 4 and self.race_in_progress:
            if self.start_time is not None:
                result_time = time.time() - self.start_absolute_time

                is_blocked = self.osf_block_var.get()
                self.osf_all_right_crossings.append((result_time, is_blocked))

                if not is_blocked and len(self.right_lane_crossings) < 1:
                    self.right_lane_crossings.append(result_time)
                    self.right_lane_result = result_time
                    self.right_lane_finished = True

                    timestamp = datetime.now().strftime("%H:%M:%S")
                    self.measurements.append({
                        'race': self.race_number,
                        'mode': "OSF - DWA TORY",
                        'lane': "PRAWY",
                        'time': result_time,
                        'timestamp': timestamp
                    })
                    self.history_tree.insert('', 0, values=(
                        self.race_number,
                        "OSF - DWA TORY",
                        "PRAWY",
                        self.format_time(result_time),
                        timestamp
                    ), tags=('race',))

                self.update_osf_display()

                # === NIEZALEŻNE ZEGARY - WYNIKI WYŚWIETLANE NATYCHMIAST W update_live_timer ===
                # Nie czekamy na oba tory - każdy tor pokazuje wynik jak skończy

    def update_osf_display(self):
        """Aktualizacja wyświetlania OSF DWA TORY"""
        display = f"🏁 OSF - BIEG #{self.race_number}\n\n"

        if self.left_lane_result is not None:
            display += f"✅ Tor LEWY:  {self.format_time(self.left_lane_result)} s\n"
        else:
            display += f"⏳ Tor LEWY:  czekam...\n"

        if self.right_lane_result is not None:
            display += f"✅ Tor PRAWY: {self.format_time(self.right_lane_result)} s"
        else:
            display += f"⏳ Tor PRAWY: czekam..."

        self.update_display(display)

        if self.left_lane_finished and self.right_lane_finished:
            self.timer_running = False
            self.race_completed = False
            self.next_race_btn.config(state='normal')
            max_time = max(self.left_lane_result, self.right_lane_result)
            self.timer_label.config(text=self.format_time_mmss(max_time))

    def handle_osf_druzyna(self, channel, time_seconds):
        """OSF DRUŻYNA"""
        if channel == 1:
            if not self.ready_for_start:
                return

            # === WYCZYŚĆ LED PRZY STARCIE ===
            if self.led_enabled and self.led_manager:
                self.led_manager.display.clear_display()

            self.start_time = time_seconds
            self.start_absolute_time = time.time()
            self.timer_running = True
            self.race_in_progress = True
            self.race_completed = False
            self.ready_for_start = False
            self.left_lane_crossings = []
            self.right_lane_crossings = []

            self.osf_all_left_crossings = []
            self.osf_all_right_crossings = []

            self.left_lane_result = None
            self.right_lane_result = None
            self.race_number += 1
            self.count_label.config(text=str(self.race_number))
            self.osf_manage_btn.config(state='normal')
            self.update_display("⏱️ START!\nLiczenie do 5 zawodników...")

        elif channel == 3 and self.race_in_progress:
            if self.start_time is not None:
                crossing_time = time.time() - self.start_absolute_time

                is_blocked = self.osf_block_var.get()
                self.osf_all_left_crossings.append((crossing_time, is_blocked))

                if not is_blocked and len(self.left_lane_crossings) < 5:
                    self.left_lane_crossings.append(crossing_time)
                    self.update_druzyna_display()

        elif channel == 4 and self.race_in_progress:
            if self.start_time is not None:
                crossing_time = time.time() - self.start_absolute_time

                is_blocked = self.osf_block_var.get()
                self.osf_all_right_crossings.append((crossing_time, is_blocked))

                if not is_blocked and len(self.right_lane_crossings) < 5:
                    self.right_lane_crossings.append(crossing_time)
                    self.update_druzyna_display()

    def update_druzyna_display(self):
        """Aktualizacja DRUŻYNA"""
        display = f"👥 OSF DRUŻYNA - BIEG #{self.race_number}\n\n"

        if len(self.left_lane_crossings) == 5:
            left_time = self.left_lane_crossings[-1]
            display += f"✅ Tor LEWY: {self.format_time(left_time)} s\n"
        else:
            display += f"⏳ Tor LEWY: {len(self.left_lane_crossings)}/5 zawodników\n"

        if len(self.right_lane_crossings) == 5:
            right_time = self.right_lane_crossings[-1]
            display += f"✅ Tor PRAWY: {self.format_time(right_time)} s"
        else:
            display += f"⏳ Tor PRAWY: {len(self.right_lane_crossings)}/5 zawodników"

        self.update_display(display)

        if len(self.left_lane_crossings) == 5 and self.left_lane_result is None:
            left_time = self.left_lane_crossings[-1]
            self.left_lane_result = left_time
            timestamp = datetime.now().strftime("%H:%M:%S")

            self.measurements.append({
                'race': self.race_number,
                'mode': "OSF DRUŻYNA",
                'lane': "LEWY (5 os.)",
                'time': left_time,
                'timestamp': timestamp
            })
            self.history_tree.insert('', 0, values=(
                self.race_number,
                "OSF DRUŻYNA",
                "LEWY (5 os.)",
                self.format_time(left_time),
                timestamp
            ), tags=('race',))

        if len(self.right_lane_crossings) == 5 and self.right_lane_result is None:
            right_time = self.right_lane_crossings[-1]
            self.right_lane_result = right_time
            timestamp = datetime.now().strftime("%H:%M:%S")

            self.measurements.append({
                'race': self.race_number,
                'mode': "OSF DRUŻYNA",
                'lane': "PRAWY (5 os.)",
                'time': right_time,
                'timestamp': timestamp
            })
            self.history_tree.insert('', 0, values=(
                self.race_number,
                "OSF DRUŻYNA",
                "PRAWY (5 os.)",
                self.format_time(right_time),
                timestamp
            ), tags=('race',))

        if len(self.left_lane_crossings) == 5 and len(self.right_lane_crossings) == 5:
            self.timer_running = False
            self.race_completed = False
            self.next_race_btn.config(state='normal')

            max_time = max(self.left_lane_crossings[-1], self.right_lane_crossings[-1])
            self.timer_label.config(text=self.format_time_mmss(max_time))

            # === NIEZALEŻNE ZEGARY - WYNIKI WYŚWIETLANE NATYCHMIAST W update_live_timer ===
            # Każdy tor pokazuje wynik jak skończy (nie czekamy na oba tory)

    def handle_wachadlo(self, channel, time_seconds):
        """WACHADŁO"""
        if channel == 1:
            if not self.ready_for_start:
                return

            # === WYCZYŚĆ LED PRZY STARCIE ===
            if self.led_enabled and self.led_manager:
                self.led_manager.display.clear_display()

            self.start_time = time_seconds
            self.start_absolute_time = time.time()
            self.timer_running = True
            self.race_in_progress = True
            self.race_completed = False
            self.ready_for_start = False
            self.left_lane_crossings = []
            self.right_lane_crossings = []

            self.osf_all_left_crossings = []
            self.osf_all_right_crossings = []

            self.race_number += 1
            self.count_label.config(text=str(self.race_number))
            self.osf_manage_btn.config(state='normal')
            self.update_display("⏱️ START!\nLiczenie do 13 przecięć...")

        elif (channel == 3 or channel == 4) and self.race_in_progress:
            if self.start_time is not None:
                current_time = time.time()
                if channel in self.last_crossing_time:
                    time_since_last = current_time - self.last_crossing_time[channel]
                    if time_since_last < self.debounce_interval:
                        return

                self.last_crossing_time[channel] = current_time

                crossing_time = time.time() - self.start_absolute_time

                is_blocked = self.osf_block_var.get()

                if channel == 3:
                    self.osf_all_left_crossings.append((crossing_time, is_blocked))

                    if not is_blocked and len(self.left_lane_crossings) < 13:
                        self.left_lane_crossings.append(crossing_time)
                else:
                    self.osf_all_right_crossings.append((crossing_time, is_blocked))

                    if not is_blocked and len(self.right_lane_crossings) < 13:
                        self.right_lane_crossings.append(crossing_time)

                self.update_wachadlo_display()

    def update_wachadlo_display(self):
        """Aktualizacja WACHADŁO"""
        display = f"🔀 WACHADŁO - BIEG #{self.race_number}\n\n"

        if len(self.left_lane_crossings) == 13:
            left_time = self.left_lane_crossings[-1]
            display += f"✅ Tor LEWY:  {self.format_time(left_time)} s ({len(self.left_lane_crossings)}/13)\n"
        else:
            display += f"⏳ Tor LEWY:  {len(self.left_lane_crossings)}/13 przecięć\n"

        if len(self.right_lane_crossings) == 13:
            right_time = self.right_lane_crossings[-1]
            display += f"✅ Tor PRAWY: {self.format_time(right_time)} s ({len(self.right_lane_crossings)}/13)"
        else:
            display += f"⏳ Tor PRAWY: {len(self.right_lane_crossings)}/13 przecięć"

        self.update_display(display)

        if len(self.left_lane_crossings) == 13 and self.left_lane_result is None:
            left_time = self.left_lane_crossings[-1]
            self.left_lane_result = left_time
            timestamp = datetime.now().strftime("%H:%M:%S")

            self.measurements.append({
                'race': self.race_number,
                'mode': "WACHADŁO",
                'lane': "LEWY",
                'time': left_time,
                'timestamp': timestamp
            })
            self.history_tree.insert('', 0, values=(
                self.race_number,
                "WACHADŁO",
                "LEWY",
                self.format_time(left_time),
                timestamp
            ), tags=('race',))

        if len(self.right_lane_crossings) == 13 and self.right_lane_result is None:
            right_time = self.right_lane_crossings[-1]
            self.right_lane_result = right_time
            timestamp = datetime.now().strftime("%H:%M:%S")

            self.measurements.append({
                'race': self.race_number,
                'mode': "WACHADŁO",
                'lane': "PRAWY",
                'time': right_time,
                'timestamp': timestamp
            })
            self.history_tree.insert('', 0, values=(
                self.race_number,
                "WACHADŁO",
                "PRAWY",
                self.format_time(right_time),
                timestamp
            ), tags=('race',))

        if len(self.left_lane_crossings) == 13 and len(self.right_lane_crossings) == 13:
            self.timer_running = False
            self.race_completed = False
            self.next_race_btn.config(state='normal')

            max_time = max(self.left_lane_crossings[-1], self.right_lane_crossings[-1])
            self.timer_label.config(text=self.format_time_mmss(max_time))

            # === NIEZALEŻNE ZEGARY - WYNIKI WYŚWIETLANE NATYCHMIAST W update_live_timer ===
            # Każdy tor pokazuje wynik jak skończy (nie czekamy na oba tory)

    def update_display(self, text):
        """Aktualizacja pola tekstowego"""
        self.display_text.config(state='normal')
        self.display_text.delete(1.0, tk.END)
        self.display_text.insert(tk.END, text)
        self.display_text.config(state='disabled')

    def update_single_display(self):
        """Aktualizacja POJEDYNCZY"""
        if self.left_lane_crossings:
            result_time = self.left_lane_crossings[0]
            self.update_display(f"✅ ZAKOŃCZONY!\n\nCzas: {self.format_time(result_time)} s")

    def update_two_lanes_display(self):
        """Aktualizacja DWA TORY"""
        self.update_osf_display()

    def add_measurement(self, mode, lane, time):
        """Dodaj pomiar do historii"""
        self.race_number += 1
        timestamp = datetime.now().strftime('%H:%M:%S')

        self.measurements.append({
            'race': self.race_number,
            'mode': mode,
            'lane': lane,
            'time': time,
            'timestamp': timestamp
        })

        self.history_tree.insert('', 0, values=(
            self.race_number,
            mode,
            lane,
            self.format_time(time),
            timestamp
        ), tags=('race',))

        self.count_label.config(text=str(self.race_number))

    def next_race(self):
        """Kolejny bieg"""
        self.ready_for_start = True
        self.race_completed = False
        self.race_in_progress = False
        self.start_time = None
        self.start_absolute_time = None  # RESET CZASU ABSOLUTNEGO
        self.timer_running = False  # ZATRZYMAJ TIMER
        self.left_lane_crossings.clear()
        self.right_lane_crossings.clear()

        self.left_lane_result = None
        self.right_lane_result = None
        self.left_lane_finished = False
        self.right_lane_finished = False

        self.last_crossing_time = {1: 0, 3: 0, 4: 0}

        self.next_race_btn.config(state='disabled')

        # RESETUJ TIMER NA EKRANIE GUI
        self.timer_label.config(text="00:00.00", fg='#9E9E9E')

        self.display_text.config(state='normal')
        self.display_text.delete(1.0, tk.END)
        self.display_text.insert(tk.END, "⏳ Oczekiwanie na START...\n")
        self.display_text.config(state='disabled')

        # === ZATRZYMAJ ROTACJĘ I WYCZYŚĆ LED ===
        if self.led_enabled and self.led_manager:
            self.led_manager.stop_rotation()
            self.led_manager.display.clear_display()

    def reset_measurement(self):
        """Reset pomiaru"""
        if messagebox.askyesno("Reset", "Czy na pewno?"):
            self.ready_for_start = True
            self.race_completed = False
            self.race_in_progress = False
            self.start_time = None
            self.timer_running = False
            self.left_lane_crossings.clear()
            self.right_lane_crossings.clear()

            self.osf_all_left_crossings.clear()
            self.osf_all_right_crossings.clear()

            self.last_crossing_time = {1: 0, 3: 0, 4: 0}

            self.next_race_btn.config(state='normal')
            self.osf_manage_btn.config(state='disabled')

            self.display_text.config(state='normal')
            self.display_text.delete(1.0, tk.END)
            self.display_text.insert(tk.END, "🔄 RESET\n")
            self.display_text.config(state='disabled')
            
            # Wyczyść LED
            if self.led_enabled and self.led_manager:
                self.led_manager.display.clear_display()

    def update_live_timer(self):
        """Live timer"""
        if self.timer_running and self.start_absolute_time:
            elapsed = time.time() - self.start_absolute_time + 0.10  # Korekcja +0.10s
            self.timer_label.config(text=self.format_time_mmss(elapsed), fg='#4CAF50')

            # === WYŚWIETLANIE BIEGNĄCEGO CZASU NA LED (OSF) ===
            if self.led_enabled and self.led_manager and self.led_manager.display.connected:
                # TRYBY Z DWOMA TORAMI - NIEZALEŻNE ZEGARY
                if self.current_mode in [MeasurementMode.OSF_DWA_TORY,
                                        MeasurementMode.OSF_DRUZYNA,
                                        MeasurementMode.WACHADLO]:
                    # LINIA 1 (LEWY TOR)
                    if self.left_lane_finished and self.left_lane_result is not None:
                        # Tor lewy skończył - pokaż wynik
                        result_str = self.format_time_mmss(self.left_lane_result)
                        packet1 = create_ranking_packet(result_str, 1, line=1)
                        packet1_text = result_str + " TOR 1"
                        # Używamy create_time_packet_line1 z tekstem wyniku
                        packet1 = create_time_packet_line1(result_str + "  TOR 1")
                    else:
                        # Tor lewy biega - pokaż biegnący czas
                        time_str = self.format_time_mmss(elapsed)
                        packet1 = create_time_packet_line1(time_str)

                    self.led_manager.display.send_packet(packet1, delay=0.05)  # Opóźnienie przed linią 2

                    # LINIA 2 (PRAWY TOR)
                    if self.right_lane_finished and self.right_lane_result is not None:
                        # Tor prawy skończył - pokaż wynik
                        result_str = self.format_time_mmss(self.right_lane_result)
                        packet2 = create_time_packet_line2(result_str + "  TOR 2")
                    else:
                        # Tor prawy biega - pokaż biegnący czas
                        time_str = self.format_time_mmss(elapsed)
                        packet2 = create_time_packet_line2(time_str)

                    self.led_manager.display.send_packet(packet2, delay=0)  # Bez opóźnienia po linii 2
                else:
                    # TRYBY POJEDYNCZE - jeden zegar
                    time_str = self.format_time_mmss(elapsed)
                    packet = create_time_packet_line1(time_str)
                    self.led_manager.display.send_packet(packet, delay=0)

        elif self.race_completed:
            self.timer_label.config(fg='#2196F3')
        else:
            self.timer_label.config(text="00:00.00", fg='#9E9E9E')

        if self.la_race_active and self.la_start_absolute_time:
            elapsed_la = time.time() - self.la_start_absolute_time + 0.10  # Korekcja +0.10s
            self.la_timer_label.config(text=self.format_time_mmss(elapsed_la), fg='#4CAF50')

            # === WYŚWIETLANIE BIEGNĄCEGO CZASU NA LED (LA) ===
            if self.led_enabled and self.led_manager and self.led_manager.display.connected:
                time_str = self.format_time_mmss(elapsed_la)

                # Wyświetl na obu liniach dla lepszej widoczności
                packet = create_time_packet_line1(time_str)
                self.led_manager.display.send_packet(packet, delay=0.05 if self.la_num_athletes >= 2 else 0)

                if self.la_num_athletes >= 2:
                    packet2 = create_time_packet_line2(time_str)
                    self.led_manager.display.send_packet(packet2, delay=0)
        else:
            self.la_timer_label.config(text="00:00.00", fg='#9E9E9E')

        self.root.after(50, self.update_live_timer)

    def update_status_indicator(self):
        """Aktualizuje wskaźniki statusu"""
        if self.la_mode:
            pass
        else:
            if self.race_in_progress:
                current_state = 'RACING'
            elif self.ready_for_start:
                current_state = 'READY'
            else:
                current_state = 'NOT_READY'

            if current_state != self.last_status_state:
                if current_state == 'RACING':
                    self.race_status_label.config(text="⚡ TRWA BIEG", bg='orange', fg='white')
                    self.big_status_label.place_forget()
                    self.format_combo.config(state='disabled')

                elif current_state == 'READY':
                    self.race_status_label.config(text="✅ GOTOWY", bg='green', fg='white')
                    self.big_status_label.place_forget()
                    self.format_combo.config(state='readonly')

                else:
                    self.race_status_label.config(text="❌ NIE GOTOWY", bg='red', fg='white')
                    self.big_status_label.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.9, relheight=0.9)
                    self.format_combo.config(state='readonly')

                self.last_status_state = current_state

        self.root.after(100, self.update_status_indicator)

    def on_mode_change(self, event=None):
        """Zmiana trybu OSF"""
        mode_text = self.mode_var.get()
        for mode in MeasurementMode:
            if mode.value == mode_text:
                self.current_mode = mode
                break

    def on_format_change(self, event=None):
        """Zmiana formatu czasu"""
        fmt_text = self.format_var.get()
        for fmt in TimeFormat:
            if fmt.value[0] == fmt_text:
                self.time_format = fmt
                break

    def osf_manual_start(self):
        """START RĘCZNY OSF"""
        if self.race_in_progress:
            messagebox.showwarning("Uwaga", "Bieg już trwa!")
            return

        if not self.ready_for_start:
            messagebox.showwarning("Uwaga", "Kliknij KOLEJNY BIEG!")
            return

        self.start_time = 0
        self.start_absolute_time = time.time()
        self.timer_running = True
        self.race_in_progress = True
        self.race_completed = False
        self.ready_for_start = False

        self.left_lane_result = None
        self.right_lane_result = None
        self.left_lane_finished = False
        self.right_lane_finished = False
        self.left_lane_crossings = []
        self.right_lane_crossings = []

        self.osf_all_left_crossings = []
        self.osf_all_right_crossings = []

        self.last_crossing_time = {1: 0, 3: 0, 4: 0}

        self.race_number += 1
        self.count_label.config(text=str(self.race_number))
        self.osf_manage_btn.config(state='normal')

        self.update_display("🖐️ START RĘCZNY!\nOczekiwanie...")
        self.osf_manual_finish_btn.config(state='normal')

    def osf_manual_finish(self):
        """META RĘCZNA OSF"""
        if not self.race_in_progress:
            messagebox.showwarning("Uwaga", "Bieg nie trwa!")
            return

        if self.start_absolute_time is None:
            messagebox.showerror("Błąd", "Brak startu!")
            return

        result_time = time.time() - self.start_absolute_time

        mode_text = self.mode_var.get()

        if "POJEDYNCZY" in mode_text:
            is_blocked = self.osf_block_var.get()
            self.osf_all_left_crossings.append((result_time, is_blocked))

            if not is_blocked and len(self.left_lane_crossings) < 1:
                self.left_lane_crossings.append(result_time)

            self.timer_running = False
            self.race_completed = True
            self.timer_label.config(text=self.format_time_mmss(result_time))
            self.add_measurement("POJEDYNCZY (RĘCZ)", "-", result_time)
            self.next_race_btn.config(state='normal')
            self.osf_manual_finish_btn.config(state='disabled')
            self.update_display(f"✅ RĘCZNIE!\n\n{self.format_time(result_time)} s")

        elif "DWA TORY" in mode_text:
            if not self.left_lane_finished and not self.right_lane_finished:
                lane = messagebox.askquestion("Który?", "Lewy (TAK) / Prawy (NIE)?")
                if lane == 'yes':
                    is_blocked = self.osf_block_var.get()
                    self.osf_all_left_crossings.append((result_time, is_blocked))
                    if not is_blocked:
                        self.left_lane_crossings.append(result_time)

                    self.left_lane_result = result_time
                    self.left_lane_finished = True
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    self.measurements.append({
                        'race': self.race_number,
                        'mode': "OSF - DWA TORY (RĘCZ)",
                        'lane': "LEWY",
                        'time': result_time,
                        'timestamp': timestamp
                    })
                    self.history_tree.insert('', 0, values=(
                        self.race_number,
                        "OSF - DWA TORY (RĘCZ)",
                        "LEWY",
                        self.format_time(result_time),
                        timestamp
                    ), tags=('race',))
                else:
                    is_blocked = self.osf_block_var.get()
                    self.osf_all_right_crossings.append((result_time, is_blocked))
                    if not is_blocked:
                        self.right_lane_crossings.append(result_time)

                    self.right_lane_result = result_time
                    self.right_lane_finished = True
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    self.measurements.append({
                        'race': self.race_number,
                        'mode': "OSF - DWA TORY (RĘCZ)",
                        'lane': "PRAWY",
                        'time': result_time,
                        'timestamp': timestamp
                    })
                    self.history_tree.insert('', 0, values=(
                        self.race_number,
                        "OSF - DWA TORY (RĘCZ)",
                        "PRAWY",
                        self.format_time(result_time),
                        timestamp
                    ), tags=('race',))

                self.update_osf_display()

            elif self.left_lane_finished and not self.right_lane_finished:
                is_blocked = self.osf_block_var.get()
                self.osf_all_right_crossings.append((result_time, is_blocked))
                if not is_blocked:
                    self.right_lane_crossings.append(result_time)

                self.right_lane_result = result_time
                self.right_lane_finished = True
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.measurements.append({
                    'race': self.race_number,
                    'mode': "OSF - DWA TORY (RĘCZ)",
                    'lane': "PRAWY",
                    'time': result_time,
                    'timestamp': timestamp
                })
                self.history_tree.insert('', 0, values=(
                    self.race_number,
                    "OSF - DWA TORY (RĘCZ)",
                    "PRAWY",
                    self.format_time(result_time),
                    timestamp
                ), tags=('race',))
                self.update_osf_display()

            elif not self.left_lane_finished and self.right_lane_finished:
                is_blocked = self.osf_block_var.get()
                self.osf_all_left_crossings.append((result_time, is_blocked))
                if not is_blocked:
                    self.left_lane_crossings.append(result_time)

                self.left_lane_result = result_time
                self.left_lane_finished = True
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.measurements.append({
                    'race': self.race_number,
                    'mode': "OSF - DWA TORY (RĘCZ)",
                    'lane': "LEWY",
                    'time': result_time,
                    'timestamp': timestamp
                })
                self.history_tree.insert('', 0, values=(
                    self.race_number,
                    "OSF - DWA TORY (RĘCZ)",
                    "LEWY",
                    self.format_time(result_time),
                    timestamp
                ), tags=('race',))
                self.update_osf_display()

            if self.left_lane_finished and self.right_lane_finished:
                self.timer_running = False
                self.race_completed = False
                self.next_race_btn.config(state='normal')
                self.osf_manual_finish_btn.config(state='disabled')
                max_time = max(self.left_lane_result, self.right_lane_result)
                self.timer_label.config(text=self.format_time_mmss(max_time))

        else:
            messagebox.showinfo("Info", "Działa tylko dla POJEDYNCZY i DWA TORY")

    def osf_manage_crossings(self):
        """Zarządzanie odczytami OSF"""
        messagebox.showinfo("Zarządzanie", "Funkcja w budowie")

    def osf_delete_measurement(self):
        """Usuń z historii OSF"""
        selected = self.history_tree.selection()
        if not selected:
            messagebox.showwarning("Brak", "Zaznacz!")
            return

        item = self.history_tree.item(selected[0])
        values = item['values']

        if messagebox.askyesno("Usuń", f"Usuń bieg {values[0]}?"):
            self.history_tree.delete(selected[0])

            race_num = values[0]
            lane = values[2]
            time_str = values[3]

            for i, m in enumerate(self.measurements):
                if (m['race'] == race_num and
                    m['lane'] == lane and
                    self.format_time(m['time']) == time_str):
                    self.measurements.pop(i)
                    break

    def export_to_csv(self):
        """Eksport OSF do CSV"""
        if not self.measurements:
            messagebox.showwarning("Brak", "Brak!")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"wyniki_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )

        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f, delimiter=';')
                    writer.writerow(['Nr_Biegu', 'Tryb', 'Tor', 'Czas_MM_SS', 'Godzina'])

                    for m in self.measurements:
                        writer.writerow([
                            m['race'],
                            m['mode'],
                            m['lane'],
                            self.format_time(m['time']),
                            m['timestamp']
                        ])

                messagebox.showinfo("OK", f"Zapisano:\n{filename}")
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie udało się:\n{e}")

    def clear_history(self):
        """Wyczyść historię OSF"""
        if messagebox.askyesno("Wyczyść", "Czy na pewno?"):
            self.measurements.clear()
            self.history_tree.delete(*self.history_tree.get_children())
            self.race_number = 0
            self.count_label.config(text="0")

    def __del__(self):
        """Zamknięcie"""
        if hasattr(self, 'log_file'):
            self.log_file.close()
        if hasattr(self, 'la_log_file') and self.la_log_file:
            self.la_log_file.close()
        if hasattr(self, 'led_manager') and self.led_manager:
            self.led_manager.shutdown()


def main():
    root = tk.Tk()
    app = ChronometerManager(root)
    root.mainloop()


if __name__ == "__main__":
    main()
