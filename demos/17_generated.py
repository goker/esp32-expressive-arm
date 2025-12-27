#!/usr/bin/env python3
"""
Demo 08: Wave and Rotate
Waves the shoulder and rotates the base to greet a crowd
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Wave and Rotate ===\\n")

WAVE_STEPS = 20
ROTATE_STEPS = 30
DELAY = 0.01

# Wave the shoulder
print("Waving...")
for _ in range(3):
    # Up
    for i in range(WAVE_STEPS):
        angle = 60 + (20 * i / WAVE_STEPS)
        set_servo(1, angle)
        time.sleep(DELAY)

    # Down
    for i in range(WAVE_STEPS):
        angle = 80 - (20 * i / WAVE_STEPS)
        set_servo(1, angle)
        time.sleep(DELAY)

# Rotate the base
print("Rotating...")
for i in range(ROTATE_STEPS):
    angle = 63 + (50 * i / ROTATE_STEPS)
    set_servo(0, angle)
    time.sleep(DELAY)

for i in range(ROTATE_STEPS):
    angle = 113 - (50 * i / ROTATE_STEPS)
    set_servo(0, angle)
    time.sleep(DELAY)

home()
print("\\n=== Wave and Rotate complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Wave and Rotate")
    print("=" * 30)
    run_on_esp32(CODE)