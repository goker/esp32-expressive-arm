#!/usr/bin/env python3
"""
Demo 08: Waving to the Crowd
The arm waves its "hand" (gripper) back and forth.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Waving to the Crowd ===\\n")

# Wave the gripper back and forth
for wave in range(3):
    print(f"  Wave {wave + 1}/3")

    # Wave right
    for angle in range(90, 150, 2):
        set_servo(3, angle)
        time.sleep(0.01)

    # Wave left
    for angle in range(150, 90, -2):
        set_servo(3, angle)
        time.sleep(0.01)

    time.sleep(0.2)

home()
print("\\n=== Wave complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Waving to the Crowd")
    print("=" * 30)
    run_on_esp32(CODE)