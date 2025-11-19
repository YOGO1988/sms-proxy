#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example: LED Display Integration with Race Timing System

This shows how to integrate the LED display into your actual race timing program.
"""

from led_display_fixed import LEDDisplayManager
import time


class RaceTimingSystem:
    """
    Example race timing system with LED display integration.
    Replace this with your actual timing system.
    """

    def __init__(self, led_port='COM5'):
        """
        Initialize the race timing system with LED display.

        Args:
            led_port: COM port for LED display (default: COM5)
        """
        print("=" * 60)
        print("Race Timing System with LED Display")
        print("=" * 60)

        # Initialize LED display
        self.led = LEDDisplayManager(port=led_port, baudrate=9600)

        if not self.led.initialize():
            print("⚠️  WARNING: LED display not available!")
            print("   System will continue without display.")
            self.led_available = False
        else:
            print("✅ LED display ready!")
            self.led_available = True

        self.current_race = None

    def show_event_info(self, event_name: str, duration: float = 5.0):
        """
        Display event name before races start.

        Args:
            event_name: Name of the event
            duration: How long to display (seconds)
        """
        print(f"\n📢 Event: {event_name}")

        if self.led_available:
            self.led.show_event_name(event_name, duration)

    def start_race(self, race_number: int, num_lanes: int):
        """
        Start a new race.

        Args:
            race_number: Race number
            num_lanes: Number of lanes/competitors
        """
        print(f"\n🏁 Starting Race #{race_number} ({num_lanes} lanes)")

        self.current_race = {
            'race_number': race_number,
            'lanes': num_lanes,
            'results': []
        }

        # Clear display to signal new race
        if self.led_available:
            self.led.clear_display()
            print("   LED display cleared (ready for race)")

    def record_finish(self, lane: int, finish_time: str):
        """
        Record a finish time for a lane.

        Args:
            lane: Lane number (1-based)
            finish_time: Time in format "MM:SS.mmm"
        """
        if not self.current_race:
            print("⚠️  No active race!")
            return

        print(f"   Lane {lane}: {finish_time}")

        # Add result
        self.current_race['results'].append({
            'lane': lane,
            'time': finish_time
        })

    def finish_race(self):
        """
        Finish the current race and display results.
        """
        if not self.current_race:
            print("⚠️  No active race!")
            return

        print(f"\n✅ Race #{self.current_race['race_number']} finished!")
        print(f"   Results:")

        # Sort by time for display
        results = sorted(
            self.current_race['results'],
            key=lambda x: self._time_to_seconds(x['time'])
        )

        for i, result in enumerate(results, 1):
            print(f"   {i}. Lane {result['lane']}: {result['time']}")

        # Update LED display
        if self.led_available:
            print("\n📺 Updating LED display...")
            self.led.update_race_results(self.current_race)

        return self.current_race

    def _time_to_seconds(self, time_str: str) -> float:
        """Convert time string to seconds for sorting."""
        try:
            parts = time_str.split(":")
            if len(parts) == 2:
                minutes = int(parts[0])
                seconds = float(parts[1])
                return minutes * 60 + seconds
        except:
            pass
        return 999999.0  # Invalid time goes to end

    def shutdown(self):
        """Shutdown the system."""
        print("\n🔴 Shutting down...")

        if self.led_available:
            self.led.shutdown()

        print("✅ System shutdown complete")


def example_single_race():
    """Example: Single race with 1 competitor"""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Single Race (1 competitor)")
    print("=" * 60)

    # Initialize system
    system = RaceTimingSystem(led_port='COM5')

    # Show event info
    system.show_event_info("MISTRZOSTWA 2025", duration=3)

    # Start race
    system.start_race(race_number=1, num_lanes=1)

    # Simulate timing (in real system, this comes from your timer)
    time.sleep(2)

    # Record finish
    system.record_finish(lane=1, finish_time="00:07.835")

    # Finish race and display results
    system.finish_race()

    time.sleep(5)

    # Shutdown
    system.shutdown()


def example_two_lane_race():
    """Example: Race with 2 competitors"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Two-Lane Race")
    print("=" * 60)

    system = RaceTimingSystem(led_port='COM5')

    system.start_race(race_number=2, num_lanes=2)

    # Simulate race
    time.sleep(2)

    # Record finishes
    system.record_finish(lane=1, finish_time="00:07.835")
    time.sleep(0.5)
    system.record_finish(lane=2, finish_time="00:10.197")

    # Display results
    system.finish_race()

    time.sleep(5)
    system.shutdown()


