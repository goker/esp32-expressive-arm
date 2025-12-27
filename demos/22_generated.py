#!/usr/bin/env python3
"""
Demo 08: Wave to Crowd
The robot arm waves to an imaginary crowd.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Wave to Crowd ===\\n")

print("Waving...")
for i in range(3):
    print(f"  Wave {i + 1}/3")

    # Wave 1: Shoulder up
    for angle in range(60, 90, 2):
        set_servo(1, angle)
        time.sleep(0.01)
    # Elbow out
    for angle in range(100, 130, 2):
        set_servo(2, angle)
        time.sleep(0.01)

    # Wave 2: Shoulder down
    for angle in range(90, 60, -2):
        set_servo(1, angle)
        time.sleep(0.01)

    # Elbow in
    for angle in range(130, 100, -2):
        set_servo(2, angle)
        time.sleep(0.01)

    time.sleep(0.2)

home()
print("\\n=== Wave complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Wave to Crowd")
    print("=" * 30)
    run_on_esp32(CODE)