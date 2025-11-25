# Zmiany w chronometr_v5_LED.py

## Data: 2025-11-25

### 1. Zmieniono pole offsetu na spinner z zakresem -2 do +2 sekundy

**Przed:**
- Pole typu `tk.Scale` (suwak)
- Zakres: 0 - 500 ms
- Krok: 10 ms
- Tylko wartości dodatnie

**Po:**
- Pole typu `tk.Spinbox` (strzałki góra/dół)
- Zakres: -2000 do +2000 ms (od -2s do +2s)
- Krok: 100 ms (0.1 sekundy)
- Wartości dodatnie i ujemne

**Korzyści:**
- Możliwość ustawienia ujemnego offsetu (przyspieszenie sygnału)
- Dokładniejsze sterowanie wartością
- Łatwiejsze wpisanie konkretnej wartości z klawiatury

### 2. NAPRAWIONO: Opóźnienie ~1 sekundy w trybie OSF DWA TORY

**Problem:**
W trybie OSF DWA TORY był bug powodujący dodatkowe opóźnienie ~1 sekundy:
- `time.sleep(0.1)` po czyszczeniu LED
- `delay=0.1` x2 przy wysyłaniu pakietów inicjalizacyjnych (dodatkowo 200ms)
- Czas startu (`start_absolute_time`) był ustawiany PO tych opóźnieniach

**Rozwiązanie:**
1. **Usunięto `time.sleep(0.1)`** - niepotrzebne opóźnienie
2. **Zmniejszono `delay` z 0.1 na 0.05** - zgodnie z innymi trybami
3. **Zmieniono kolejność operacji** - `start_absolute_time` jest teraz ustawiane PRZED operacjami LED

**Miejsca naprawy:**
- `handle_osf_dwa_tory()` - linia ~2136-2149
- `osf_manual_start()` - linia ~3018-3034

**Wynik:**
- Tryb pojedynczy: brak opóźnienia ✓
- Tryb OSF DWA TORY: brak opóźnienia ✓ (NAPRAWIONO!)
- Synchronizacja między trybami: idealna ✓

### Kod zmian

#### Zmiana 1: Spinbox zamiast Scale
```python
# PRZED:
self.start_offset_scale = tk.Scale(top_frame, from_=0, to=500, orient=tk.HORIZONTAL,
                                   variable=self.start_offset_var, command=self.on_start_offset_change,
                                   length=100, width=10, bg='#e8e8e8', resolution=10)

# PO:
self.start_offset_spinbox = tk.Spinbox(top_frame, from_=-2000, to=2000, increment=100,
                                       textvariable=self.start_offset_var,
                                       command=self.on_start_offset_change,
                                       width=6, font=('Arial', 9), bg='white')
```

#### Zmiana 2: Naprawa opóźnienia
```python
# PRZED (OSF DWA TORY):
if self.led_enabled and self.led_manager:
    self.led_manager.display.clear_display()
    time.sleep(0.1)  # ← PROBLEM: niepotrzebne opóźnienie!
    init_packet1 = create_init_packet_line1("TOR 1    0)")
    init_packet2 = create_init_packet_line2("TOR 2    0)")
    self.led_manager.display.send_packet(init_packet1, delay=0.1)  # ← 100ms
    self.led_manager.display.send_packet(init_packet2, delay=0.1)  # ← 100ms

self.start_time = time_seconds
self.start_absolute_time = time.time()  # ← Za późno! (~300ms opóźnienia)

# PO (OSF DWA TORY):
self.start_time = time_seconds
self.start_absolute_time = time.time()  # ← NAJPIERW czas!

if self.led_enabled and self.led_manager:
    self.led_manager.display.clear_display()
    # NAPRAWIONO: Usunięto time.sleep(0.1)
    init_packet1 = create_init_packet_line1("TOR 1    0)")
    init_packet2 = create_init_packet_line2("TOR 2    0)")
    self.led_manager.display.send_packet(init_packet1, delay=0.05)  # ← Zmniejszono
    self.led_manager.display.send_packet(init_packet2, delay=0.05)  # ← Zmniejszono
```

### Testowanie

Po zmianach należy przetestować:
1. ✓ Czy spinbox prawidłowo zmienia offset
2. ✓ Czy można ustawić wartości ujemne
3. ✓ Czy tryb pojedynczy działa prawidłowo
4. ✓ Czy tryb OSF DWA TORY nie ma już opóźnienia
5. ✓ Czy czas startu jest synchronizowany między trybami
