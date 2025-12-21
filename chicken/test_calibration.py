#!/usr/bin/env python3
"""
Test your calibration limits
Moves each servo through min → default → max positions
"""

import sys
import os
import json
import time

script_dir = os.path.dirname(os.path.abspath(__file__))
demos_dir = os.path.join(script_dir, "..", "demos")
sys.path.insert(0, demos_dir)

from utils import run_on_esp32


def load_calibration():
    """Load calibration limits"""
    cal_path = os.path.join(script_dir, "calibration_limits.json")
    with open(cal_path, 'r') as f:
        return json.load(f)


def test_servo(servo_num, servo_name, limits):
    """Test one servo through its range"""
    min_angle = limits['min']
    default_angle = limits['default']
    max_angle = limits['max']

    print(f"\n{'='*60}")
    print(f"Testing {servo_name.upper()} (Servo {servo_num})")
    print(f"  Min: {min_angle}° | Default: {default_angle}° | Max: {max_angle}°")
    print(f"{'='*60}")

    code = f'''
from machine import Pin, PWM
import time

pin = {servo_num + 4}  # GPIO pins start at 4
pwm = PWM(Pin(pin), freq=50)

def angle_to_duty(angle):
    return int(round(26 + (angle / 180) * (128 - 26)))

def move_to(angle, label):
    print(f"  → {{label}}: {{angle}}°")
    pwm.duty(angle_to_duty(angle))
    time.sleep(2)

print("\\nMoving {servo_name}...")
move_to({default_angle}, "Default")
time.sleep(1)
move_to({min_angle}, "Min")
time.sleep(1)
move_to({max_angle}, "Max")
time.sleep(1)
move_to({default_angle}, "Back to Default")

print("✓ {servo_name} test complete")
'''

    run_on_esp32(code)


def test_all_servos():
    """Test all servos in sequence"""
    calibration = load_calibration()

    print("\n" + "="*60)
    print("  CALIBRATION TEST")
    print("="*60)
    print("\nLoaded calibration:")
    for name, limits in calibration.items():
        print(f"  {name:10s}: min={limits['min']:3d}° | default={limits['default']:3d}° | max={limits['max']:3d}°")

    input("\nPress Enter to start testing each servo...")

    servos = [
        (0, "base", calibration["base"]),
        (1, "shoulder", calibration["shoulder"]),
        (2, "elbow", calibration["elbow"]),
        (3, "gripper", calibration["gripper"])
    ]

    for servo_num, servo_name, limits in servos:
        test_servo(servo_num, servo_name, limits)
        time.sleep(1)

    print("\n" + "="*60)
    print("  ✓ ALL TESTS COMPLETE")
    print("="*60)


def move_to_defaults():
    """Move all servos to their default positions"""
    calibration = load_calibration()

    defaults = [
        calibration["base"]["default"],
        calibration["shoulder"]["default"],
        calibration["elbow"]["default"],
        calibration["gripper"]["default"]
    ]

    print("\n" + "="*60)
    print("  Moving all servos to DEFAULT positions")
    print("="*60)
    print(f"  Base: {defaults[0]}°")
    print(f"  Shoulder: {defaults[1]}°")
    print(f"  Elbow: {defaults[2]}°")
    print(f"  Gripper: {defaults[3]}°")

    code = f'''
from machine import Pin, PWM
import time

SERVO_PINS = [4, 5, 6, 7]
defaults = {defaults}

def angle_to_duty(angle):
    return int(round(26 + (angle / 180) * (128 - 26)))

print("\\nMoving to defaults...")
for i, pin in enumerate(SERVO_PINS):
    pwm = PWM(Pin(pin), freq=50)
    pwm.duty(angle_to_duty(defaults[i]))
    print(f"  Servo {{i}}: {{defaults[i]}}°")
    time.sleep(0.5)

print("\\n✓ All servos at default positions")
'''

    run_on_esp32(code)


def main():
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command in ["defaults", "home"]:
            move_to_defaults()
        elif command == "test":
            test_all_servos()
        else:
            print(f"Unknown command: {command}")
            print("Usage:")
            print("  python test_calibration.py home      # Move all to home (default) positions")
            print("  python test_calibration.py test      # Test each servo individually")
    else:
        print("Calibration Test")
        print()
        print("Commands:")
        print("  python test_calibration.py home      # Move all to home (default) positions")
        print("  python test_calibration.py test      # Test each servo (min→default→max)")
        print()
        choice = input("What would you like to do? (home/test): ").strip().lower()

        if choice == "test":
            test_all_servos()
        elif choice in ["home", "defaults"]:
            move_to_defaults()
        else:
            print("Invalid choice. Use 'home' or 'test'")


if __name__ == "__main__":
    main()
