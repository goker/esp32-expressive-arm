#!/usr/bin/env python3
"""
Demo 08: Waving Hello
Waves the robot arm to greet an audience
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Waving Hello ===\\n")

# Wave the arm multiple times
for i in range(5):
    print(f"  Wave {i+1}/5")

    # Open Gripper
    for angle in range(90, 150, 2):
        set_servo(3, angle)
        time.sleep(0.01)

    # Wave with shoulder and elbow
    for angle in range(45, 75, 1):
        set_servo(1, angle)
        set_servo(2, 110 - (angle - 45))
        time.sleep(0.01)

    for angle in range(74, 44, -1):
        set_servo(1, angle)
        set_servo(2, 110 - (angle - 45))
        time.sleep(0.01)

    # Close Gripper
    for angle in range(150, 90, -2):
        set_servo(3, angle)
        time.sleep(0.01)

    time.sleep(0.2)

home()
print("\\n=== Waving complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Waving Hello")
    print("=" * 30)
    run_on_esp32(CODE)