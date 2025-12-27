#!/usr/bin/env python3
"""
Gripper Calibration Test
Moves Servo 3 to various angles to determine Open/Closed positions.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("=== Gripper Calibration Test ===")
print("Observing Servo 3 (Gripper)...")

def test_angle(angle, label):
    print("Moving to " + str(angle) + " (" + label + ")...")
    move_servos_to({3: angle}, 1.0)
    time.sleep(1.0)

# Test sequence
test_angle(90, "Current Release")
test_angle(180, "Current Grip")
test_angle(0, "Possible Close")
test_angle(45, "Check 45")
test_angle(135, "Check 135")
test_angle(90, "Return to 90")

print("=== Calibration Complete ===")
'''

if __name__ == "__main__":
    run_on_esp32(CODE)
