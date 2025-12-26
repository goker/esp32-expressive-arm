#!/usr/bin/env python3
"""
Demo 08: Menacing Pincers
Opens and closes the gripper in a quick, aggressive manner.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Menacing Pincers ===\\n")

REPEATS = 5
DELAY = 0.1

print("Performing menacing pincer action...")
for i in range(REPEATS):
    print(f"  Repeat {i + 1}/{REPEATS}")

    # Close quickly
    for angle in range(90, 170, 5):
        set_servo(3, angle)
        time.sleep(0.01)

    time.sleep(DELAY)

    # Open quickly
    for angle in range(170, 90, -5):
        set_servo(3, angle)
        time.sleep(0.01)

    time.sleep(DELAY)

home()
print("\\n=== Menacing pincers complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Menacing Pincers")
    print("=" * 30)
    run_on_esp32(CODE)