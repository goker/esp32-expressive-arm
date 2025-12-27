#!/usr/bin/env python3
"""
Demo 08: Wave to Crowd
Waves the arm to simulate greeting a crowd.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Wave to Crowd ===\\n")

WAVES = 3
DELAY = 0.1

print("Waving to the crowd...")
for wave in range(WAVES):
    print(f"  Wave {wave + 1}/{WAVES}")

    # Wave Out
    for angle in range(63, 140, 2):
        set_servo(0, angle)
        time.sleep(0.01)
    time.sleep(DELAY)

    # Wave In
    for angle in range(140, 62, -2):
        set_servo(0, angle)
        time.sleep(0.01)
    time.sleep(DELAY)

home()
print("\\n=== Waving complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Wave to Crowd")
    print("=" * 30)
    run_on_esp32(CODE)