#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=====================================================
CHRONOMETR Z TABLICĄ LED
=====================================================

KOMPLETNY PROGRAM - wszystko w jednym pliku!

Funkcje:
- Chronometr z możliwością Start/Stop
- Wyświetlanie czasu na tablicy LED w czasie rzeczywistym
- Zapisywanie wyników wielu zawodników
- Automatyczne wyświetlanie rankingu na tablicy LED
- Jasność tablicy
- Czyszczenie tablicy

INSTRUKCJA:
1. Podłącz tablicę LED
2. Uruchom: python chronometr_z_tablica_led.py
3. Podaj port tablicy (np. COM5, COM6) lub zostaw puste jeśli nie masz tablicy
4. Używaj przycisków do pomiaru czasu
"""

import serial
import time
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime


# ============================================================================
# FUNKCJE CRC I PAKIETY LED
# ============================================================================

def calculate_crc16(data: bytes) -> int:
    """Oblicza CRC-16-CCITT dla danych"""
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
    """Tworzy pakiet z czasem dla linii 1"""
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


def create_ranking_packet(time_str: str, place: int, line: int) -> bytes:
    """Tworzy pakiet rankingowy (miejsce + czas)"""
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


# ============================================================================
# KLASA TABLICY LED
# ============================================================================

class TablicaLED:
    """Obsługa tablicy LED"""

    PAKIETY = {
        'clear_line1': bytes.fromhex('1B 07 54 00 14 75 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 2D 2D 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),
        'clear_line2': bytes.fromhex('1B 07 54 00 60 FC 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 2D 2D 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),
        'brightness_15': bytes.fromhex('1B 06 0C 00 15 3C 00 00 0F 00 0D 0A'.replace(' ', '')),
    }

    def __init__(self, port=None):
        self.port = port
        self.ser = None
        self.polaczony = False
        self.timer_thread = None
        self.timer_running = False
        self.ranking_thread = None
        self.ranking_running = False

    def polacz(self):
        """Połącz z tablicą LED"""
        if not self.port:
            return False

        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=9600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )
            self.polaczony = True
            time.sleep(0.3)
            print(f"✅ [LED] Połączono z tablicą na {self.port}")
            self.wyslij('brightness_15')
            return True
        except Exception as e:
            print(f"❌ [LED] Błąd połączenia: {e}")
            self.polaczony = False
            return False

    def rozlacz(self):
        """Rozłącz tablicę"""
        self.zatrzymaj_timer()
        self.zatrzymaj_ranking()
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.polaczony = False

    def wyslij(self, pakiet, delay=0.1):
        """Wyślij pakiet do tablicy"""
        if not self.polaczony:
            return False

        if isinstance(pakiet, str):
            pakiet = self.PAKIETY.get(pakiet)
            if not pakiet:
                return False

        try:
            self.ser.write(pakiet)
            self.ser.flush()
            if delay > 0:
                time.sleep(delay)
            return True
        except Exception as e:
            print(f"❌ [LED] Błąd wysyłania: {e}")
            return False

    def wyczysc(self):
        """Wyczyść całą tablicę"""
        self.zatrzymaj_timer()
        self.zatrzymaj_ranking()
        self.wyslij('clear_line1')
        time.sleep(0.05)
        self.wyslij('clear_line2')

    def pokaz_czas(self, czas_sekund):
        """Pokaż czas na linii 1"""
        if not self.polaczony:
            return

        minutes = int(czas_sekund // 60)
        seconds = int(czas_sekund % 60)
        milliseconds = int((czas_sekund % 1) * 1000)
        time_str = f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

        pakiet = create_time_packet_line1(time_str)
        self.wyslij(pakiet, delay=0)

    def _timer_worker(self, get_elapsed_time):
        """Wątek aktualizacji timera na LED"""
        while self.timer_running:
            elapsed = get_elapsed_time()
            if elapsed is not None:
                self.pokaz_czas(elapsed)
            time.sleep(0.1)

    def start_timer(self, get_elapsed_time):
        """Uruchom ciągłą aktualizację timera"""
        if not self.polaczony:
            return

        self.zatrzymaj_timer()
        self.timer_running = True
        self.timer_thread = threading.Thread(
            target=self._timer_worker,
            args=(get_elapsed_time,),
            daemon=True
        )
        self.timer_thread.start()

    def zatrzymaj_timer(self):
        """Zatrzymaj timer"""
        self.timer_running = False
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join(timeout=1)

    def _ranking_worker(self, wyniki):
        """Wątek rotacji rankingu"""
        self.wyczysc()
        time.sleep(0.2)

        index = 0
        while self.ranking_running:
            para = wyniki[index:index+2]

            if len(para) == 1:
                miejsce = index + 1
                czas = para[0]
                pakiet = create_ranking_packet(czas, miejsce, line=1)
                self.wyslij(pakiet)
                time.sleep(0.05)
                self.wyslij('clear_line2')

            elif len(para) == 2:
                miejsce1 = index + 1
                miejsce2 = index + 2
                czas1 = para[0]
                czas2 = para[1]

                pakiet1 = create_ranking_packet(czas1, miejsce1, line=1)
                self.wyslij(pakiet1)
                time.sleep(0.05)

                pakiet2 = create_ranking_packet(czas2, miejsce2, line=2)
                self.wyslij(pakiet2)

            time.sleep(3.0)

            index += 2
            if index >= len(wyniki):
                index = 0

    def pokaz_ranking(self, wyniki):
        """Pokaż ranking z rotacją"""
        if not self.polaczony or len(wyniki) == 0:
            return

        self.zatrzymaj_timer()
        self.zatrzymaj_ranking()

        if len(wyniki) <= 2:
            if len(wyniki) == 1:
                pakiet = create_ranking_packet(wyniki[0], 1, line=1)
                self.wyslij(pakiet)
            else:
                pakiet1 = create_ranking_packet(wyniki[0], 1, line=1)
                self.wyslij(pakiet1)
                time.sleep(0.05)
                pakiet2 = create_ranking_packet(wyniki[1], 2, line=2)
                self.wyslij(pakiet2)
        else:
            self.ranking_running = True
            self.ranking_thread = threading.Thread(
                target=self._ranking_worker,
                args=(wyniki,),
                daemon=True
            )
            self.ranking_thread.start()

    def zatrzymaj_ranking(self):
        """Zatrzymaj rotację rankingu"""
        self.ranking_running = False
        if self.ranking_thread and self.ranking_thread.is_alive():
            self.ranking_thread.join(timeout=2)


# ============================================================================
# CHRONOMETR - GŁÓWNA APLIKACJA
# ============================================================================

class Chronometr:
    """Aplikacja chronometru z obsługą tablicy LED"""

    def __init__(self, root):
        self.root = root
        self.root.title("⏱️ CHRONOMETR Z TABLICĄ LED")
        self.root.geometry("600x700")
        self.root.configure(bg='#2c3e50')

        # Zmienne
        self.running = False
        self.start_time = None
        self.elapsed_time = 0
        self.wyniki = []  # Lista czasów
        self.led = None

        # GUI
        self.setup_gui()

        # Pytaj o port LED
        self.root.after(500, self.setup_led)

    def setup_gui(self):
        """Tworzenie interfejsu"""

        # Nagłówek
        header = tk.Frame(self.root, bg='#34495e', height=60)
        header.pack(fill=tk.X)

        tk.Label(header, text="⏱️ CHRONOMETR", font=('Arial', 24, 'bold'),
                bg='#34495e', fg='white').pack(pady=10)

        # Wyświetlacz czasu
        time_frame = tk.Frame(self.root, bg='#1a252f', bd=5, relief=tk.RIDGE)
        time_frame.pack(pady=20, padx=20, fill=tk.X)

        self.time_label = tk.Label(time_frame, text="00:00.000",
                                   font=('Courier', 48, 'bold'),
                                   bg='#1a252f', fg='#3498db')
        self.time_label.pack(pady=20)

        # Przyciski kontroli
        btn_frame = tk.Frame(self.root, bg='#2c3e50')
        btn_frame.pack(pady=10)

        self.start_btn = tk.Button(btn_frame, text="▶ START",
                                   command=self.start,
                                   font=('Arial', 16, 'bold'),
                                   bg='#27ae60', fg='white',
                                   width=12, height=2)
        self.start_btn.grid(row=0, column=0, padx=5)

        self.stop_btn = tk.Button(btn_frame, text="⏸ STOP",
                                  command=self.stop,
                                  font=('Arial', 16, 'bold'),
                                  bg='#e74c3c', fg='white',
                                  width=12, height=2,
                                  state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1, padx=5)

        self.reset_btn = tk.Button(btn_frame, text="↻ RESET",
                                   command=self.reset,
                                   font=('Arial', 16, 'bold'),
                                   bg='#95a5a6', fg='white',
                                   width=12, height=2)
        self.reset_btn.grid(row=1, column=0, padx=5, pady=5)

        self.save_btn = tk.Button(btn_frame, text="💾 ZAPISZ",
                                  command=self.save_time,
                                  font=('Arial', 16, 'bold'),
                                  bg='#f39c12', fg='white',
                                  width=12, height=2,
                                  state=tk.DISABLED)
        self.save_btn.grid(row=1, column=1, padx=5, pady=5)

        # Przyciski LED
        led_frame = tk.LabelFrame(self.root, text=" 📺 TABLICA LED ",
                                 font=('Arial', 12, 'bold'),
                                 bg='#2c3e50', fg='white')
        led_frame.pack(pady=10, padx=20, fill=tk.X)

        led_btn_frame = tk.Frame(led_frame, bg='#2c3e50')
        led_btn_frame.pack(pady=10)

        self.led_status = tk.Label(led_btn_frame, text="● Brak tablicy",
                                   font=('Arial', 10), fg='gray', bg='#2c3e50')
        self.led_status.pack()

        tk.Button(led_btn_frame, text="📊 Pokaż ranking",
                 command=self.pokaz_ranking_led,
                 font=('Arial', 10), bg='#9b59b6', fg='white',
                 padx=10, pady=5).pack(side=tk.LEFT, padx=5, pady=5)

        tk.Button(led_btn_frame, text="🧹 Wyczyść",
                 command=self.wyczysc_led,
                 font=('Arial', 10), bg='#7f8c8d', fg='white',
                 padx=10, pady=5).pack(side=tk.LEFT, padx=5)

        # Lista wyników
        results_frame = tk.LabelFrame(self.root, text=" 🏆 WYNIKI ",
                                     font=('Arial', 12, 'bold'),
                                     bg='#2c3e50', fg='white')
        results_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = tk.Scrollbar(results_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.results_listbox = tk.Listbox(results_frame,
                                          font=('Courier', 12),
                                          bg='#34495e', fg='white',
                                          yscrollcommand=scrollbar.set,
                                          selectbackground='#3498db')
        self.results_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.config(command=self.results_listbox.yview)

        # Przycisk czyszczenia wyników
        tk.Button(results_frame, text="🗑️ Wyczyść wyniki",
                 command=self.clear_results,
                 font=('Arial', 10), bg='#c0392b', fg='white',
                 padx=10, pady=5).pack(pady=5)

    def setup_led(self):
        """Konfiguracja połączenia LED"""
        port = tk.simpledialog.askstring(
            "Tablica LED",
            "Podaj port tablicy LED (np. COM5, COM6)\n\n" +
            "Zostaw puste jeśli nie masz tablicy:",
            parent=self.root
        )

        if port and port.strip():
            self.led = TablicaLED(port.strip())
            if self.led.polacz():
                self.led_status.config(text="● Tablica połączona", fg='#27ae60')
                self.led.wyczysc()
            else:
                messagebox.showerror("Błąd", f"Nie udało się połączyć z tablicą na {port}")
                self.led = None
                self.led_status.config(text="● Brak tablicy", fg='gray')
        else:
            self.led_status.config(text="● Brak tablicy", fg='gray')

    def update_display(self):
        """Aktualizacja wyświetlacza"""
        if self.running:
            self.elapsed_time = time.time() - self.start_time

        minutes = int(self.elapsed_time // 60)
        seconds = int(self.elapsed_time % 60)
        milliseconds = int((self.elapsed_time % 1) * 1000)

        time_str = f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
        self.time_label.config(text=time_str)

        if self.running:
            self.root.after(10, self.update_display)

    def get_elapsed_time(self):
        """Zwraca aktualny czas (dla LED)"""
        if self.running:
            return time.time() - self.start_time
        return None

    def start(self):
        """Start chronometru"""
        if not self.running:
            self.running = True
            self.start_time = time.time()
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.save_btn.config(state=tk.DISABLED)
            self.time_label.config(fg='#27ae60')

            self.update_display()

            # LED: Start timera
            if self.led:
                self.led.start_timer(self.get_elapsed_time)

    def stop(self):
        """Stop chronometru"""
        if self.running:
            self.running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.save_btn.config(state=tk.NORMAL)
            self.time_label.config(fg='#e74c3c')

            # LED: Zatrzymaj timer
            if self.led:
                self.led.zatrzymaj_timer()
                # Pokaż końcowy czas
                self.led.pokaz_czas(self.elapsed_time)

    def reset(self):
        """Reset chronometru"""
        self.running = False
        self.elapsed_time = 0
        self.start_time = None
        self.time_label.config(text="00:00.000", fg='#3498db')
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.DISABLED)

        # LED: Wyczyść
        if self.led:
            self.led.zatrzymaj_timer()
            self.led.wyczysc()

    def save_time(self):
        """Zapisz czas do listy wyników"""
        if self.elapsed_time > 0:
            minutes = int(self.elapsed_time // 60)
            seconds = int(self.elapsed_time % 60)
            milliseconds = int((self.elapsed_time % 1) * 1000)
            time_str = f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

            self.wyniki.append(time_str)

            # Dodaj do listy
            miejsce = len(self.wyniki)
            self.results_listbox.insert(tk.END, f"  {miejsce}. {time_str}")
            self.results_listbox.see(tk.END)

            print(f"✅ Zapisano: {time_str}")

            # Reset i przygotuj do kolejnego
            self.reset()

    def clear_results(self):
        """Wyczyść wszystkie wyniki"""
        if messagebox.askyesno("Potwierdzenie", "Czy na pewno wyczyścić wszystkie wyniki?"):
            self.wyniki.clear()
            self.results_listbox.delete(0, tk.END)
            print("🗑️ Wyczyszczono wyniki")

    def pokaz_ranking_led(self):
        """Pokaż ranking na tablicy LED"""
        if not self.led:
            messagebox.showwarning("Uwaga", "Tablica LED nie jest połączona!")
            return

        if len(self.wyniki) == 0:
            messagebox.showinfo("Info", "Brak wyników do wyświetlenia!")
            return

        self.led.pokaz_ranking(self.wyniki)
        print(f"📊 Ranking wyświetlony na LED ({len(self.wyniki)} wyników)")

    def wyczysc_led(self):
        """Wyczyść tablicę LED"""
        if self.led:
            self.led.wyczysc()
            print("🧹 Tablica LED wyczyszczona")

    def on_closing(self):
        """Zamknięcie aplikacji"""
        if self.led:
            self.led.rozlacz()
        self.root.destroy()


# ============================================================================
# URUCHOMIENIE PROGRAMU
# ============================================================================

def main():
    root = tk.Tk()
    app = Chronometr(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    # Import dodatkowy dla dialogu
    import tkinter.simpledialog
    main()
