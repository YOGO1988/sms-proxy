#!/usr/bin/env python3
"""Test brightness mapping - NO HARDWARE NEEDED"""

def test_brightness_mapping():
    """Test that brightness percentages map to correct levels"""

    # Brightness mapping logic (copied from set_brightness)
    def map_brightness(brightness):
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

        return level

    print("="*70)
    print("BRIGHTNESS MAPPING TEST")
    print("="*70)

    test_values = [
        (0, 0),
        (10, 0),
        (13, 0),
        (14, 3),
        (20, 3),
        (33, 3),
        (34, 8),
        (50, 8),
        (60, 8),
        (61, 9),
        (73, 9),
        (74, 12),
        (80, 12),
        (99, 12),
        (100, 15),
    ]

    all_passed = True
    for percentage, expected_level in test_values:
        actual_level = map_brightness(percentage)
        status = "✅" if actual_level == expected_level else "❌"
        if actual_level != expected_level:
            all_passed = False
        print(f"{status} {percentage:3d}% -> Level {actual_level:2d} (expected {expected_level:2d})")

    print("="*70)
    if all_passed:
        print("✅ All tests PASSED!")
    else:
        print("❌ Some tests FAILED!")

    return all_passed

if __name__ == "__main__":
    test_brightness_mapping()
