#!/usr/bin/env python3
"""
Demo 08: Japanese Bow
Simulates a Japanese bow by rotating the base and lowering the shoulder.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Japanese Bow ===\\n")

STEPS = 50
DELAY = 0.02

# Bowing motion
print("Bowing...")
for i in range(STEPS):
    t = i / STEPS
    s = minimum_jerk(t)

    base = 63 + (90 - 63) * s
    shoulder = 60 + (90 - 60) * s

    set_servo(0, base)
    set_servo(1, shoulder)
    time.sleep(DELAY)

time.sleep(0.5)

# Returning to upright position
print("Returning to upright...")
for i in range(STEPS):
    t = i / STEPS
    s = minimum_jerk(t)

    base = 90 + (63 - 90) * s
    shoulder = 90 + (60 - 90) * s

    set_servo(0, base)
    set_servo(1, shoulder)
    time.sleep(DELAY)

home()
print("\\n=== Bow complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Japanese Bow")
    print("=" * 30)
    run_on_esp32(CODE)