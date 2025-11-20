#!/usr/bin/env python3
"""
INTEGRACJA LED DISPLAY Z CHRONOMETREM
Dodatkowy kod do włączenia w chronometer_manager.py

INSTRUKCJA INTEGRACJI:
1. Dodać import na początku pliku
2. Dodać zmienne w __init__
3. Dodać GUI konfiguracji LED w setup_la_tab
4. Dodać wywołania LED w metodach LA
"""

# ============================================================================
# 1. IMPORT (dodać na początku pliku, po innych importach)
# ============================================================================
from led_display_complete import LEDDisplayManager

# ============================================================================
# 2. ZMIENNE W __init__ (dodać w ChronometerManager.__init__)
# ============================================================================
"""
# LED Display
self.led_manager = None  # LED Display Manager
self.led_enabled = False  # Czy tablica jest włączona
self.led_port = 'COM6'  # Port tablicy LED (domyślnie COM6, można zmienić)
self.led_num_lanes = 1  # 1 lub 2 linie czasów
self.led_brightness = 100  # Jasność 0-100%
self.led_event_name = "YO&GO ZAWODY"  # Nazwa zawodów
self.led_timer_thread = None  # Wątek aktualizacji timera na LED
self.led_timer_running = False  # Czy timer LED działa
"""

# ============================================================================
# 3. GUI KONFIGURACJI LED (dodać w setup_la_tab, po config_frame)
# ============================================================================
"""
        # === KONFIGURACJA TABLICY LED ===
        led_config_frame = tk.LabelFrame(self.la_tab, text=" 📺 TABLICA LED ",
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

        # Rząd 4: Nazwa zawodów
        led_row4 = tk.Frame(led_config_frame, bg='white')
        led_row4.pack(fill=tk.X, padx=10, pady=3)

        tk.Label(led_row4, text="Nazwa zawodów:", font=('Arial', 9), bg='white').pack(side=tk.LEFT, padx=3)

        self.led_event_name_var = tk.StringVar(value="YO&GO ZAWODY")
        self.led_event_name_entry = tk.Entry(led_row4, textvariable=self.led_event_name_var,
                                             width=25, font=('Arial', 9))
        self.led_event_name_entry.pack(side=tk.LEFT, padx=3)

        tk.Button(led_row4, text="Wyświetl nazwę", command=self.led_show_event_name,
                 font=('Arial', 8), bg='#607D8B', fg='white', padx=8, pady=2).pack(side=tk.LEFT, padx=5)
"""

# ============================================================================
# 4. METODY LED (dodać do klasy ChronometerManager)
# ============================================================================
"""
    def led_connect(self):
        '''Połączenie z tablicą LED'''
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

                    # Wyświetl nazwę zawodów
                    event_name = self.led_event_name_var.get()
                    if event_name:
                        self.led_manager.display.show_event_name(event_name)
                        time.sleep(2)
                        self.led_manager.display.clear_display()
                else:
                    messagebox.showerror("Błąd", f"Nie udało się połączyć z tablicą LED na {port}")
                    self.led_manager = None
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie udało się połączyć z tablicą LED:\n{e}")
                self.led_manager = None

    def led_set_brightness(self, value):
        '''Ustawienie jasności tablicy LED'''
        if self.led_enabled and self.led_manager:
            brightness = int(value)
            self.led_manager.display.set_brightness(brightness)
            print(f"💡 [LED] Jasność: {brightness}%")

    def led_show_event_name(self):
        '''Wyświetlenie nazwy zawodów na tablicy'''
        if not self.led_enabled or not self.led_manager:
            messagebox.showwarning("Uwaga", "Tablica LED nie jest połączona!")
            return

        event_name = self.led_event_name_var.get()
        if event_name:
            self.led_manager.display.show_event_name(event_name)
            print(f"📺 [LED] Wyświetlono nazwę: {event_name}")

    def led_update_timer_worker(self):
        '''Wątek aktualizacji timera na tablicy LED'''
        while self.led_timer_running and self.la_start_absolute_time:
            elapsed = time.time() - self.la_start_absolute_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            milliseconds = int((elapsed % 1) * 1000)

            # Format MM:SS.mmm
            time_str = f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

            # Wyślij na tablicę
            num_lanes = self.led_lanes_var.get()

            if num_lanes == 1:
                # Jedna linia
                from led_display_complete import create_time_packet_line1
                packet = create_time_packet_line1(time_str)
                self.led_manager.display.send_packet(packet, delay=0)
            else:
                # Dwie linie - ten sam czas na obu
                from led_display_complete import create_time_packet_line1, create_time_packet_line2
                packet1 = create_time_packet_line1(time_str)
                packet2 = create_time_packet_line2(time_str)
                self.led_manager.display.send_packet(packet1, delay=0)
                time.sleep(0.05)
                self.led_manager.display.send_packet(packet2, delay=0)

            time.sleep(0.1)  # Aktualizacja co 100ms

    def led_start_timer(self):
        '''Uruchomienie timera na tablicy LED'''
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
        '''Zatrzymanie timera na tablicy LED'''
        self.led_timer_running = False
        if self.led_timer_thread and self.led_timer_thread.is_alive():
            self.led_timer_thread.join(timeout=1)
        print("⏹️ [LED] Timer zatrzymany na tablicy")

    def led_show_ranking(self):
        '''Wyświetlenie rankingu na tablicy LED'''
        if not self.led_enabled or not self.led_manager:
            return

        if not self.la_results:
            print("⚠️ [LED] Brak wyników do rankingu")
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
                'lane': i,  # Numer miejsca
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
        '''Czyszczenie tablicy LED'''
        if self.led_enabled and self.led_manager:
            self.led_manager.stop_rotation()  # Zatrzymaj ranking jeśli był
            self.led_manager.display.clear_display()
            print("🧹 [LED] Wyczyszczono tablicę")
"""

# ============================================================================
# 5. MODYFIKACJE W METODACH LA (dodać wywołania LED)
# ============================================================================
"""
# W la_next_race() (na początku metody):
        # LED: Wyczyść tablicę
        self.led_clear()

# W la_manual_start() (po ustawieniu la_race_active = True):
        # LED: Uruchom timer
        self.led_start_timer()

# W process_la_crossing() (przy kanale 1 - START, po la_race_active = True):
        # LED: Uruchom timer
        self.led_start_timer()

# W process_la_crossing() (gdy ostatni zawodnik kończy, po self.la_add_to_history()):
        # LED: Zatrzymaj timer i uruchom ranking
        self.led_stop_timer()
        time.sleep(0.5)
        self.led_show_ranking()

# W la_reset_race() (na początku metody):
        # LED: Wyczyść tablicę i zatrzymaj timer
        self.led_stop_timer()
        self.led_clear()
"""

print("Kod integracji LED Display przygotowany!")
print("Zintegruj go z chronometer_manager.py zgodnie z instrukcjami powyżej.")
