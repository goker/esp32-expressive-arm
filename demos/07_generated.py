#!/usr/bin/env python3
"""
Demo 08: Smooth Wave Hello
Generates a smooth waving motion using the shoulder joint.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Smooth Wave Hello ===\\n")

STEPS = 50
DELAY = 0.01

# Wave up and down three times
for wave in range(3):
    print(f"  Wave {wave + 1}/3")

    # Wave up
    for i in range(STEPS):
        t = i / STEPS
        s = minimum_jerk(t)
        angle = 60 + (80 - 60) * s
        set_servo(1, angle)
        time.sleep(DELAY)

    # Wave down
    for i in range(STEPS):
        t = i / STEPS
        s = minimum_jerk(t)
        angle = 80 + (60 - 80) * s
        set_servo(1, angle)
        time.sleep(DELAY)

    time.sleep(0.2)

home()
print("\\n=== Wave complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Smooth Wave Hello")
    print("=" * 30)
    run_on_esp32(CODE)