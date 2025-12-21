#!/usr/bin/env python3
"""
Demo 01: Test each servo individually
Moves each servo: 90 -> 60 -> 120 -> 90
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 01: Test Servos ===\\n")

for i, name in enumerate(SERVO_NAMES):
    print(f"Testing {name}...")

    # Move to 60
    for angle in range(90, 59, -2):
        set_servo_direct(i, angle)
        time.sleep(0.02)
    time.sleep(0.2)

    # Move to 120
    for angle in range(60, 121, 2):
        set_servo_direct(i, angle)
        time.sleep(0.02)
    time.sleep(0.2)

    # Back to 90
    for angle in range(120, 89, -2):
        set_servo_direct(i, angle)
        time.sleep(0.02)
    time.sleep(0.3)

    print(f"  {name} OK!")

home()
print("\\n=== Test complete! ===")
'''

if __name__ == "__main__":
    print("Demo 01: Test Servos")
    print("=" * 30)
    run_on_esp32(CODE)
