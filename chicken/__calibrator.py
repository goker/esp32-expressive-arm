#!/usr/bin/env python3
"""
Servo Calibrator - Learn how your servos actually move
Creates servo_config.json with calibration data
"""

import sys
import os
import json

# Add demos folder to path
script_dir = os.path.dirname(os.path.abspath(__file__))
demos_dir = os.path.join(script_dir, '..', 'demos')
sys.path.insert(0, demos_dir)

from utils import run_on_esp32, SERVO_HEADER

SERVO_NAMES = ["Base", "Shoulder", "Elbow", "Gripper"]
SERVO_DESCRIPTIONS = [
    "Base (rotation left/right)",
    "Shoulder (up/down)",
    "Elbow (bend forward/backward)",
    "Gripper (open/close)"
]

def test_servo(servo_num, servo_name):
    """Test a servo and ask user what happened"""
    print(f"\n{'='*60}")
    print(f"Testing: {servo_name}")
    print(f"{'='*60}")

    CODE = SERVO_HEADER + f'''
print("\\nStarting at 90° (neutral)...")
set_servo_direct({servo_num}, 90)
time.sleep(1)

print("Moving to 60° (what we think is one direction)...")
for angle in range(90, 59, -2):
    set_servo_direct({servo_num}, angle)
    time.sleep(0.02)
time.sleep(1)

print("Moving to 120° (what we think is opposite direction)...")
for angle in range(60, 121, 2):
    set_servo_direct({servo_num}, angle)
    time.sleep(0.02)
time.sleep(1)

print("Returning to 90° (neutral)...")
set_servo_direct({servo_num}, 90)
time.sleep(0.5)
'''

    run_on_esp32(CODE)

    print(f"\nWhat did the {servo_name} do?")
    print("When it moved from 90° to 60°, it went:")

    if servo_num == 0:  # Base
        print("  1. LEFT (counterclockwise)")
        print("  2. RIGHT (clockwise)")
    elif servo_num == 1:  # Shoulder
        print("  1. UP (raised)")
        print("  2. DOWN (lowered)")
    elif servo_num == 2:  # Elbow
        print("  1. FORWARD (extended toward front)")
        print("  2. BACKWARD (pulled toward back)")
    elif servo_num == 3:  # Gripper
        print("  1. OPENED (spread apart)")
        print("  2. CLOSED (squeezed together)")

    while True:
        choice = input("\nEnter 1 or 2: ").strip()
        if choice in ['1', '2']:
            return choice == '1'  # True if normal, False if inverted
        print("Please enter 1 or 2")

def main():
    print("="*60)
    print("  SERVO CALIBRATION WIZARD")
    print("="*60)
    print("\nThis will test each servo to learn how YOUR robot moves.")
    print("Watch carefully and answer the questions.")
    print("\nPress Ctrl+C at any time to cancel.")

    input("\nReady? Press Enter to start...")

    config = {
        "servos": {}
    }

    for i in range(4):
        is_normal = test_servo(i, SERVO_DESCRIPTIONS[i])
        config["servos"][SERVO_NAMES[i].lower()] = {
            "pin": i,
            "inverted": not is_normal,  # Store if it's inverted
            "description": SERVO_DESCRIPTIONS[i]
        }
        print(f"✓ {SERVO_NAMES[i]} calibrated: {'NORMAL' if is_normal else 'INVERTED'}")

    # Save config
    config_path = os.path.join(script_dir, 'servo_config.json')
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print("\n" + "="*60)
    print("  CALIBRATION COMPLETE!")
    print("="*60)
    print(f"\nSaved to: {config_path}")
    print("\nCalibration summary:")
    for name, data in config["servos"].items():
        status = "INVERTED" if data["inverted"] else "NORMAL"
        print(f"  {name.capitalize():10} - {status}")

    print("\nAll chicken scripts will now use this calibration.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCalibration cancelled.")
        sys.exit(0)
