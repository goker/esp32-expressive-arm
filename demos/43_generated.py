#!/usr/bin/env python3
"""
Demo 08: Pick Up
Simulates picking up an object with very smooth motions.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Pick Up ===\\n")

def main_sequence():
    """Main execution flow for the pick up task."""
    reach_forward()
    grip()
    lift()
    home()

def reach_forward():
    """Extends the arm forward."""
    print("Reaching forward...")
    steps = 100
    delay = 0.02
    start_shoulder = smooth_pos[1]
    start_elbow = smooth_pos[2]
    target_shoulder = 35
    target_elbow = 140
    for i in range(steps):
        t = i / steps
        s = minimum_jerk(t)
        shoulder = start_shoulder + (target_shoulder - start_shoulder) * s
        elbow = start_elbow + (target_elbow - start_elbow) * s
        set_servo(1, shoulder)
        set_servo(2, elbow)
        time.sleep(delay)
    set_servo_direct(1, target_shoulder)
    set_servo_direct(2, target_elbow)
    time.sleep(0.5)

def grip():
    """Closes the gripper."""
    print("Gripping...")
    start_angle = smooth_pos[3]
    target_angle = 180
    steps = 50
    delay = 0.02
    for i in range(steps):
        angle = start_angle + (target_angle - start_angle) * i / steps
        set_servo(3, angle)
        time.sleep(delay)
    set_servo_direct(3, target_angle)
    time.sleep(1.5)

def lift():
    """Lifts the arm."""
    print("Lifting...")
    steps = 100
    delay = 0.02
    start_shoulder = smooth_pos[1]
    start_elbow = smooth_pos[2]
    target_shoulder = 55
    target_elbow = 120
    for i in range(steps):
        t = i / steps
        s = minimum_jerk(t)
        shoulder = start_shoulder + (target_shoulder - start_shoulder) * s
        elbow = start_elbow + (target_elbow - start_elbow) * s
        set_servo(1, shoulder)
        set_servo(2, elbow)
        time.sleep(delay)
    set_servo_direct(1, target_shoulder)
    set_servo_direct(2, target_elbow)
    time.sleep(0.5)

main_sequence()

print("\\n=== Pick up complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Pick Up")
    print("=" * 30)
    run_on_esp32(CODE)