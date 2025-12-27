#!/usr/bin/env python3
"""
Demo 08: Pick Up
Simulates picking up an object with smooth movements.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Pick Up ===\\n")

def reach_and_grip():
    """Reaches forward and grips an object."""
    print("Reaching forward...")
    steps = 100
    delay = 0.01

    start_shoulder = 60
    start_elbow = 100
    target_shoulder = 20
    target_elbow = 150

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
    time.sleep(0.2)

    print("Gripping...")
    for angle in range(90, 181, 2):
        set_servo(3, angle)
        time.sleep(0.01)
    set_servo_direct(3, 180)
    time.sleep(0.5)

def lift_object():
    """Lifts the object upwards."""
    print("Lifting...")
    steps = 100
    delay = 0.01

    start_shoulder = 20
    start_elbow = 150
    target_shoulder = 50
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
    time.sleep(0.2)

def main_sequence():
    """Main execution flow"""
    reach_and_grip()
    lift_object()
    home()

# -- Execution --
main_sequence()

print("\\n=== Pick Up complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Pick Up")
    print("=" * 30)
    run_on_esp32(CODE)