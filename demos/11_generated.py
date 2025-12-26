#!/usr/bin/env python3
"""
Demo 08: Menacing Gripper
Moves the gripper in a threatening manner, rotating the base to target different areas.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Menacing Gripper ===\\n")

def gripper_threat(base_angle):
    set_servo(0, base_angle)
    for angle in range(80, 150, 3):
        set_servo(3, angle)
        time.sleep(0.01)
    for angle in range(150, 80, -3):
        set_servo(3, angle)
        time.sleep(0.01)

# Threaten left
print("Threatening left...")
gripper_threat(10)
time.sleep(0.3)

# Threaten center
print("Threatening center...")
gripper_threat(63)
time.sleep(0.3)

# Threaten right
print("Threatening right...")
gripper_threat(160)
time.sleep(0.3)

# Threaten up
print("Threatening up...")
set_servo(0, 63)
for angle in range(80, 150, 3):
    set_servo(3, angle)
    set_servo(1, 30)
    time.sleep(0.01)
for angle in range(150, 80, -3):
    set_servo(3, angle)
    set_servo(1, 60)
    time.sleep(0.01)
time.sleep(0.3)

home()
print("\\n=== Menacing complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Menacing Gripper")
    print("=" * 30)
    run_on_esp32(CODE)