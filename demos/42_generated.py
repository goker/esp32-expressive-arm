#!/usr/bin/env python3
"""
Demo 08: Gentle Pick
Picks up an object with extremely smooth motions.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Gentle Pick ===\\n")

STEPS = 100
DELAY = 0.02

def reach_and_grip():
    print("Reaching forward...")
    start_shoulder = 60
    start_elbow = 100
    target_shoulder = 30
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
    time.sleep(0.2)

    print("Gripping...")
    for angle in range(90, 181, 1):
        set_servo(3, angle)
        time.sleep(DELAY)

    set_servo_direct(3, 180)
    time.sleep(0.5)

def lift_slightly():
    print("Lifting slightly...")
    start_shoulder = 30
    start_elbow = 130
    target_shoulder = 40
    target_elbow = 120

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
    time.sleep(0.2)


def release():
    print("Releasing...")
    for angle in range(180, 90, -1):
        set_servo(3, angle)
        time.sleep(DELAY)

    set_servo_direct(3, 90)
    time.sleep(0.5)


def main_sequence():
    """Main execution flow"""
    reach_and_grip()
    lift_slightly()
    release()
    home()

# -- Execution --
main_sequence()

print("\\n=== Gentle Pick complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Gentle Pick")
    print("=" * 30)
    run_on_esp32(CODE)