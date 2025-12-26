#!/usr/bin/env python3
"""
Demo 08: Ground Positioning
Positions the arm near the ground with open gripper for object placement.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Ground Positioning ===\\n")

STEPS = 100
DELAY = 0.02

# Positioning near ground
print("Moving to ground position...")
for i in range(STEPS):
    t = i / STEPS
    s = minimum_jerk(t)

    shoulder = 60 + (90 - 60) * s  # Move shoulder down
    elbow = 100 + (40 - 100) * s    # Extend elbow

    set_servo(1, shoulder)
    set_servo(2, elbow)
    time.sleep(DELAY)

# Open the gripper
print("Opening gripper...")
for angle in range(90, 180, 1):
    set_servo(3, angle)
    time.sleep(0.01)

time.sleep(1)

home()
print("\\n=== Ground positioning complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Ground Positioning")
    print("=" * 30)
    run_on_esp32(CODE)