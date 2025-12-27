#!/usr/bin/env python3
"""
Demo 08: Wave to the Crowd
Waves the arm in a friendly greeting.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Wave to the Crowd ===\\n")

# Wave with base and shoulder
def wave():
    for i in range(3):
        print(f"  Wave {i + 1}/3")

        # Move base right
        for angle in range(63, 100, 2):
            set_servo(0, angle)
            time.sleep(0.01)

        # Move shoulder up
        for angle in range(60, 85, 2):
            set_servo(1, angle)
            time.sleep(0.01)

        # Move shoulder down
        for angle in range(85, 60, -2):
            set_servo(1, angle)
            time.sleep(0.01)

        # Move base left
        for angle in range(100, 63, -2):
            set_servo(0, angle)
            time.sleep(0.01)

        time.sleep(0.2)

wave()

home()
print("\\n=== Wave complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Wave to the Crowd")
    print("=" * 30)
    run_on_esp32(CODE)