def example_multi_lane_race():
    """Example: Race with 4+ competitors (with rotation)"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Multi-Lane Race (rotation)")
    print("=" * 60)

    system = RaceTimingSystem(led_port='COM5')

    system.start_race(race_number=3, num_lanes=4)

    # Simulate race
    time.sleep(2)

    # Record finishes
    system.record_finish(lane=1, finish_time="00:02.043")
    system.record_finish(lane=2, finish_time="00:03.413")
    system.record_finish(lane=3, finish_time="00:04.768")
    system.record_finish(lane=4, finish_time="00:06.135")

    # Display results (will rotate lanes 1-2, then 3-4, then back)
    system.finish_race()

    print("\n⏱️  Watching rotation for 15 seconds...")
    time.sleep(15)

    system.shutdown()


def example_integration_with_your_code():
    """
    Example: How to integrate with YOUR existing timing code.

    Replace the timing logic with your actual implementation.
    """
    print("\n" + "=" * 60)
    print("INTEGRATION TEMPLATE FOR YOUR CODE")
    print("=" * 60)

    # Step 1: Initialize LED display at program start
    led = LEDDisplayManager(port='COM5', baudrate=9600)

    if not led.initialize():
        print("⚠️  LED display not available - continuing without it")
        led = None  # Set to None so we can check later

    # Step 2: Before races start (optional)
    if led:
        led.show_event_name("YOUR EVENT NAME", duration=5)

    # Step 3: When starting a new race
    print("\n--- YOUR RACE START CODE HERE ---")

    if led:
        led.clear_display()  # Clear display = signal that new race is ready

    # Step 4: YOUR TIMING CODE RUNS HERE
    # ... your code to detect finish times ...

    # Let's simulate collecting results
    race_results = {
        'race_number': 1,
        'lanes': 2,
        'results': [
            {'lane': 1, 'time': '00:07.835'},  # ← from your timer
            {'lane': 2, 'time': '00:10.197'}   # ← from your timer
        ]
    }

    print("--- YOUR RACE FINISH CODE HERE ---")

    # Step 5: When race finishes, update display
    if led:
        led.update_race_results(race_results)

    # Display will now show:
    # - 1 result: single time on line 1
    # - 2 results: both times on lines 1 and 2
    # - 3+ results: rotating pairs every 3 seconds

    print("\n✅ Race complete - results displayed on LED")

    # Step 6: At program shutdown
    if led:
        led.shutdown()


def main():
    """Main menu for examples"""
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "LED DISPLAY INTEGRATION EXAMPLES" + " " * 15 + "║")
    print("╚" + "═" * 58 + "╝")

    print("\nChoose an example:")
    print("  1. Single race (1 competitor)")
    print("  2. Two-lane race (2 competitors)")
    print("  3. Multi-lane race (4 competitors, with rotation)")
    print("  4. Integration template (for your code)")
    print("  q. Quit")

    choice = input("\nChoice: ").strip()

    if choice == '1':
        example_single_race()
    elif choice == '2':
        example_two_lane_race()
    elif choice == '3':
        example_multi_lane_race()
    elif choice == '4':
        example_integration_with_your_code()
    elif choice.lower() in ['q', 'quit']:
        print("Bye!")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
