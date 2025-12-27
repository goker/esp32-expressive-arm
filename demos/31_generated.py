#!/usr/bin/env python3
"""
Demo 08: Open Gripper Sequence
Opens the gripper twice in succession.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Open Gripper Sequence ===\\n")

print("Opening Gripper...")
for angle in range(90, 181, 2):
    set_servo(3, angle)
    time.sleep(0.01)

time.sleep(0.5)

print("Opening Gripper Again...")
for angle in range(180, 181, 2):
    set_servo(3, angle)
    time.sleep(0.01)

home()
print("\\n=== Open Gripper Sequence complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Open Gripper Sequence")
    print("=" * 30)
    run_on_esp32(CODE)