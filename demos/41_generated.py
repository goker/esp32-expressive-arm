#!/usr/bin/env python3
"""
Demo 08: Pick Up
Simulates picking up an object with smooth, gradual motions.
"""

from utils import SERVO_HEADER, run_on_esp32

CODE = (
    SERVO_HEADER
    + '''
print("\\n=== DEMO 08: Pick Up ===\\n")

STEPS = 80
DELAY = 0.015

def reach_position():
    """Reaches to a pre-defined position."""
    print("Reaching to position...")
    start_shoulder, start_elbow = smooth_pos[1], smooth_pos[2]
    target_shoulder, target_elbow = 30, 140
    for i in range(STEPS):
        t = i / STEPS
        s = minimum_jerk(t)
        set_servo(1, start_shoulder + (target_shoulder - start_shoulder) * s)
        set_servo(2, start_elbow + (target_elbow - start_elbow) * s)
        time.sleep(DELAY)
    set_servo_direct(1, target_shoulder)
    set_servo_direct(2, target_elbow)
    time.sleep(0.2)

def grip_object():
    """Closes the gripper to grab the object."""
    print("Gripping...")
    start_gripper = smooth_pos[3]
    target_gripper = 180
    grip_steps = 50
    for i in range(grip_steps):
        t = i / grip_steps
        s = minimum_jerk(t)
        set_servo(3, start_gripper + (target_gripper - start_gripper) * s)
        time.sleep(DELAY)
    set_servo_direct(3, target_gripper)
    time.sleep(3) # CRITICAL: Wait for physical gripper to close

def lift_object():
    """Lifts the object."""
    print("Lifting...")
    start_shoulder, start_elbow = smooth_pos[1], smooth_pos[2]
    target_shoulder, target_elbow = 50, 120
    lift_steps = 60
    for i in range(lift_steps):
        t = i / lift_steps
        s = minimum_jerk(t)
        set_servo(1, start_shoulder + (target_shoulder - start_shoulder) * s)
        set_servo(2, start_elbow + (target_elbow - start_elbow) * s)
        time.sleep(DELAY)
    set_servo_direct(1, target_shoulder)
    set_servo_direct(2, target_elbow)
    time.sleep(0.2)

def main_sequence():
    """Main execution flow for the pick up task."""
    reach_position()
    grip_object()
    time.sleep(0.5)
    lift_object()

main_sequence()
home()
print("\\n=== Pick up complete! ===")
'''
)

if __name__ == "__main__":
    print("Demo 08: Pick Up")
    print("=" * 30)
    run_on_esp32(CODE)
