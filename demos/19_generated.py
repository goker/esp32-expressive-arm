#!/usr/bin/env python3
"""
Demo 08: Wave to Crowd
Simulates waving to a crowd using base and shoulder movements.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Wave to Crowd ===\\n")

WAVES = 3
DELAY = 0.2

print("Waving to the crowd...")
for wave in range(WAVES):
    print(f"  Wave {wave + 1}/{WAVES}")

    # Move base left
    for angle in range(63, 20, -1):
        set_servo(0, angle)
        time.sleep(0.01)

    # Move shoulder up
    for angle in range(60, 90, 1):
        set_servo(1, angle)
        time.sleep(0.01)

    # Move shoulder down
    for angle in range(90, 60, -1):
        set_servo(1, angle)
        time.sleep(0.01)

    # Move base right
    for angle in range(20, 63, 1):
        set_servo(0, angle)
        time.sleep(0.01)

    time.sleep(DELAY)

home()
print("\\n=== Wave complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Wave to Crowd")
    print("=" * 30)
    run_on_esp32(CODE)