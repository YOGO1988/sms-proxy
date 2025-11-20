# 🚀 INSTRUKCJA INTEGRACJI LED DISPLAY Z CHRONOMETREM

## 📋 KROK 1: Dodaj import na początku pliku

Na początku pliku (po `import time`), dodaj:

```python
# === IMPORT LED DISPLAY ===
from led_display_complete import LEDDisplayManager, create_time_packet_line1, create_time_packet_line2
```

---

## 📋 KROK 2: Dodaj zmienne LED w `__init__`

W metodzie `ChronometerManager.__init__`, **na końcu** (po wszystkich zmiennych), dodaj:

```python
        # ==============================
        # ZMIENNE DLA TABLICY LED
        # ==============================
        self.led_manager = None  # LED Display Manager
        self.led_enabled = False  # Czy tablica jest włączona
        self.led_port = None  # Port tablicy LED
        self.led_timer_thread = None  # Wątek aktualizacji timera na LED
        self.led_timer_running = False  # Czy timer LED działa
```

---

## 📋 KROK 3: Dodaj wybór portu LED w `setup_gui`

W metodzie `setup_gui()`, w sekcji **top_frame** (zaraz po `self.status_label.pack`), dodaj:

```python
        # === PORT LED ===
        tk.Label(top_frame, text="Port LED:", font=('Arial', 9), bg='#e8e8e8').pack(side=tk.LEFT, padx=(20, 3))

        self.led_port_var = tk.StringVar()
        self.led_port_combo = ttk.Combobox(top_frame, textvariable=self.led_port_var, width=10,
                                          state='readonly', font=('Arial', 9))
        self.led_port_combo.pack(side=tk.LEFT, padx=3)

        self.led_connect_btn = tk.Button(top_frame, text="🔌 LED", command=self.led_toggle_connection,
                                         font=('Arial', 9, 'bold'), bg='#2196F3', fg='white', padx=8)
        self.led_connect_btn.pack(side=tk.LEFT, padx=3)

        self.led_status_label = tk.Label(top_frame, text="● LED OFF", font=('Arial', 8),
                                         fg='gray', bg='#e8e8e8')
        self.led_status_label.pack(side=tk.LEFT, padx=5)
```

---

## 📋 KROK 4: Dodaj konfigurację LED w zakładce LA

W metodzie `setup_la_tab()`, **ZARAZ PO** `config_frame.pack(...)` (po pierwszej ramce konfiguracji), dodaj:

```python
        # === KONFIGURACJA TABLICY LED ===
        led_config_frame = tk.LabelFrame(self.la_tab, text=" 📺 TABLICA LED ",
                                        font=('Arial', 9, 'bold'), bg='white',
                                        relief=tk.RIDGE, bd=2)
        led_config_frame.pack(fill=tk.X, padx=10, pady=3)

        # Rząd 1: Liczba linii + Jasność
        led_row1 = tk.Frame(led_config_frame, bg='white')
        led_row1.pack(fill=tk.X, padx=10, pady=3)

        tk.Label(led_row1, text="Liczba linii:", font=('Arial', 9), bg='white').pack(side=tk.LEFT, padx=3)

        self.led_lanes_var = tk.IntVar(value=1)
        tk.Radiobutton(led_row1, text="1 meta", variable=self.led_lanes_var, value=1,
                      font=('Arial', 9), bg='white').pack(side=tk.LEFT, padx=3)
        tk.Radiobutton(led_row1, text="2 mety", variable=self.led_lanes_var, value=2,
                      font=('Arial', 9), bg='white').pack(side=tk.LEFT, padx=3)

        tk.Label(led_row1, text="  Jasność:", font=('Arial', 9), bg='white').pack(side=tk.LEFT, padx=(15, 3))

        self.led_brightness_var = tk.IntVar(value=100)
        self.led_brightness_scale = tk.Scale(led_row1, from_=0, to=100, orient=tk.HORIZONTAL,
                                             variable=self.led_brightness_var, length=120,
                                             command=self.led_set_brightness)
        self.led_brightness_scale.pack(side=tk.LEFT, padx=3)

        tk.Label(led_row1, textvariable=self.led_brightness_var, font=('Arial', 9),
                bg='white', width=3).pack(side=tk.LEFT)
        tk.Label(led_row1, text="%", font=('Arial', 9), bg='white').pack(side=tk.LEFT)

        # Rząd 2: Nazwa zawodów
        led_row2 = tk.Frame(led_config_frame, bg='white')
        led_row2.pack(fill=tk.X, padx=10, pady=3)

        tk.Label(led_row2, text="Nazwa zawodów:", font=('Arial', 9), bg='white').pack(side=tk.LEFT, padx=3)

        self.led_event_name_var = tk.StringVar(value="YO&GO ZAWODY")
        self.led_event_name_entry = tk.Entry(led_row2, textvariable=self.led_event_name_var,
                                             width=25, font=('Arial', 9))
        self.led_event_name_entry.pack(side=tk.LEFT, padx=3)

        tk.Button(led_row2, text="Wyświetl", command=self.led_show_event_name,
                 font=('Arial', 8), bg='#607D8B', fg='white', padx=8, pady=2).pack(side=tk.LEFT, padx=5)

        tk.Button(led_row2, text="Wyczyść", command=self.led_clear,
                 font=('Arial', 8), bg='#f44336', fg='white', padx=8, pady=2).pack(side=tk.LEFT, padx=3)
```

