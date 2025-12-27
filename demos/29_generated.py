#!/usr/bin/env python3
"""
Demo 08: Wave to Crowd
Waves the arm back and forth to simulate waving to a crowd.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Wave to Crowd ===\\n")

WAVES = 3
SWEEP_RANGE = 30
DELAY = 0.01

print(f"Waving {WAVES} times...")
for wave in range(WAVES):
    print(f"  Wave {wave + 1}/{WAVES}")

    # Wave out
    for angle in range(63, 63 + SWEEP_RANGE, 1):
        set_servo(0, angle)
        time.sleep(DELAY)

    # Wave back
    for angle in range(63 + SWEEP_RANGE, 63 - SWEEP_RANGE, -1):
        set_servo(0, angle)
        time.sleep(DELAY)

    # Return to center
    for angle in range(63 - SWEEP_RANGE, 63, 1):
        set_servo(0, angle)
        time.sleep(DELAY)

home()
print("\\n=== Wave complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Wave to Crowd")
    print("=" * 30)
    run_on_esp32(CODE)