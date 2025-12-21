#!/usr/bin/env python3
"""
Robot Arm Chicken Pickup - YAML-driven motion controller

All motion sequences defined in correct_sequence.yaml
MicroPython code template in micropython_runner.py

Usage:
    python main.py 00    # Emergency stop
    python main.py 01    # Lower arm for placement
    python main.py 02    # Return to baseline
    python main.py 03    # Pick up object
    python main.py 04    # Drop object
"""

import sys
import os
import yaml

script_dir = os.path.dirname(os.path.abspath(__file__))
demos_dir = os.path.join(script_dir, "..", "demos")
sys.path.insert(0, demos_dir)

from utils import run_on_esp32
from servo_utils import get_calibrated_angles
from micropython_runner import TEMPLATE


def load_sequence():
    """Load motion sequence from YAML"""
    yaml_path = os.path.join(script_dir, "correct_sequence.yaml")
    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f)


def generate_stage_code(stage_num):
    """Generate MicroPython code for a stage"""
    sequence = load_sequence()
    stage = sequence['stages'][stage_num]

    # Generate waypoint commands
    waypoint_commands = []
    for i, wp in enumerate(stage['waypoints']):
        pos = wp['position']
        dur = wp['duration']
        desc = wp['description']

        waypoint_commands.append(f'''
print("  → {desc}")
move_to_position({pos}, {dur})
time.sleep(0.3)
''')

    # Fill template
    code = TEMPLATE.format(
        calibration_code=get_calibrated_angles(),
        stage_num=stage_num,
        stage_name=stage['name'].upper(),
        waypoint_commands=''.join(waypoint_commands)
    )

    return code


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py [00|01|02|03|04]")
        print()
        print("Stages:")
        print("  00 - Emergency stop")
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

    print("=" * 60)
    print(f"  STAGE {stage}")
    print("=" * 60)

    code = generate_stage_code(stage)
    run_on_esp32(code)


if __name__ == "__main__":
    main()
