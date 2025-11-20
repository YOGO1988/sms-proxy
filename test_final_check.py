#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ostateczny test - czy wszystkie pakiety się tworzą poprawnie
"""

def calculate_crc16(data: bytes) -> int:
    """CRC-16-CCITT"""
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


def create_time_packet(text: str, base_packet: bytes) -> bytes:
    """Tworzy pakiet TIME (58 bajtów)"""
    packet = bytearray(base_packet)
    text_padded = text.ljust(34)[:34]
    packet[22:56] = text_padded.encode('ascii', errors='replace')
    packet[4] = 0
    packet[5] = 0
    crc = calculate_crc16(bytes(packet))
    packet[4] = crc & 0xFF
    packet[5] = (crc >> 8) & 0xFF
    return bytes(packet)


def create_meta_packet(text: str, base_packet: bytes) -> bytes:
    """Tworzy pakiet META (62 bajty)"""
    packet = bytearray(base_packet)
    text_padded = text.ljust(38)[:38]
    packet[22:60] = text_padded.encode('ascii', errors='replace')
    packet[4] = 0
    packet[5] = 0
    crc = calculate_crc16(bytes(packet))
    packet[4] = crc & 0xFF
    packet[5] = (crc >> 8) & 0xFF
    return bytes(packet)


# Oryginalne pakiety
TIME_BASE = bytes.fromhex('1B 07 3A 00 51 8B 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 34 36 37 20 20 2D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A')
TIME_META_TOR1 = bytes.fromhex('1B 07 3E 00 A1 2A 00 00 01 00 00 00 00 00 00 00 00 00 00 00 0A 00 30 30 27 30 37 22 2E 37 38 37 20 54 4F 52 20 31 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 0D 0A')

print("="*70)
print("TEST WSZYSTKICH PAKIETÓW")
print("="*70)

# Test 1: Pakiet TIME
print("\n1️⃣ Pakiet TIME (00'00\".000):")
pkt_time = create_time_packet("00'00\".000  - ", TIME_BASE)
print(f"   Długość: {len(pkt_time)} bajtów (powinno być 58)")
print(f"   Końcówka: {pkt_time[56]:02X} {pkt_time[57]:02X} (powinno być 0D 0A)")
print(f"   Tekst: '{pkt_time[22:56].decode('ascii')}'")
if len(pkt_time) == 58 and pkt_time[56] == 0x0D and pkt_time[57] == 0x0A:
    print("   ✅ OK!")
else:
    print("   ❌ BŁĄD!")

# Test 2: Pakiet META TOR 1
print("\n2️⃣ Pakiet META TOR 1 (00'05\".123):")
pkt_meta1 = create_meta_packet("00'05\".123 TOR 1", TIME_META_TOR1)
print(f"   Długość: {len(pkt_meta1)} bajtów (powinno być 62)")
print(f"   Bajt 2: 0x{pkt_meta1[2]:02X} (powinno być 0x3E)")
print(f"   Końcówka: {pkt_meta1[60]:02X} {pkt_meta1[61]:02X} (powinno być 0D 0A)")
print(f"   Tekst: '{pkt_meta1[22:60].decode('ascii')}'")
if len(pkt_meta1) == 62 and pkt_meta1[2] == 0x3E and pkt_meta1[60] == 0x0D and pkt_meta1[61] == 0x0A:
    print("   ✅ OK!")
else:
    print("   ❌ BŁĄD!")

# Test 3: Czy możemy odtworzyć oryginalny pakiet?
print("\n3️⃣ Odtwarzanie oryginalnego pakietu TIME:")
pkt_restore = create_time_packet("00'07\".467  - ", TIME_BASE)
if pkt_restore == TIME_BASE:
    print("   ✅ Możemy odtworzyć ORYGINALNY pakiet TIME!")
else:
    print("   ❌ Nie udało się odtworzyć")

print("\n4️⃣ Odtwarzanie oryginalnego pakietu META TOR 1:")
pkt_restore_meta = create_meta_packet("00'07\".787 TOR 1", TIME_META_TOR1)
if pkt_restore_meta == TIME_META_TOR1:
    print("   ✅ Możemy odtworzyć ORYGINALNY pakiet META!")
else:
    print("   ❌ Nie udało się odtworzyć")

print("\n" + "="*70)
print("PODSUMOWANIE:")
print("="*70)
all_ok = (
    len(pkt_time) == 58 and pkt_time[56] == 0x0D and pkt_time[57] == 0x0A and
    len(pkt_meta1) == 62 and pkt_meta1[60] == 0x0D and pkt_meta1[61] == 0x0A and
    pkt_restore == TIME_BASE and
    pkt_restore_meta == TIME_META_TOR1
)

if all_ok:
    print("✅ WSZYSTKO DZIAŁA POPRAWNIE!")
    print("✅ Możesz teraz przetestować na prawdziwym urządzeniu!")
else:
    print("❌ Są problemy - sprawdź powyżej")

print("="*70)
