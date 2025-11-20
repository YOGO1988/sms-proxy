#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=====================================================
TABLICA LED - PROSTY SKRYPT DO TESTOWANIA
=====================================================

WSZYSTKO W JEDNYM PLIKU - gotowe do użycia!

Funkcje:
- Wyświetlanie czasów na 1 lub 2 liniach
- Ranking (numery miejsc + czasy)
- Timer działający w czasie rzeczywistym
- Jasność 0-100%
- Czyszczenie tablicy

INSTRUKCJA:
1. Podłącz tablicę LED do komputera (USB/RS232)
2. Uruchom: python tablica_led_prosty.py
3. Podaj numer portu (np. COM5, COM6)
4. Użyj komend z menu
"""

import serial
import time
import threading


# ============================================================================
# FUNKCJE CRC I PAKIETY
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
    """
    Tworzy pakiet z czasem dla linii 1
    time_str: czas w formacie "00:07.787"
    """
    base = bytearray.fromhex('1B 07 3A 00 51 8B 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 34 36 37 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))

    # Formatuj czas: "00:07.787" -> "00'07".787"
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

    # Tekst: 34 bajty (bytes 22-55)
    text_padded = (formatted + "  - ").ljust(34)[:34]
    base[22:56] = text_padded.encode('ascii', errors='replace')

    # Przelicz CRC
    base[4] = 0
    base[5] = 0
    crc = calculate_crc16(bytes(base))
    base[4] = crc & 0xFF
    base[5] = (crc >> 8) & 0xFF

    return bytes(base)


def create_time_packet_line2(time_str: str) -> bytes:
    """
    Tworzy pakiet z czasem dla linii 2
    time_str: czas w formacie "00:10.362"
    """
    base = bytearray.fromhex('1B 07 3A 00 51 8B 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 30 30 27 30 37 22 2E 34 36 37 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))

    # Formatuj czas
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

    # Tekst: 34 bajty
    text_padded = (formatted + "  - ").ljust(34)[:34]
    base[22:56] = text_padded.encode('ascii', errors='replace')

    # Przelicz CRC
    base[4] = 0
    base[5] = 0
    crc = calculate_crc16(bytes(base))
    base[4] = crc & 0xFF
    base[5] = (crc >> 8) & 0xFF

    return bytes(base)


def create_ranking_packet(time_str: str, place: int, line: int) -> bytes:
    """
    Tworzy pakiet rankingowy (miejsce + czas)
    time_str: czas "00:07.787"
    place: numer miejsca (1, 2, 3...)
    line: linia (1 lub 2)
    """
    if line == 1:
        base = bytearray.fromhex('1B 07 3E 00 A1 2A 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 37 38 37 20 54 4F 52 20 31 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))
    else:
        base = bytearray.fromhex('1B 07 3E 00 8F 5C 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 30 30 27 31 30 22 2E 33 36 32 20 54 4F 52 20 32 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', ''))

    # Formatuj czas
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

    # Tekst: numer miejsca + czas
    place_text = f"{place}."
    display_text = f"{place_text} {formatted}".ljust(38)[:38]
    base[22:60] = display_text.encode('ascii', errors='replace')

    # Przelicz CRC
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
    """Obsługa tablicy LED - wszystko w jednej klasie"""

    # Gotowe pakiety
    PAKIETY = {
        'clear_line1': bytes.fromhex('1B 07 54 00 14 75 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 2D 2D 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),
        'clear_line2': bytes.fromhex('1B 07 54 00 60 FC 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 2D 2D 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A'.replace(' ', '')),
        'brightness_0': bytes.fromhex('1B 06 0C 00 FB E8 00 00 00 00 0D 0A'.replace(' ', '')),
        'brightness_15': bytes.fromhex('1B 06 0C 00 15 3C 00 00 0F 00 0D 0A'.replace(' ', '')),
    }

    def __init__(self, port='COM5'):
        self.port = port
        self.ser = None
        self.polaczony = False
        self.timer_thread = None
        self.timer_running = False
        self.timer_start_time = None
        self.ranking_thread = None
        self.ranking_running = False

    def polacz(self):
        """Połącz z tablicą LED"""
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
            print(f"✅ Połączono z tablicą LED na {self.port}")

            # Ustaw jasność na max
            self.jasnosc(100)
            return True
        except Exception as e:
            print(f"❌ Błąd połączenia: {e}")
            self.polaczony = False
            return False

    def rozlacz(self):
        """Rozłącz tablicę"""
        self.zatrzymaj_timer()
        self.zatrzymaj_ranking()
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.polaczony = False
        print("✅ Rozłączono")

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
            print(f"❌ Błąd wysyłania: {e}")
            return False

    def wyczysc(self):
        """Wyczyść całą tablicę"""
        print("🧹 Czyszczę tablicę...")
        self.zatrzymaj_timer()
        self.zatrzymaj_ranking()
        self.wyslij('clear_line1')
        time.sleep(0.05)
        self.wyslij('clear_line2')

    def jasnosc(self, procent):
        """Ustaw jasność 0-100%"""
        procent = max(0, min(100, procent))
        print(f"💡 Jasność: {procent}%")

        if procent == 0:
            self.wyslij('brightness_0')
        else:
            self.wyslij('brightness_15')

    def pokaz_czas(self, czas, linia=1):
        """
        Pokaż czas na określonej linii
        czas: string np. "00:07.787"
        linia: 1 lub 2
        """
        if linia == 1:
            pakiet = create_time_packet_line1(czas)
        else:
            pakiet = create_time_packet_line2(czas)

        self.wyslij(pakiet)
        print(f"⏱️  Linia {linia}: {czas}")

    def pokaz_dwa_czasy(self, czas1, czas2):
        """Pokaż dwa czasy (linia 1 i 2)"""
        print("⏱️  Pokazuję dwa czasy:")
        print(f"   Linia 1: {czas1}")
        print(f"   Linia 2: {czas2}")

        pakiet1 = create_time_packet_line1(czas1)
        self.wyslij(pakiet1)
        time.sleep(0.05)

        pakiet2 = create_time_packet_line2(czas2)
        self.wyslij(pakiet2)

    def _timer_worker(self):
        """Wątek timera"""
        self.timer_start_time = time.time()
        print("🏁 START TIMERA!")

        while self.timer_running:
            elapsed = time.time() - self.timer_start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            milliseconds = int((elapsed % 1) * 1000)

            time_str = f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

            pakiet = create_time_packet_line1(time_str)
            self.wyslij(pakiet, delay=0)

            time.sleep(0.1)  # Aktualizacja co 100ms

    def start_timer(self):
        """Uruchom timer"""
        self.zatrzymaj_timer()
        self.zatrzymaj_ranking()
        self.wyczysc()
        time.sleep(0.5)

        print("\n🏁 Naciśnij ENTER aby wystartować timer...")
        input()

        self.timer_running = True
        self.timer_thread = threading.Thread(target=self._timer_worker, daemon=True)
        self.timer_thread.start()

    def zatrzymaj_timer(self):
        """Zatrzymaj timer"""
        if self.timer_running:
            self.timer_running = False
            if self.timer_thread:
                self.timer_thread.join(timeout=1)

            # Oblicz końcowy czas
            if self.timer_start_time:
                final_time = time.time() - self.timer_start_time
                minutes = int(final_time // 60)
                seconds = int(final_time % 60)
                milliseconds = int((final_time % 1) * 1000)
                time_str = f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
                print(f"🏁 META! Czas: {time_str}")
                return time_str
        return None

    def _ranking_worker(self, wyniki):
        """Wątek rotacji rankingu"""
        print(f"🔄 Ranking: {len(wyniki)} zawodników")

        self.wyczysc()
        time.sleep(0.2)

        index = 0
        while self.ranking_running:
            # Pobierz parę wyników (2 na raz)
            para = wyniki[index:index+2]

            if len(para) == 1:
                # Jeden wynik
                miejsce = index + 1
                czas = para[0]
                pakiet = create_ranking_packet(czas, miejsce, line=1)
                self.wyslij(pakiet)
                time.sleep(0.05)
                self.wyslij('clear_line2')
                print(f"  📊 Miejsce {miejsce}: {czas}")

            elif len(para) == 2:
                # Dwa wyniki
                miejsce1 = index + 1
                miejsce2 = index + 2
                czas1 = para[0]
                czas2 = para[1]

                pakiet1 = create_ranking_packet(czas1, miejsce1, line=1)
                self.wyslij(pakiet1)
                time.sleep(0.05)

                pakiet2 = create_ranking_packet(czas2, miejsce2, line=2)
                self.wyslij(pakiet2)

                print(f"  📊 Miejsca {miejsce1}-{miejsce2}:")
                print(f"     {miejsce1}. {czas1}")
                print(f"     {miejsce2}. {czas2}")

            # Czekaj 3 sekundy
            time.sleep(3.0)

            # Następna para
            index += 2
            if index >= len(wyniki):
                index = 0
                print("  🔄 Powrót do początku")

    def pokaz_ranking(self, wyniki):
        """
        Pokaż ranking z rotacją
        wyniki: lista stringów z czasami, np. ["00:07.787", "00:10.362", "00:12.456"]
        """
        self.zatrzymaj_timer()
        self.zatrzymaj_ranking()

        if len(wyniki) == 0:
            print("⚠️  Brak wyników!")
            return

        if len(wyniki) <= 2:
            # Bez rotacji
            if len(wyniki) == 1:
                pakiet = create_ranking_packet(wyniki[0], 1, line=1)
                self.wyslij(pakiet)
                print(f"🏆 1. {wyniki[0]}")
            else:
                pakiet1 = create_ranking_packet(wyniki[0], 1, line=1)
                self.wyslij(pakiet1)
                time.sleep(0.05)
                pakiet2 = create_ranking_packet(wyniki[1], 2, line=2)
                self.wyslij(pakiet2)
                print(f"🏆 1. {wyniki[0]}")
                print(f"🏆 2. {wyniki[1]}")
        else:
            # Z rotacją (3+ wyników)
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
# GŁÓWNY PROGRAM - MENU
# ============================================================================

def main():
    print("=" * 70)
    print("                    TABLICA LED - PROSTY PROGRAM")
    print("=" * 70)
    print()
    print("Ten program obsługuje tablicę LED w jednym pliku!")
    print()

    # Pytaj o port
    port = input("Podaj port tablicy (np. COM5, COM6): ").strip()
    if not port:
        port = "COM5"

    # Połącz
    tablica = TablicaLED(port)
    if not tablica.polacz():
        print("\n❌ Nie udało się połączyć!")
        print("Sprawdź:")
        print("  - Czy tablica jest podłączona?")
        print("  - Czy numer portu jest poprawny?")
        print("  - Czy tablica jest włączona?")
        return

    print("\n✅ Połączono z tablicą!")
    print("\n" + "=" * 70)
    print("KOMENDY:")
    print("=" * 70)
    print("  1       - Pokaż jeden czas")
    print("  2       - Pokaż dwa czasy")
    print("  timer   - Uruchom timer (ENTER=start, ENTER=stop)")
    print("  ranking - Pokaż ranking (3+ wyników z rotacją)")
    print("  jasnosc - Zmień jasność")
    print("  wyczysc - Wyczyść tablicę")
    print("  quit    - Wyjście")
    print("=" * 70)

    try:
        while True:
            cmd = input("\n> ").strip().lower()

            if cmd == 'quit' or cmd == 'q':
                break

            elif cmd == '1':
                czas = input("Podaj czas (np. 00:07.787): ").strip()
                if czas:
                    tablica.pokaz_czas(czas, linia=1)

            elif cmd == '2':
                czas1 = input("Czas linia 1 (np. 00:07.787): ").strip()
                czas2 = input("Czas linia 2 (np. 00:10.362): ").strip()
                if czas1 and czas2:
                    tablica.pokaz_dwa_czasy(czas1, czas2)

            elif cmd == 'timer':
                print("\n⏱️  TIMER:")
                print("  1. Naciśnij ENTER aby wystartować")
                print("  2. Naciśnij ENTER ponownie aby zatrzymać")
                tablica.start_timer()
                input("\n🏁 Naciśnij ENTER aby zatrzymać...")
                czas_koncowy = tablica.zatrzymaj_timer()
                if czas_koncowy:
                    print(f"✅ Zapisany czas: {czas_koncowy}")

            elif cmd == 'ranking':
                print("\n🏆 RANKING:")
                print("Podaj czasy (po kolei, od najszybszego):")
                print("Naciśnij ENTER bez podawania czasu aby zakończyć")

                wyniki = []
                i = 1
                while True:
                    czas = input(f"  Miejsce {i}: ").strip()
                    if not czas:
                        break
                    wyniki.append(czas)
                    i += 1

                if wyniki:
                    tablica.pokaz_ranking(wyniki)
                    if len(wyniki) > 2:
                        print("\n⏱️  Rotacja działa... (wpisz 'wyczysc' aby zatrzymać)")

            elif cmd == 'jasnosc':
                procent = input("Jasność 0-100%: ").strip()
                try:
                    procent = int(procent)
                    tablica.jasnosc(procent)
                except:
                    print("❌ Podaj liczbę 0-100")

            elif cmd == 'wyczysc':
                tablica.wyczysc()

            else:
                print("❌ Nieznana komenda. Wpisz: 1, 2, timer, ranking, jasnosc, wyczysc, quit")

    except KeyboardInterrupt:
        print("\n\nPrzerwano przez użytkownika")

    finally:
        print("\n🔴 Zamykam...")
        tablica.rozlacz()
        print("✅ Gotowe!")


if __name__ == "__main__":
    main()
