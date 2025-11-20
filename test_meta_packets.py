#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analiza pakietów META (TOR 1, TOR 2)
"""

# Pakiet TIME (58 bajtów)
TIME_BASE = bytes.fromhex('1B 07 3A 00 51 8B 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 34 36 37 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A')

# Pakiet META TOR 1 (62 bajty)
TIME_META_TOR1 = bytes.fromhex('1B 07 3E 00 A1 2A 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 37 38 37 20 54 4F 52 20 31 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A')

# Pakiet META TOR 2 (62 bajty)
TIME_META_TOR2 = bytes.fromhex('1B 07 3E 00 8F 5C 00 00 01 00 00 00 00 00 00 00 00 00 10 00 0A 00 30 30 27 31 30 22 2E 33 36 32 20 54 4F 52 20 32 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A')

print("="*70)
print("ANALIZA PAKIETÓW META")
print("="*70)

print(f"\nTIME BASE:      {len(TIME_BASE)} bajtów")
print(f"META TOR 1:     {len(TIME_META_TOR1)} bajtów")
print(f"META TOR 2:     {len(TIME_META_TOR2)} bajtów")

print(f"\nRóżnica: {len(TIME_META_TOR1) - len(TIME_BASE)} bajtów")

# Porównaj strukturę
print("\n" + "="*70)
print("STRUKTURA:")
print("="*70)

print("\nHeader (bajty 0-3):")
print(f"  TIME:      {' '.join(f'{b:02X}' for b in TIME_BASE[0:4])}")
print(f"  META TOR1: {' '.join(f'{b:02X}' for b in TIME_META_TOR1[0:4])}")
print(f"  META TOR2: {' '.join(f'{b:02X}' for b in TIME_META_TOR2[0:4])}")
print(f"  Różnica: Bajt 2 = 0x3A (TIME) vs 0x3E (META)")

print("\nTekst TIME (bajty 22-55):")
text_time = TIME_BASE[22:56].decode('ascii', errors='replace')
print(f"  '{text_time}'")
print(f"  Długość: {len(text_time)} znaków")

print("\nTekst META TOR 1 (bajty 22-?):")
text_meta1 = TIME_META_TOR1[22:60].decode('ascii', errors='replace')
print(f"  '{text_meta1}'")
print(f"  Długość: {len(text_meta1)} znaków")

print("\nTekst META TOR 2 (bajty 22-?):")
text_meta2 = TIME_META_TOR2[22:60].decode('ascii', errors='replace')
print(f"  '{text_meta2}'")
print(f"  Długość: {len(text_meta2)} znaków")

print("\nKońcówka TIME (bajty 56-57):")
print(f"  {' '.join(f'{b:02X}' for b in TIME_BASE[56:58])}")

print("\nKońcówka META TOR 1 (bajty 60-61):")
print(f"  {' '.join(f'{b:02X}' for b in TIME_META_TOR1[60:62])}")

print("\nKońcówka META TOR 2 (bajty 60-61):")
print(f"  {' '.join(f'{b:02X}' for b in TIME_META_TOR2[60:62])}")

# Sprawdź gdzie jest różnica
print("\n" + "="*70)
print("GDZIE JEST 4 DODATKOWE BAJTY?")
print("="*70)

print("\nPorównanie bajtów 50-62:")
print(f"TIME:      {' '.join(f'{b:02X}' for b in TIME_BASE[50:58])}")
print(f"META TOR1: {' '.join(f'{b:02X}' for b in TIME_META_TOR1[50:62])}")
print(f"META TOR2: {' '.join(f'{b:02X}' for b in TIME_META_TOR2[50:62])}")

print("\n" + "="*70)
print("WNIOSEK:")
print("="*70)
print("Pakiet META:")
print("  - Bajt 2: 0x3E (zamiast 0x3A)")
print("  - Tekst: 38 znaków (bajty 22-59) zamiast 34")
print("  - Końcówka: 0D 0A (bajty 60-61)")
print("  - Razem: 62 bajty")
print("\nFunkcja create_time_packet() tworzy pakiet TIME (58 bajtów).")
print("Dla META musimy:")
print("  1. Zmienić bajt 2 z 0x3A na 0x3E")
print("  2. Rozszerzyć tekst do 38 znaków (dodać 4 spacje przed \\r\\n)")
print("="*70)
