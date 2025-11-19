# LED Display Integration - Quick Reference

**YO&GO Events - 2025**

> **FIXED VERSION** - Based on actual protocol from your working chronometer program

---

## Quick Start (5 minutes)

### 1. Test the Display

```bash
python test_fixed_protocol.py
```

Watch your LED display! It will test:
- ✅ Clearing
- ✅ Single time
- ✅ Two times
- ✅ Rotation (4 competitors)
- ✅ Event name

### 2. Use in Your Program

```python
from led_display_fixed import LEDDisplayManager

# Initialize
led = LEDDisplayManager(port='COM5', baudrate=9600)
if not led.initialize():
    print("LED not available")
    exit()

# Clear before race
led.clear_display()

# Show results after race
led.update_race_results({
    'race_number': 1,
    'lanes': 2,
    'results': [
        {'lane': 1, 'time': '00:07.835'},
        {'lane': 2, 'time': '00:10.197'}
    ]
})

# Cleanup
led.shutdown()
```

**Done! That's all you need!**

---

## Available Tools

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `test_fixed_protocol.py` | Test with real hardware | **Start here** - verify display works |
| `simulate_protocol.py` | View protocol bytes | Debug without hardware |
| `example_race_integration.py` | Integration examples | Learn how to integrate |
| `led_display_fixed.py` | Main module | Import this in your code |

---

## Testing Without Hardware

Want to see what bytes are sent?

```bash
python simulate_protocol.py
```

Output:
```
INITIALIZATION SEQUENCE
Set9600 command (sent 3x):
HEX (10 bytes):
  1B 09 0A 00 A4 EB 00 00 0D 0A

ASCII: [1B][09][0A][00]¤ë[00][00][0D][0A]
```

Interactive mode:
```bash
python simulate_protocol.py --interactive
```

---

## Integration Examples

```bash
python example_race_integration.py
```

Choose:
1. Single race (1 competitor)
2. Two-lane race (2 competitors)
3. Multi-lane race (4 competitors, rotation)
4. Integration template for your code

---

## How It Works

### Display Behavior

**1 competitor:**
```
Line 1: 00'07".835 TOR 1
Line 2: (empty)
```

**2 competitors:**
```
Line 1: 00'07".835 TOR 1
Line 2: 00'10".197 TOR 2
```

**3+ competitors:**
- Rotates pairs every 3 seconds
- Shows lanes 1-2, then 3-4, then 1-2...
- Continues until stopped

### Time Format

**Your code provides:** `MM:SS.mmm` (e.g., `00:07.835`)

**Display shows:** `MM'SS".mmm TOR X` (e.g., `00'07".835 TOR 1`)

**Conversion happens automatically!** You don't need to do anything.

---

## Protocol Details

Full documentation: `PROTOCOL_ANALYSIS.md`

Key points:
- **Baudrate:** 9600
- **Commands:** Start with `1B` (ESC)
- **Line selection:** Byte at position 18 (`00`=line 1, `10`=line 2)
- **Time format:** Uses `'` and `"` instead of `:`
- **Initialization:** Sends `Set9600` command 3 times

---

## Troubleshooting

### Display doesn't respond

1. Check power
2. Verify COM port (is it really COM5?)
3. Check cable connection
4. Run `python simulate_protocol.py` to verify protocol

### Wrong port

Edit your code:
```python
led = LEDDisplayManager(port='COM5', baudrate=9600)  # Change COM5
```

Or make it ask:
```python
port = input("COM Port: ") or "COM5"
led = LEDDisplayManager(port=port, baudrate=9600)
```

### Times not displaying correctly

The module handles format conversion automatically. You provide `MM:SS.mmm`, it converts to `MM'SS".mmm`.

If times still wrong, check:
- Is time in correct format? (`00:07.835`)
- Is lane number provided? (`{'lane': 1, 'time': '00:07.835'}`)

### Display shows garbage

This means protocol mismatch. Run:
```bash
python simulate_protocol.py
```

Compare output with `PROTOCOL_ANALYSIS.md`. If they match but display still shows garbage, the display might use different protocol variant.

---

## Files

### Use These ✅
- `led_display_fixed.py` - **Main module (FIXED!)**
- `test_fixed_protocol.py` - Hardware test
- `simulate_protocol.py` - Protocol viewer
- `example_race_integration.py` - Examples
- `PROTOCOL_ANALYSIS.md` - Protocol documentation
- `INSTRUKCJA_NAPRAWY.md` - Full instructions (Polish)

### Ignore These ❌
- `led_display.py` - Old version (DOESN'T WORK)
- `led_autotest.py` - Old testing tool
- `diagnose_led.py` - Old diagnostic
- `simple_send.py` - Old test

---

## API Reference

### LEDDisplayManager

#### `__init__(port, baudrate=9600)`
Create display manager.
- `port`: COM port (e.g., `'COM5'`)
- `baudrate`: Always 9600 for your display

#### `initialize() -> bool`
Connect to display. Returns `True` if successful.

#### `clear_display()`
Clear/turn off display. Use before each race.

#### `update_race_results(race_data: dict)`
Display race results. Automatically handles 1, 2, or many competitors.

**race_data format:**
```python
{
    'race_number': 1,
    'lanes': 2,
    'results': [
        {'lane': 1, 'time': '00:07.835'},
        {'lane': 2, 'time': '00:10.197'}
    ]
}
```

#### `show_event_name(name: str, duration: float = 5.0)`
Show event name. Optional.
- `name`: Event name to display
- `duration`: How long to show (seconds)

#### `shutdown()`
Disconnect and cleanup. Call when program exits.

---

## Next Steps

1. **Test:** `python test_fixed_protocol.py`
2. **Learn:** `python example_race_integration.py`
3. **Integrate:** Add 5 lines to your code (see Quick Start)
4. **Race!** 🏁

---

## What's Different from Old Version?

The old `led_display.py` **didn't work** because it assumed standard ASCII protocol.

Your display uses **custom manufacturer protocol:**
- Special initialization command (`Set9600`)
- Binary command structure (`1B 07`, `1B 08`, `1B 09`)
- Custom time format (`00'07".835` not `00:07.835`)
- Line selection bytes

The new `led_display_fixed.py` implements the **exact protocol** from your working chronometer program.

---

## Support

If display doesn't work:

1. Run `python test_fixed_protocol.py`
2. Note which tests pass/fail
3. Check what appears on display
4. Report back with:
   - Which tests worked?
   - What did display show?
   - Any errors in console?

---

**Good luck! 🎉**

For complete instructions in Polish: `INSTRUKCJA_NAPRAWY.md`
