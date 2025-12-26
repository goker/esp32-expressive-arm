#!/usr/bin/env python3
"""
Demo 08: Smooth Picking Motion
A smooth picking motion with coordinated servo movements.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Smooth Picking Motion ===\\n")

STEPS = 100
DELAY = 0.01

# Define start and end positions for each servo
start_base = 63
end_base = 75
start_shoulder = 60
end_shoulder = 30
start_elbow = 100
end_elbow = 140
start_gripper = 90
end_gripper = 160  # Close gripper

# --- Reach Forward ---
print("Reaching forward...")
for i in range(STEPS):
    t = i / STEPS
    s = minimum_jerk(t)

    base = start_base + (end_base - start_base) * s
    shoulder = start_shoulder + (end_shoulder - start_shoulder) * s
    elbow = start_elbow + (end_elbow - start_elbow) * s

    set_servo(0, base)
    set_servo(1, shoulder)
    set_servo(2, elbow)
    time.sleep(DELAY)

time.sleep(0.2)

# --- Close Gripper ---
print("Closing Gripper...")
for angle in range(start_gripper, end_gripper + 1, 1):
    set_servo(3, angle)
    time.sleep(0.01)

time.sleep(0.2)

# --- Lift Object ---
print("Lifting Object...")
lift_steps = 80
lift_shoulder_start = end_shoulder
lift_shoulder_end = 50
lift_elbow_start = end_elbow
lift_elbow_end = 90
for i in range(lift_steps):
    t = i / lift_steps
    s = minimum_jerk(t)
    shoulder = lift_shoulder_start + (lift_shoulder_end - lift_shoulder_start) * s
    elbow = lift_elbow_start + (lift_elbow_end - lift_elbow_start) * s
    set_servo(1, shoulder)
    set_servo(2, elbow)
    time.sleep(DELAY)

time.sleep(0.2)

# --- Open Gripper ---
print("Opening Gripper...")
for angle in range(end_gripper, 89, -1):
    set_servo(3, angle)
    time.sleep(0.01)

time.sleep(0.2)

# --- Return to home ---
print("Returning to Home...")
home()
print("\\n=== Smooth Picking Complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Smooth Picking Motion")
    print("=" * 30)
    run_on_esp32(CODE)