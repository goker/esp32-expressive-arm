#!/usr/bin/env python3
"""
Robot Arm Chicken Pickup - Main Script

Precision object pickup demo with smooth, controlled movements.

Usage:
    python main.py 01    # Lower arm for placement
    python main.py 02    # Return to baseline
    python main.py 03    # Pick up object
    python main.py 04    # Drop object
    python main.py 00    # Emergency stop

Stages:
    00 - Emergency stop (return to safe position, no base rotation)
    01 - Lower arm to ground (90,90,90,90) → (90,175,80,120)
    02 - Return to baseline via home() + open gripper to 120°
    03 - Full pickup: lower, close gripper, lift
    04 - Drop: open gripper from 40° to 120°

Features:
    - Servo calibration system (servo_config.json)
    - Global speed control via SPEED_MULTIPLIER
    - Minimum jerk trajectory for smooth motion
    - Direct servo control for immediate response

See chicken/README.md for full documentation.
"""

import sys
import os

# Add demos folder to path
script_dir = os.path.dirname(os.path.abspath(__file__))
demos_dir = os.path.join(script_dir, "..", "demos")
sys.path.insert(0, demos_dir)

from utils import run_on_esp32, SERVO_HEADER
from servo_utils import get_calibrated_angles

def stage_00_emergency_stop():
    """00: Emergency stop - return to home without rotating base"""
    code = SERVO_HEADER + get_calibrated_angles() + '''
# Override home() to do nothing (prevent violent snap at startup)
def home():
    pass

_original_set_servo_direct = set_servo_direct
def set_servo_direct(servo_num, angle):
    calibrated = calibrated_angle(servo_num, angle)
    _original_set_servo_direct(servo_num, calibrated)

print("\\n=== EMERGENCY STOP ===\\n")

# Capture current positions
start_pos = [current_pos[i] for i in range(4)]

# Only move shoulder, elbow, gripper to 90 (leave base alone)
targets = [start_pos[0], 90, 90, 90]

print(f"Returning to safe position (base stays at {start_pos[0]}°)...")

steps = int(300 * SPEED_MULTIPLIER)
delay = 0.05 * SPEED_MULTIPLIER

for step in range(steps + 1):
    progress = step / steps
    smooth = 10 * (progress ** 3) - 15 * (progress ** 4) + 6 * (progress ** 5)

    for i in range(1, 4):  # Skip base (0)
        angle = start_pos[i] + (targets[i] - start_pos[i]) * smooth
        set_servo_direct(i, int(angle))

    time.sleep(delay)

print("\\n=== SAFE ===")
'''
    return code

def stage_01_lower_for_placement():
    """01: Lower arm and open gripper for object placement"""
    code = SERVO_HEADER + get_calibrated_angles() + '''
# Override home() to do nothing (prevent violent snap at startup)
def home():
    pass

_original_set_servo_direct = set_servo_direct
def set_servo_direct(servo_num, angle):
    calibrated = calibrated_angle(servo_num, angle)
    _original_set_servo_direct(servo_num, calibrated)

print("\\n=== LOWERING ARM FOR PLACEMENT ===\\n")

# Start from home (90, 90, 90, 90)
start_pos = [90, 90, 90, 90]

# Target: base center, shoulder down, elbow forward, gripper open
targets = [90, 175, 80, 120]

print("Lowering arm to ground and opening gripper...")

steps = int(250 * SPEED_MULTIPLIER)
delay = 0.05 * SPEED_MULTIPLIER

for step in range(steps + 1):
    progress = step / steps
    smooth = 10 * (progress ** 3) - 15 * (progress ** 4) + 6 * (progress ** 5)

    for i in range(4):
        angle = start_pos[i] + (targets[i] - start_pos[i]) * smooth
        set_servo_direct(i, int(angle))

    time.sleep(delay)

print("\\n=== ARM LOWERED ===")
print("Place chicken in front of gripper, then run: python main.py 02")
'''
    return code

def stage_02_return_to_baseline():
    """02: home() already moved arm to 90,90,90,90 - just open gripper"""
    code = SERVO_HEADER + get_calibrated_angles() + '''
_original_set_servo_direct = set_servo_direct
def set_servo_direct(servo_num, angle):
    calibrated = calibrated_angle(servo_num, angle)
    _original_set_servo_direct(servo_num, calibrated)

print("\\n=== RETURNING TO BASELINE ===\\n")
print("Arm already at home (90,90,90,90) from home() call")
print("Opening gripper slowly...")

# home() already set everything to 90
# Just need to slowly open gripper from 90 to 120
steps = int(150 * SPEED_MULTIPLIER)
delay = 0.04 * SPEED_MULTIPLIER

for step in range(steps + 1):
    progress = step / steps
    angle = 90 + (120 - 90) * progress
    set_servo_direct(3, int(angle))
    time.sleep(delay)

print("\\n=== BASELINE SET ===")
print("Position: (90, 90, 90, 120) - Ready to pick!")
'''
    return code

