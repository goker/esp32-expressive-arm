#!/usr/bin/env python3
"""
00: EMERGENCY STOP - Return to home position immediately
"""

import sys
import os

# Add demos folder to path (relative to this script's location)
script_dir = os.path.dirname(os.path.abspath(__file__))
demos_dir = os.path.join(script_dir, '..', 'demos')
sys.path.insert(0, demos_dir)

from utils import run_on_esp32, SERVO_HEADER
from servo_utils import get_calibrated_angles

CODE = SERVO_HEADER + get_calibrated_angles() + '''
# Wrap servo functions to use calibration
_original_set_servo = set_servo
_original_set_servo_direct = set_servo_direct

def set_servo(servo_num, target):
    """Set servo with calibration applied"""
    calibrated = calibrated_angle(servo_num, target)
    _original_set_servo(servo_num, calibrated)

def set_servo_direct(servo_num, angle):
    """Set servo directly with calibration applied"""
    calibrated = calibrated_angle(servo_num, angle)
    _original_set_servo_direct(servo_num, calibrated)

print("\\n=== EMERGENCY STOP - RETURNING HOME ===\\n")

# Slowly return to safe position WITHOUT rotating base
print("Returning to safe position (no base rotation)...")

# Get final positions - keep base wherever it is, return others to 90
target_positions = [None, 90, 90, 90]  # Base stays, shoulder/elbow/gripper to 90

# Capture start positions ONCE before loop
start_positions = [None, current_pos[1], current_pos[2], current_pos[3]]

steps = int(500 * SPEED_MULTIPLIER)  # EXTRA slow for emergency return
delay = 0.08 * SPEED_MULTIPLIER  # Slower delay

for step in range(steps):
    t = step / steps
    s = minimum_jerk(t)

    # Use set_servo_direct for immediate response (no smoothing)
    # Don't move base (servo 0), only move shoulder, elbow, gripper
    for i in range(1, 4):
        set_servo_direct(i, int(start_positions[i] + (target_positions[i] - start_positions[i]) * s))

    time.sleep(delay)

print("\\n=== SAFE - ARM AT REST POSITION ===")
print("Base position unchanged")
'''

if __name__ == "__main__":
    print("=" * 50)
    print("  🔴 EMERGENCY STOP - RETURNING TO HOME")
    print("=" * 50)
    run_on_esp32(CODE)
