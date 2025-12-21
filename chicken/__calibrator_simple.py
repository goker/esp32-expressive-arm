#!/usr/bin/env python3
"""
Simple Calibrator - Just shoulder and elbow
"""

import sys
import os
import json

# Add demos folder to path
script_dir = os.path.dirname(os.path.abspath(__file__))
demos_dir = os.path.join(script_dir, '..', 'demos')
sys.path.insert(0, demos_dir)

from utils import run_on_esp32, SERVO_HEADER

def test_shoulder():
    """Test shoulder movement"""
    print(f"\n{'='*60}")
    print(f"Testing: SHOULDER (up/down)")
    print(f"{'='*60}")

    CODE = SERVO_HEADER + '''
print("\\nStarting at 90° (neutral)...")
set_servo_direct(1, 90)
time.sleep(1)

print("Moving to 130° (testing direction 1)...")
for angle in range(90, 131, 2):
    set_servo_direct(1, angle)
    time.sleep(0.02)
time.sleep(1.5)

print("Moving to 60° (testing direction 2)...")
for angle in range(130, 59, -2):
    set_servo_direct(1, angle)
    time.sleep(0.02)
time.sleep(1.5)

print("Returning to 90° (neutral)...")
set_servo_direct(1, 90)
time.sleep(0.5)
'''

    run_on_esp32(CODE)

    print("\nWhat did the SHOULDER do?")
    print("When it moved to 130°, the shoulder went:")
    print("  1. DOWN (toward ground)")
    print("  2. UP (toward sky)")

    while True:
        choice = input("\nEnter 1 or 2: ").strip()
        if choice in ['1', '2']:
            return choice == '1'  # True if 130° = down (normal), False if up (inverted)
        print("Please enter 1 or 2")

def test_elbow():
    """Test elbow movement"""
    print(f"\n{'='*60}")
    print(f"Testing: ELBOW (forward/backward)")
    print(f"{'='*60}")

    CODE = SERVO_HEADER + '''
print("\\nStarting at 90° (neutral)...")
set_servo_direct(2, 90)
time.sleep(1)

print("Moving to 120° (testing direction 1)...")
for angle in range(90, 121, 2):
    set_servo_direct(2, angle)
    time.sleep(0.02)
time.sleep(1.5)

print("Moving to 60° (testing direction 2)...")
for angle in range(120, 59, -2):
    set_servo_direct(2, angle)
    time.sleep(0.02)
time.sleep(1.5)

print("Returning to 90° (neutral)...")
set_servo_direct(2, 90)
time.sleep(0.5)
'''

    run_on_esp32(CODE)

    print("\nWhat did the ELBOW do?")
    print("When it moved to 120°, the elbow went:")
    print("  1. FORWARD (extended out front)")
    print("  2. BACKWARD (pulled toward back)")

    while True:
        choice = input("\nEnter 1 or 2: ").strip()
        if choice in ['1', '2']:
            return choice == '1'  # True if 120° = forward (normal), False if backward (inverted)
        print("Please enter 1 or 2")

def main():
    print("="*60)
    print("  SIMPLE CALIBRATION - Shoulder & Elbow Only")
    print("="*60)
    print("\nWatch the arm carefully and answer the questions.")

    input("\nReady? Press Enter to start...")

    # Test shoulder
    shoulder_130_is_down = test_shoulder()
    print(f"\n✓ Shoulder: 130° goes {'DOWN' if shoulder_130_is_down else 'UP'}")

    # Test elbow
    elbow_120_is_forward = test_elbow()
    print(f"✓ Elbow: 120° goes {'FORWARD' if elbow_120_is_forward else 'BACKWARD'}")

    # Build config
    config = {
        "servos": {
            "base": {"pin": 0, "inverted": False},  # Not calibrating
            "shoulder": {
                "pin": 1,
                "inverted": not shoulder_130_is_down,  # If 130 goes UP, it's inverted
                "description": "Shoulder (up/down)"
            },
            "elbow": {
                "pin": 2,
                "inverted": not elbow_120_is_forward,  # If 120 goes BACK, it's inverted
                "description": "Elbow (forward/backward)"
            },
            "gripper": {"pin": 3, "inverted": False}  # Not calibrating
        }
    }

    # Save config
    config_path = os.path.join(script_dir, 'servo_config.json')
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print("\n" + "="*60)
    print("  CALIBRATION COMPLETE!")
    print("="*60)
    print(f"\nSaved to: servo_config.json")
    print("\nCalibration summary:")
    print(f"  Shoulder: {'INVERTED' if config['servos']['shoulder']['inverted'] else 'NORMAL'} (130° = {'UP' if not shoulder_130_is_down else 'DOWN'})")
    print(f"  Elbow:    {'INVERTED' if config['servos']['elbow']['inverted'] else 'NORMAL'} (120° = {'BACKWARD' if not elbow_120_is_forward else 'FORWARD'})")

    print("\nAll chicken scripts will now use this calibration.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCalibration cancelled.")
        sys.exit(0)
