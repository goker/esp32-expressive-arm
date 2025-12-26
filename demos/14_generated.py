#!/usr/bin/env python3
"""
Demo 08: Waving Base Rotation
Rotates the base while waving with the shoulder.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Waving Base Rotation ===\\n")

WAVES = 2
ROTATIONS = 2
STEPS = 50
DELAY = 0.02

print("Waving and rotating...")

for rotation in range(ROTATIONS):
    print(f"Rotation {rotation + 1}/{ROTATIONS}")
    for i in range(STEPS):
        t = i / STEPS
        angle = 63 + 57 * math.sin(2 * math.pi * t)
        set_servo(0, angle)
        time.sleep(DELAY)
    for wave in range(WAVES):
        print(f"Wave {wave + 1}/{WAVES}")
        for i in range(STEPS):
            t = i / STEPS
            shoulder_angle = 60 + 20 * math.sin(2 * math.pi * t)
            set_servo(1, shoulder_angle)
            time.sleep(DELAY)

home()
print("\\n=== Wave and rotation complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Waving Base Rotation")
    print("=" * 30)
    run_on_esp32(CODE)