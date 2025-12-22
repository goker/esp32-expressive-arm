#!/usr/bin/env python3
"""
Robot Arm Motion Controller - Pure YAML/Calibration driven

All positions come from:
- calibration_limits.json (min/max/default for each servo)
- correct_sequence.yaml (motion sequences using keywords)

Usage: python main.py [00|01|02|03|04]
"""

import sys
import os
import yaml
import json

script_dir = os.path.dirname(os.path.abspath(__file__))
demos_dir = os.path.join(script_dir, "..", "demos")
sys.path.insert(0, demos_dir)

from utils import find_port
import subprocess


def load_calibration():
    """Load calibration limits from JSON"""
    cal_path = os.path.join(script_dir, "calibration_limits.json")
    with open(cal_path, 'r') as f:
        return json.load(f)


def load_sequence():
    """Load motion sequence from YAML"""
    yaml_path = os.path.join(script_dir, "correct_sequence.yaml")
    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f)


def resolve_position(position_spec, calibration):
    """Convert keywords (min/max/default) to actual angles"""
    servo_names = ['base', 'shoulder', 'elbow', 'gripper']
    resolved = []

    for i, spec in enumerate(position_spec):
        servo_name = servo_names[i]

        if isinstance(spec, str):
            if spec in ['min', 'max', 'default']:
                resolved.append(calibration[servo_name][spec])
            else:
                raise ValueError(f"Invalid keyword '{spec}' for {servo_name}")
        else:
            resolved.append(int(spec))

    return resolved


def run_stage(stage_num):
    """Run a stage - load YAML, resolve positions, send to robot"""
    calibration = load_calibration()
    sequence = load_sequence()
    stage = sequence['stages'][stage_num]

    print("\n" + "=" * 60)
    print(f"  STAGE {stage_num}: {stage['name'].upper()}")
    print("=" * 60)

    # Resolve all waypoints
    waypoints_resolved = []
    for i, wp in enumerate(stage['waypoints']):
        resolved_pos = resolve_position(wp['position'], calibration)
        waypoints_resolved.append({
            'position': resolved_pos,
            'duration': wp['duration'],
            'description': wp['description']
        })

        print(f"\nWaypoint {i+1}: {wp['description']}")
        print(f"  YAML: {wp['position']}")
        print(f"  Resolved: {resolved_pos}")
        print(f"  Duration: {wp['duration']}s")

    # Get default positions from calibration
    defaults = [
        calibration['base']['default'],
        calibration['shoulder']['default'],
        calibration['elbow']['default'],
        calibration['gripper']['default']
    ]

    # Generate MicroPython code
    micropython_code = f"""
from machine import Pin, PWM
import time

SERVO_PINS = [4, 5, 6, 7]
# Initialize current_pos from calibrated defaults (not hardcoded 90)
current_pos = {defaults}

servos = []
for pin in SERVO_PINS:
    pwm = PWM(Pin(pin), freq=50)
    servos.append(pwm)

def angle_to_duty(angle):
    return int(round(26 + (angle / 180) * (128 - 26)))

def set_servo(servo_num, angle):
    duty = angle_to_duty(angle)
    servos[servo_num].duty(duty)
    current_pos[servo_num] = angle

def move_to_position(target, duration):
    start = [current_pos[i] for i in range(4)]

    steps = int(duration / 0.05)
    if steps == 0:
        steps = 1

    for step in range(steps + 1):
        progress = step / steps
        smooth = 10 * (progress ** 3) - 15 * (progress ** 4) + 6 * (progress ** 5)

        for i in range(4):
            angle = start[i] + (target[i] - start[i]) * smooth
            set_servo(i, int(angle))

        time.sleep(0.05)

print("\\n=== STAGE {stage_num}: {stage['name'].upper()} ===\\n")
print("Starting from calibrated defaults:", current_pos)
"""

    # Add waypoint commands
    for wp in waypoints_resolved:
        micropython_code += f"""
print("  → {wp['description']}")
move_to_position({wp['position']}, {wp['duration']})
time.sleep(0.3)
"""

    micropython_code += """
print("\\nFinal position:", current_pos)
print("=== COMPLETE ===")
"""

    # Send to robot
    port = find_port()
    if not port:
        print("\nERROR: No USB port found!")
        sys.exit(1)

    print(f"\nSending to robot on {port}...")

    # Use full path to mpremote from venv
    venv_dir = os.path.join(script_dir, "..", ".venv")
    mpremote_path = os.path.join(venv_dir, "bin", "mpremote")

    if not os.path.exists(mpremote_path):
        # Fallback to system mpremote
        mpremote_path = "mpremote"

    result = subprocess.run(
        [mpremote_path, "connect", port, "exec", micropython_code],
        capture_output=False
    )

    if result.returncode != 0:
        print("\nERROR: Failed to execute!")
        sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py [00|01|02|03|04]")
        print()
        print("Stages:")
        print("  00 - Emergency stop (move to defaults)")
        print("  01 - Lower for placement")
        print("  02 - Return to baseline")
        print("  03 - Pick up object")
        print("  04 - Drop object")
        sys.exit(1)

    stage = sys.argv[1]
    valid_stages = ["00", "01", "02", "03", "04"]

    if stage not in valid_stages:
        print(f"Error: Unknown stage '{stage}'")
        print(f"Valid stages: {', '.join(valid_stages)}")
        sys.exit(1)

    run_stage(stage)


if __name__ == "__main__":
    main()
