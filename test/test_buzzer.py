"""Buzzer pin finder — toggles each GPIO pin on/off to locate the buzzer.

Usage:
    python scripts/test_buzzer.py

For each pin (0-27) it will:
  1. HIGH for 0.5s  (bunyi jika buzzer terpasang)
  2. LOW  for 0.3s
Then move to the next pin.

Press CTRL+C to stop early.
"""

import time

try:
    import RPi.GPIO as GPIO
except ImportError:
    print("ERROR: RPi.GPIO not available. Run on Raspberry Pi.")
    raise SystemExit(1)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

PINS = list(range(0, 28))

print("=" * 50)
print("  BUZZER PIN FINDER")
print("=" * 50)
print(f"Testing pins: {PINS[0]} → {PINS[-1]}")
print("Listen for the buzzer sound and note the pin number.")
print("Press CTRL+C to stop.\n")

try:
    for pin in PINS:
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

        print(f"Pin {pin:2d} → HIGH ... ", end="", flush=True)
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(0.5)

        GPIO.output(pin, GPIO.LOW)
        print("LOW")
        time.sleep(0.3)

except KeyboardInterrupt:
    print("\n\nStopped by user.")

finally:
    GPIO.cleanup()
    print("GPIO cleaned up.")