---

## 📋 KROK 5: Dodaj metody LED (WSZYSTKIE NA KONIEC KLASY)

Na **KOŃCU klasy** `ChronometerManager`, przed `def __del__`, dodaj wszystkie metody LED:

```python
    # ============================================================================
    # METODY LED DISPLAY
    # ============================================================================

    def led_toggle_connection(self):
        """Połącz/Rozłącz tablicę LED"""
        if not self.led_enabled:
            self.led_connect()
        else:
            self.led_disconnect()

    def led_connect(self):
        """Połączenie z tablicą LED"""
        port = self.led_port_var.get()
        if not port:
            messagebox.showwarning("Brak portu", "Wybierz port dla tablicy LED!")
            return

        try:
            self.led_manager = LEDDisplayManager(port, 9600)
            if self.led_manager.initialize():
                self.led_enabled = True
                self.led_port = port
                self.led_status_label.config(text="● LED ON", fg='green')
                self.led_connect_btn.config(bg='#f44336')

                # Ustaw jasność
                brightness = self.led_brightness_var.get()
                self.led_manager.display.set_brightness(brightness)

                print(f"✅ [LED] Połączono tablicę na {port}")
                messagebox.showinfo("LED", f"Połączono z tablicą LED na {port}")
            else:
                messagebox.showerror("Błąd", f"Nie udało się połączyć z tablicą LED na {port}")
                self.led_manager = None
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd połączenia z tablicą LED:\n{e}")
            self.led_manager = None

    def led_disconnect(self):
        """Rozłączenie tablicy LED"""
        if self.led_manager:
            self.led_stop_timer()
            self.led_manager.shutdown()
            self.led_manager = None

        self.led_enabled = False
        self.led_status_label.config(text="● LED OFF", fg='gray')
        self.led_connect_btn.config(bg='#2196F3')
        print("🔴 [LED] Rozłączono tablicę LED")

    def led_set_brightness(self, value):
        """Ustawienie jasności tablicy LED"""
        if self.led_enabled and self.led_manager:
            brightness = int(value)
            self.led_manager.display.set_brightness(brightness)

    def led_show_event_name(self):
        """Wyświetlenie nazwy zawodów na tablicy"""
        if not self.led_enabled or not self.led_manager:
            messagebox.showwarning("Uwaga", "Tablica LED nie jest połączona!")
            return

        event_name = self.led_event_name_var.get()
        if event_name:
            self.led_manager.display.show_event_name(event_name)
            print(f"📺 [LED] Nazwa: {event_name}")

    def led_update_timer_worker(self):
        """Wątek aktualizacji timera na tablicy LED"""
        while self.led_timer_running and self.la_start_absolute_time:
            elapsed = time.time() - self.la_start_absolute_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            milliseconds = int((elapsed % 1) * 1000)

            # Format MM:SS.mmm
            time_str = f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

            # Wyślij na tablicę
            num_lanes = self.led_lanes_var.get()

            try:
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
            except:
                pass  # Ignoruj błędy komunikacji

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
        print("⏱️ [LED] Timer uruchomiony")

    def led_stop_timer(self):
        """Zatrzymanie timera na tablicy LED"""
        self.led_timer_running = False
        if self.led_timer_thread and self.led_timer_thread.is_alive():
            self.led_timer_thread.join(timeout=1)

    def led_show_ranking(self):
        """Wyświetlenie rankingu na tablicy LED"""
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
        print(f"🏆 [LED] Ranking uruchomiony ({len(results)} zawodników)")

    def led_clear(self):
        """Czyszczenie tablicy LED"""
        if self.led_enabled and self.led_manager:
            self.led_stop_timer()
            self.led_manager.stop_rotation()  # Zatrzymaj ranking jeśli był
            self.led_manager.display.clear_display()
            print("🧹 [LED] Wyczyszczono tablicę")
```

