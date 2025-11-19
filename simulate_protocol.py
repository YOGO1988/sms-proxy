#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LED Display Protocol Simulator
Shows exactly what bytes would be sent to the display without requiring hardware.
Perfect for verification and debugging.
"""

from led_display_fixed import LEDDisplayProtocol
import sys


def hex_dump(data: bytes, label: str = ""):
    """Pretty print hex dump of bytes"""
    if label:
        print(f"\n{label}")
        print("=" * 60)

    # Print as HEX
    hex_str = " ".join(f"{b:02X}" for b in data)
    print(f"HEX ({len(data)} bytes):")

    # Print in rows of 16 bytes
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hex_part = " ".join(f"{b:02X}" for b in chunk)
        ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        print(f"  {hex_part:<48}  {ascii_part}")

    # Print as ASCII (where printable)
    print(f"\nASCII (printable chars only):")
    ascii_str = "".join(chr(b) if 32 <= b < 127 else f"[{b:02X}]" for b in data)
    print(f"  {ascii_str}")

    print()


def simulate_initialization():
    """Simulate initialization sequence"""
    print("\n" + "█" * 60)
    print("INITIALIZATION SEQUENCE")
    print("█" * 60)

    protocol = LEDDisplayProtocol()
    init_cmd = protocol.build_init_command()

    hex_dump(init_cmd, "Set9600 command (sent 3x on connection):")

    print("Expected behavior:")
    print("  ✓ Display initializes communication at 9600 baud")
    print("  ✓ Display is ready to receive commands")


def simulate_clear():
    """Simulate clear display"""
    print("\n" + "█" * 60)
    print("CLEAR DISPLAY")
    print("█" * 60)

    protocol = LEDDisplayProtocol()
    clear_cmd = protocol.build_clear_command()

    hex_dump(clear_cmd, "Clear command (sent 3x):")

    print("Expected behavior:")
    print("  ✓ Display turns off / clears all content")
    print("  ✓ Ready for new race")


def simulate_single_time():
    """Simulate displaying single time"""
    print("\n" + "█" * 60)
    print("SINGLE TIME DISPLAY")
    print("█" * 60)

    protocol = LEDDisplayProtocol()

    # Test time: 00:02.043
    time_str = "00:02.043"
    display_text = "00'02\".043 TOR 1"

    cmd = protocol.build_display_command(display_text, line=0)

    hex_dump(cmd, f"Display '{time_str}' on lane 1:")

    print("Expected behavior:")
    print("  ✓ Line 1: 00'02\".043 TOR 1")
    print("  ✓ Line 2: (empty)")


def simulate_two_times():
    """Simulate displaying two times"""
    print("\n" + "█" * 60)
    print("TWO TIMES DISPLAY")
    print("█" * 60)

    protocol = LEDDisplayProtocol()

    # Test times from original data
    time1_str = "00:07.835"
    time2_str = "00:10.197"

    display_text1 = "00'07\".835 TOR 1"
    display_text2 = "00'10\".197 TOR 2"

    cmd1 = protocol.build_display_command(display_text1, line=0)
    cmd2 = protocol.build_display_command(display_text2, line=1)

    hex_dump(cmd1, f"Display '{time1_str}' on lane 1 (line 0):")
    hex_dump(cmd2, f"Display '{time2_str}' on lane 2 (line 1):")

    print("Expected behavior:")
    print("  ✓ Line 1: 00'07\".835 TOR 1")
    print("  ✓ Line 2: 00'10\".197 TOR 2")


def simulate_event_name():
    """Simulate displaying event name"""
    print("\n" + "█" * 60)
    print("EVENT NAME DISPLAY")
    print("█" * 60)

    protocol = LEDDisplayProtocol()

    event_name = "MISTRZOSTWA 2025"
    cmd = protocol.build_display_command(event_name, line=0)

    hex_dump(cmd, f"Display event name: '{event_name}':")

    print("Expected behavior:")
    print("  ✓ Line 1: MISTRZOSTWA 2025")
    print("  ✓ Line 2: (empty)")


def compare_with_original():
    """Compare generated commands with original HEX data"""
    print("\n" + "█" * 60)
    print("COMPARISON WITH ORIGINAL PROGRAM")
    print("█" * 60)

    print("\n" + "-" * 60)
    print("INITIALIZATION (Set9600)")
    print("-" * 60)

    original_init = bytes([0x1B, 0x09, 0x0A, 0x00, 0xA4, 0xEB, 0x00, 0x00, 0x0D, 0x0A])
    protocol = LEDDisplayProtocol()
    generated_init = protocol.build_init_command()

    print(f"Original:  {' '.join(f'{b:02X}' for b in original_init)}")
    print(f"Generated: {' '.join(f'{b:02X}' for b in generated_init)}")
    print(f"Match: {'✓ YES' if original_init == generated_init else '✗ NO'}")

    print("\n" + "-" * 60)
    print("TIME DISPLAY: 00'07\".835 TOR 1")
    print("-" * 60)

    # Original from user's HEX dump (simplified - showing key parts)
    print("Original command structure from working program:")
    print("  1B 07 3E 00 ... 00 00 0A 00 [TEXT] ... 0D 0A")
    print("  Line byte (position 18): 00 (line 1)")
    print("  ASCII part: 30 30 27 30 37 22 2E 38 33 35 20 54 4F 52 20 31")
    print("           = \"00'07\\\".835 TOR 1\"")

    display_text = "00'07\".835 TOR 1"
    generated_cmd = protocol.build_display_command(display_text, line=0)

    print(f"\nGenerated: {' '.join(f'{b:02X}' for b in generated_cmd)}")
    print(f"Line byte at position 18: {generated_cmd[18]:02X} (should be 00 for line 1)")

    # Extract ASCII part
    ascii_start = 22  # After the 0A 00 separator
    text_bytes = generated_cmd[ascii_start:ascii_start+len(display_text)]
    print(f"ASCII part: {' '.join(f'{b:02X}' for b in text_bytes)}")
    print(f"         = \"{text_bytes.decode('ascii', errors='replace')}\"")

    print("\n" + "-" * 60)
    print("TIME DISPLAY: 00'10\".197 TOR 2 (LINE 2)")
    print("-" * 60)

    print("Original command structure from working program:")
    print("  1B 07 3E 00 ... 10 00 0A 00 [TEXT] ... 0D 0A")
    print("  Line byte (position 18): 10 (line 2)")
    print("  ASCII part: 30 30 27 31 30 22 2E 31 39 37 20 54 4F 52 20 32")
    print("           = \"00'10\\\".197 TOR 2\"")

    display_text2 = "00'10\".197 TOR 2"
    generated_cmd2 = protocol.build_display_command(display_text2, line=1)

    print(f"\nGenerated: {' '.join(f'{b:02X}' for b in generated_cmd2)}")
    print(f"Line byte at position 18: {generated_cmd2[18]:02X} (should be 10 for line 2)")

    # Extract ASCII part
    text_bytes2 = generated_cmd2[ascii_start:ascii_start+len(display_text2)]
    print(f"ASCII part: {' '.join(f'{b:02X}' for b in text_bytes2)}")
    print(f"         = \"{text_bytes2.decode('ascii', errors='replace')}\"")


def interactive_mode():
    """Interactive mode for custom testing"""
    print("\n" + "█" * 60)
    print("INTERACTIVE MODE")
    print("█" * 60)
    print("\nGenerate custom commands to see what bytes would be sent.")
    print("Type 'quit' to exit.\n")

    protocol = LEDDisplayProtocol()

    while True:
        print("\nOptions:")
        print("  1. Display custom text")
        print("  2. Display custom time")
        print("  3. Clear display")
        print("  4. Initialize")
        print("  q. Quit")

        choice = input("\nChoice: ").strip().lower()

        if choice in ['q', 'quit']:
            break

        if choice == '1':
            text = input("Enter text to display: ")
            line = input("Line (0 or 1, default 0): ").strip()
            line = int(line) if line else 0

            cmd = protocol.build_display_command(text, line)
            hex_dump(cmd, f"Display '{text}' on line {line}:")

        elif choice == '2':
            time_str = input("Enter time (MM:SS.mmm): ")
            lane = input("Lane number (1-4): ").strip()
            lane = int(lane) if lane else 1
            line = input("Line (0 or 1, default 0): ").strip()
            line = int(line) if line else 0

            # Convert time format
            parts = time_str.replace(":", "'").split(".")
            if len(parts) == 2:
                time_formatted = f"{parts[0]}\".{parts[1]} TOR {lane}"
            else:
                time_formatted = time_str

            cmd = protocol.build_display_command(time_formatted, line)
            hex_dump(cmd, f"Display time '{time_str}' (lane {lane}, line {line}):")

        elif choice == '3':
            cmd = protocol.build_clear_command()
            hex_dump(cmd, "Clear display:")

        elif choice == '4':
            cmd = protocol.build_init_command()
            hex_dump(cmd, "Initialize (Set9600):")


def main():
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "LED DISPLAY PROTOCOL SIMULATOR" + " " * 18 + "║")
    print("║" + " " * 12 + "Shows bytes without hardware" + " " * 18 + "║")
    print("╚" + "═" * 58 + "╝")

    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        interactive_mode()
    else:
        simulate_initialization()
        simulate_clear()
        simulate_single_time()
        simulate_two_times()
        simulate_event_name()
        compare_with_original()

        print("\n" + "█" * 60)
        print("SUMMARY")
        print("█" * 60)
        print("\nThis simulation shows the exact bytes that would be sent")
        print("to your LED display for each operation.")
        print("\nKey protocol features:")
        print("  ✓ All commands start with 1B (ESC)")
        print("  ✓ Command type: 1B 09 (init), 1B 07 (display), 1B 08 (clear)")
        print("  ✓ Time format: MM'SS\".mmm (apostrophe and quote)")
        print("  ✓ Line selection: byte at position 18 (00=line1, 10=line2)")
        print("  ✓ All commands end with 0D 0A (CRLF)")
        print("\nTo test with custom inputs:")
        print("  python simulate_protocol.py --interactive")
        print("\nTo test with actual hardware:")
        print("  python test_fixed_protocol.py")
        print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
