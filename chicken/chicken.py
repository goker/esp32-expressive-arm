#!/usr/bin/env python3
"""
Chicken - Workflow Executor

Executes workflow JSON files created by workflow_designer.py

Usage:
    python chicken.py workflow_name.json
    python chicken.py workflows/my_task.json
"""

import json
import os
import sys
import subprocess

script_dir = os.path.dirname(os.path.abspath(__file__))
demos_dir = os.path.join(script_dir, "..", "demos")
sys.path.insert(0, demos_dir)

from utils import find_port


def load_workflow(filepath):
    """Load workflow from JSON file"""
    if not os.path.exists(filepath):
        # Try workflows directory
        alt_path = os.path.join(script_dir, "workflows", filepath)
        if os.path.exists(alt_path):
            filepath = alt_path
        else:
            print(f"Error: Workflow file not found: {filepath}")
            sys.exit(1)

    with open(filepath, 'r') as f:
        return json.load(f)


def load_servo_config():
    """Load servo configuration with inversion settings"""
    config_path = os.path.join(script_dir, "servo_config.json")
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except:
        # Default: no inversions
        return {
            "servos": {
                "base": {"pin": 0, "inverted": False},
                "shoulder": {"pin": 1, "inverted": False},
                "elbow": {"pin": 2, "inverted": False},
                "gripper": {"pin": 3, "inverted": False}
            }
        }


def apply_inversions(logical_positions, servo_config):
    """Convert logical positions to physical positions based on servo inversions"""
    servo_names = ["base", "shoulder", "elbow", "gripper"]
    physical_positions = []

    for i, logical_angle in enumerate(logical_positions):
        servo_name = servo_names[i]
        is_inverted = servo_config['servos'][servo_name].get('inverted', False)

        if is_inverted:
            physical_angle = 180 - logical_angle
        else:
            physical_angle = logical_angle

        physical_positions.append(physical_angle)

    return physical_positions


def execute_workflow(workflow):
    """Execute a workflow on the robot"""
    print("\n" + "=" * 60)
    print(f"  🤖 Executing: {workflow['name']}")
    print("=" * 60)

    if workflow.get('description'):
        print(f"\n{workflow['description']}\n")

    print(f"Steps: {len(workflow['steps'])}")
    print()

    # Load servo config for inversions
    servo_config = load_servo_config()
    inverted_servos = [name for name, cfg in servo_config['servos'].items() if cfg.get('inverted', False)]
    if inverted_servos:
        print(f"Note: Applying inversions for {', '.join(inverted_servos)} servo(s)")

    # Find port
    port = find_port()
    if not port:
        print("ERROR: No USB port found!")
        sys.exit(1)

    print(f"Connected to: {port}\n")

    # Convert all workflow positions to physical angles
    converted_steps = []
    for step in workflow['steps']:
        logical_pos = step['position']
        physical_pos = apply_inversions(logical_pos, servo_config)
        converted_steps.append({
            'name': step['name'],
            'position': physical_pos,
            'duration': step['duration']
        })
        print(f"  {step['name']}: {logical_pos} -> {physical_pos}")

    print()

    # Generate MicroPython code
    micropython_code = """
from machine import Pin, PWM
import time

SERVO_PINS = [4, 5, 6, 7]
current_pos = [90, 90, 90, 90]

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
        # Minimum jerk trajectory
        smooth = 10 * (progress ** 3) - 15 * (progress ** 4) + 6 * (progress ** 5)

        for i in range(4):
            angle = start[i] + (target[i] - start[i]) * smooth
            set_servo(i, int(angle))

        time.sleep(0.05)

print("Starting workflow execution...")
"""

    # Add each step (using physical positions)
    for i, step in enumerate(converted_steps):
        micropython_code += f"""
print("\\n[{i+1}/{len(converted_steps)}] {step['name']}")
print("  Position: {step['position']}")
print("  Duration: {step['duration']}s")
move_to_position({step['position']}, {step['duration']})
time.sleep(0.3)
"""

    micropython_code += """
print("\\n✓ Workflow complete!")
print(f"Final position: {current_pos}")
"""

    # Execute on robot
    print("Executing workflow on robot...")
    print("-" * 60)

    result = subprocess.run(
        ["mpremote", "connect", port, "exec", micropython_code],
        capture_output=False
    )

    print("-" * 60)

    if result.returncode != 0:
        print("\nError executing workflow!")
        sys.exit(1)

    print("\n✓ Workflow execution complete!")


def list_workflows():
    """List all available workflows"""
    workflows_dir = os.path.join(script_dir, "workflows")

    if not os.path.exists(workflows_dir):
        print("No workflows directory found. Create workflows using workflow_designer.py")
        return

    files = [f for f in os.listdir(workflows_dir) if f.endswith(".json")]

    if not files:
        print("No workflows found. Create workflows using workflow_designer.py")
        return

    print("\nAvailable workflows:")
    print("-" * 60)

    for filename in sorted(files):
        filepath = os.path.join(workflows_dir, filename)
        try:
            with open(filepath, 'r') as f:
                workflow = json.load(f)
                print(f"\n  {filename}")
                print(f"  Name: {workflow.get('name', 'Untitled')}")
                print(f"  Steps: {len(workflow.get('steps', []))}")
                if workflow.get('description'):
                    print(f"  Description: {workflow['description']}")
        except Exception as e:
            print(f"\n  {filename} (error loading: {e})")

    print("\n" + "-" * 60)
    print("\nUsage: python chicken.py <filename>")


def main():
    print("\n" + "=" * 60)
    print("  🐔 Chicken - Workflow Executor")
    print("=" * 60)

    if len(sys.argv) < 2:
        print("\nUsage: python chicken.py <workflow.json>")
        print("\nExamples:")
        print("  python chicken.py my_workflow.json")
        print("  python chicken.py workflows/pickup.json")
        print("\nList workflows:")
        print("  python chicken.py --list")
        sys.exit(1)

    if sys.argv[1] == "--list" or sys.argv[1] == "-l":
        list_workflows()
        sys.exit(0)

    workflow_file = sys.argv[1]
    workflow = load_workflow(workflow_file)

    # Show workflow info
    print(f"\nLoaded: {workflow['name']}")
    print(f"Steps: {len(workflow['steps'])}")

    for i, step in enumerate(workflow['steps']):
        print(f"  {i+1}. {step['name']} - {step['duration']}s")

    print()
    response = input("Execute this workflow? [y/N] ")

    if response.lower() != 'y':
        print("Cancelled.")
        sys.exit(0)

    execute_workflow(workflow)


if __name__ == "__main__":
    main()