def stage_03_pick_chicken():
    """03: Override home() to skip init, lower to position, grab, then manually call home()"""
    code = SERVO_HEADER + get_calibrated_angles() + '''
# Override home() to do nothing initially
_original_home = home
def home():
    pass

_original_set_servo_direct = set_servo_direct
def set_servo_direct(servo_num, angle):
    calibrated = calibrated_angle(servo_num, angle)
    _original_set_servo_direct(servo_num, calibrated)

print("\\n=== PICKING UP CHICKEN ===\\n")

# PHASE 1: Lower to chicken
print("Phase 1: Lowering to chicken...")
start_pos = [90, 90, 90, 90]
lower_targets = [90, 175, 80, 120]

steps = int(250 * SPEED_MULTIPLIER)
delay = 0.05 * SPEED_MULTIPLIER

for step in range(steps + 1):
    progress = step / steps
    smooth = 10 * (progress ** 3) - 15 * (progress ** 4) + 6 * (progress ** 5)

    for i in range(4):
        angle = start_pos[i] + (lower_targets[i] - start_pos[i]) * smooth
        set_servo_direct(i, int(angle))

    time.sleep(delay)

time.sleep(0.3)

# PHASE 2: Close gripper
print("Phase 2: Closing gripper...")
steps = int(100 * SPEED_MULTIPLIER)
delay = 0.04 * SPEED_MULTIPLIER

for step in range(steps + 1):
    progress = step / steps
    angle = 120 + (40 - 120) * progress
    set_servo_direct(3, int(angle))
    time.sleep(delay)

print("Gripped!")
time.sleep(0.5)

# PHASE 3: Lift smoothly to home position - arm only, not gripper
print("Phase 3: Lifting chicken smoothly...")
start_pos = [90, 175, 80]
lift_targets = [90, 90, 90]

steps = int(250 * SPEED_MULTIPLIER)
delay = 0.05 * SPEED_MULTIPLIER

for step in range(steps + 1):
    progress = step / steps
    smooth = 10 * (progress ** 3) - 15 * (progress ** 4) + 6 * (progress ** 5)

    for i in range(3):  # Only base, shoulder, elbow
        angle = start_pos[i] + (lift_targets[i] - start_pos[i]) * smooth
        set_servo_direct(i, int(angle))

    time.sleep(delay)

print("\\n=== CHICKEN LIFTED! ===")
print("Position: (90, 90, 90, 40) - gripper closed")
'''
    return code

def stage_04_drop_chicken():
    """04: Open gripper (already at home position)"""
    code = SERVO_HEADER + get_calibrated_angles() + '''
# Override home() to do nothing (prevent violent snap at startup)
def home():
    pass

_original_set_servo_direct = set_servo_direct
def set_servo_direct(servo_num, angle):
    calibrated = calibrated_angle(servo_num, angle)
    _original_set_servo_direct(servo_num, calibrated)

print("\\n=== DROPPING CHICKEN ===\\n")

# Just open gripper (arm is already at home position from stage 03)
print("Opening gripper...")
start_gripper = 40
target_gripper = 120

steps = int(80 * SPEED_MULTIPLIER)
delay = 0.04 * SPEED_MULTIPLIER

for step in range(steps + 1):
    progress = step / steps
    angle = start_gripper + (target_gripper - start_gripper) * progress
    set_servo_direct(3, int(angle))
    time.sleep(delay)

print("\\n=== MISSION COMPLETE ===")
print("Chicken dropped! All servos at home (90, 90, 90, 120)")
'''
    return code

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py [00|01|02|03|04]")
        print()
        print("Stages:")
        print("  00 - Emergency stop (return to safe position)")
        print("  01 - Lower arm for chicken placement")
        print("  02 - Return to baseline")
        print("  03 - Pick up chicken (lower, grab, lift)")
        print("  04 - Drop chicken and return home")
        sys.exit(1)

    stage = sys.argv[1]

    stages = {
        "00": stage_00_emergency_stop,
        "01": stage_01_lower_for_placement,
        "02": stage_02_return_to_baseline,
        "03": stage_03_pick_chicken,
        "04": stage_04_drop_chicken,
    }

    if stage not in stages:
        print(f"Error: Unknown stage '{stage}'")
        print("Valid stages: 00, 01, 02, 03, 04")
        sys.exit(1)

    print("=" * 60)
    print(f"  STAGE {stage}")
    print("=" * 60)

    code = stages[stage]()
    run_on_esp32(code)

if __name__ == "__main__":
    main()
