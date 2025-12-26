#!/usr/bin/env python3
"""
Demo 08: Wave to Crowd
Robot arm waves its gripper while rotating the base
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Wave to Crowd ===\\n")

WAVE_CYCLES = 3
BASE_SWEEP = 50
GRIPPER_SWEEP = 40
DELAY = 0.015

print("Starting wave...")

for cycle in range(WAVE_CYCLES):
    print(f"  Wave cycle {cycle + 1}/{WAVE_CYCLES}")

    # Base rotate right
    for base_angle in range(63, 63 + BASE_SWEEP, 2):
        set_servo(0, base_angle)
        time.sleep(DELAY)

    # Gripper open
    for gripper_angle in range(90, 90 + GRIPPER_SWEEP, 2):
        set_servo(3, gripper_angle)
        time.sleep(DELAY)

    # Base rotate left
    for base_angle in range(63 + BASE_SWEEP, 63 - BASE_SWEEP, -2):
        set_servo(0, base_angle)
        time.sleep(DELAY)

    # Gripper close
    for gripper_angle in range(90 + GRIPPER_SWEEP, 90 - GRIPPER_SWEEP, -2):
        set_servo(3, gripper_angle)
        time.sleep(DELAY)

    # Base rotate center
    for base_angle in range(63 - BASE_SWEEP, 63, 2):
        set_servo(0, base_angle)
        time.sleep(DELAY)

print("Wave complete!")
home()
print("\\n=== Wave to Crowd complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Wave to Crowd")
    print("=" * 30)
    run_on_esp32(CODE)