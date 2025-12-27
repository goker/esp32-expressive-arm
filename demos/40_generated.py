#!/usr/bin/env python3
"""
Demo 08: Pick Up Object
Reaches forward, grips, lifts slightly, and returns to home position.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Pick Up Object ===\\n")

STEPS = 100
DELAY = 0.01

# 1. Reach forward
print("Reaching forward...")
start_shoulder = 60
start_elbow = 100
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
set_servo_direct(1, target_shoulder)
set_servo_direct(2, target_elbow)
time.sleep(0.5)

# 2. Grip
print("Gripping...")
start_gripper = 90
target_gripper = 180

for angle in range(start_gripper, target_gripper + 1, 2):
    set_servo(3, angle)
    time.sleep(DELAY)
set_servo_direct(3, target_gripper)
time.sleep(1.0)  # IMPORTANT: Wait for the gripper to close

# 3. Lift slightly
print("Lifting slightly...")
start_shoulder = 30
start_elbow = 140
target_shoulder = 40
target_elbow = 130

for i in range(STEPS):
    t = i / STEPS
    s = minimum_jerk(t)
    shoulder = start_shoulder + (target_shoulder - start_shoulder) * s
    elbow = start_elbow + (target_elbow - start_elbow) * s
    set_servo(1, shoulder)
    set_servo(2, elbow)
    time.sleep(DELAY)
set_servo_direct(1, target_shoulder)
set_servo_direct(2, target_elbow)
time.sleep(0.5)

home()
print("\\n=== Pick up object complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Pick Up Object")
    print("=" * 30)
    run_on_esp32(CODE)