---

## 📋 KROK 6: Zmodyfikuj metody LA

Dodaj wywołania LED w odpowiednich miejscach:

### 6.1 W `refresh_ports()` - odśwież też porty LED:

```python
    def refresh_ports(self):
        """Odświeżanie listy portów"""
        ports = serial.tools.list_ports.comports()
        port_list = [port.device for port in ports]

        # Chronometr
        self.port_combo['values'] = port_list
        if port_list:
            self.port_combo.current(0)

        # LED
        self.led_port_combo['values'] = port_list
        if len(port_list) > 1:
            self.led_port_combo.current(1)  # Domyślnie drugi port
        elif port_list:
            self.led_port_combo.current(0)
```

### 6.2 W `la_next_race()` - na początku metody:

```python
    def la_next_race(self):
        """KOLEJNY BIEG LA"""
        # LED: Wyczyść tablicę
        self.led_clear()

        # ... reszta kodu bez zmian ...
```

### 6.3 W `la_manual_start()` - po ustawieniu `la_race_active = True`:

```python
        # ... kod ustawiający la_race_active = True ...

        # LED: Uruchom timer
        self.led_start_timer()

        # ... reszta kodu bez zmian ...
```

### 6.4 W `process_la_crossing()` - w dwóch miejscach:

**a) Przy kanale 1 (START), po `la_race_active = True`:**

```python
                    self.la_race_active = True
                    # ... kod ...

                    # LED: Uruchom timer
                    self.led_start_timer()

                    # Teraz przetwórz to przecięcie
                    self.process_la_crossing(channel, time_seconds)
```

**b) Gdy ostatni zawodnik kończy, po `self.la_add_to_history()`:**

```python
                    # Dodaj do historii
                    self.la_add_to_history()

                    # LED: Zatrzymaj timer i uruchom ranking
                    self.led_stop_timer()
                    time.sleep(0.5)
                    self.led_show_ranking()

                    if self.la_log_file:
                        # ... kod logu ...
```

### 6.5 W `la_reset_race()` - na początku metody:

```python
    def la_reset_race(self):
        """RESET biegu LA"""
        # LED: Wyczyść tablicę i zatrzymaj timer
        self.led_stop_timer()
        self.led_clear()

        # ... reszta kodu bez zmian ...
```

---

## ✅ GOTOWE!

Po dodaniu wszystkich zmian:
1. Zapisz plik
2. Uruchom program
3. Wybierz porty: jeden dla chronometru, drugi dla tablicy LED
4. Połącz oba urządzenia
5. Testuj w zakładce LA!

---

## 🧪 TEST:

1. **Połącz chronometr i tablicę LED**
2. **W zakładce LA:**
   - Ustaw liczbę zawodników
   - Wybierz 1 lub 2 mety (linie)
   - Kliknij "Kolejny bieg"
3. **Start biegu** - na tablicy pojawi się timer
4. **Zawodnicy kończą** - czasy się zapisują
5. **Ostatni zawodnik** - automatycznie uruchamia się ranking
6. **Kolejny bieg** - tablica się czyści

---

## 📞 POMOC:

Jeśli coś nie działa, sprawdź:
- Czy oba porty są poprawnie wybrane
- Czy tablica LED jest połączona (status "● LED ON")
- Czy w konsoli są komunikaty błędów
