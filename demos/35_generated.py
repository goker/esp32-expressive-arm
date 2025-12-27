#!/usr/bin/env python3
"""
Demo 08: Pick Up Object
Reaches forward, grips, and lifts an imaginary object.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Pick Up Object ===\\n")

STEPS = 100
DELAY = 0.015

# Initial positions
start_shoulder = 60
start_elbow = 100

# Reach forward
print("Reaching forward...")
target_shoulder = 30
target_elbow = 140
for i in range(STEPS):
    t = i / STEPS
    s = minimum_jerk(t)
    shoulder = start_shoulder + (target_shoulder - start_shoulder) * s
    elbow = start_elbow + (target_elbow - start_elbow) * s
    set_servo(1, shoulder)
    set_servo(2, elbow)
    time.sleep(DELAY)

time.sleep(0.5)

# Grip
print("Gripping...")
start_gripper = 90
target_gripper = 160
GRIP_STEPS = 50
for i in range(GRIP_STEPS):
    t = i / GRIP_STEPS
    s = minimum_jerk(t)
    gripper = start_gripper + (target_gripper - start_gripper) * s
    set_servo(3, gripper)
    time.sleep(DELAY)

time.sleep(0.5)

# Lift slightly
print("Lifting...")
start_shoulder = target_shoulder
start_elbow = target_elbow
target_shoulder = 40
target_elbow = 130

LIFT_STEPS = 75
for i in range(LIFT_STEPS):
    t = i / LIFT_STEPS
    s = minimum_jerk(t)
    shoulder = start_shoulder + (target_shoulder - start_shoulder) * s
    elbow = start_elbow + (target_elbow - start_elbow) * s
    set_servo(1, shoulder)
    set_servo(2, elbow)
    time.sleep(DELAY)

time.sleep(0.5)

home()
print("\\n=== Pick up complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Pick Up Object")
    print("=" * 30)
    run_on_esp32(CODE)