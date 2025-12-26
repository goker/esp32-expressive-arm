#!/usr/bin/env python3
"""
Simple Chicken - Executes workflows created by workflow_designer_simple.py

Just sends the exact angles saved in the workflow. No inversion logic.

Usage:
    python chicken_simple.py workflow.json
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
            print(f"Error: File not found: {filepath}")
            sys.exit(1)

    with open(filepath, 'r') as f:
        return json.load(f)


def execute_workflow(workflow):
    """Execute workflow on robot - NO INVERSIONS, just send exact angles"""
    print("\n" + "=" * 60)
    print(f"  🤖 Executing: {workflow['name']}")
    print("=" * 60)

    if workflow.get('description'):
        print(f"\n{workflow['description']}\n")

    print(f"Steps: {len(workflow['steps'])}")
    print()

    # Find port
    port = find_port()
    if not port:
        print("ERROR: No USB port found!")
        sys.exit(1)

    print(f"Connected to: {port}\n")

    # Show steps - NO CONVERSION, just show what we'll send
    for i, step in enumerate(workflow['steps']):
        print(f"  {i+1}. {step['name']}: {step['position']} ({step['duration']}s)")

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
        smooth = 10 * (progress ** 3) - 15 * (progress ** 4) + 6 * (progress ** 5)

        for i in range(4):
            angle = start[i] + (target[i] - start[i]) * smooth
            set_servo(i, int(angle))

        time.sleep(0.05)

# HARDCODED: Move to neutral position first
print("\\nMoving to neutral position...")
neutral = [90, 90, 90, 90]
for i in range(4):
    set_servo(i, neutral[i])
time.sleep(1.0)

print("\\nStarting workflow...")
"""

    # Add steps - EXACT angles from workflow, NO CONVERSION
    for i, step in enumerate(workflow['steps']):
        micropython_code += f"""
print("\\n[{i+1}/{len(workflow['steps'])}] {step['name']}")
move_to_position({step['position']}, {step['duration']})
time.sleep(0.3)
"""

    micropython_code += """
print("\\n✓ Complete!")
"""

    # Execute
    print("Executing on robot...")
    print("-" * 60)

    result = subprocess.run(
        ["mpremote", "connect", port, "exec", micropython_code],
        capture_output=False
    )

    print("-" * 60)

    if result.returncode != 0:
        print("\nError executing workflow!")
        sys.exit(1)

    print("\n✓ Workflow complete!")


def list_workflows():
    """List available workflows"""
    workflows_dir = os.path.join(script_dir, "workflows")

    if not os.path.exists(workflows_dir):
        print("No workflows directory found.")
        return

    files = [f for f in os.listdir(workflows_dir) if f.endswith(".json")]

    if not files:
        print("No workflows found.")
        return

    print("\nAvailable workflows:")
    print("-" * 60)

    for filename in sorted(files):
        filepath = os.path.join(workflows_dir, filename)
        try:
            with open(filepath, 'r') as f:
                wf = json.load(f)
                print(f"\n  {filename}")
                print(f"  Name: {wf.get('name', 'Untitled')}")
                print(f"  Steps: {len(wf.get('steps', []))}")
        except:
            print(f"\n  {filename} (error)")

    print("\n" + "-" * 60)


def main():
    print("\n" + "=" * 60)
    print("  🐔 Simple Chicken - Workflow Executor")
    print("=" * 60)

    if len(sys.argv) < 2:
        print("\nUsage: python chicken_simple.py <workflow.json>")
        print("\nExamples:")
        print("  python chicken_simple.py my_workflow.json")
        print("  python chicken_simple.py workflows/pickup.json")
        print("\nList workflows:")
        print("  python chicken_simple.py --list")
        sys.exit(1)

    if sys.argv[1] in ["--list", "-l"]:
        list_workflows()
        sys.exit(0)

    workflow_file = sys.argv[1]
    workflow = load_workflow(workflow_file)

    print(f"\nLoaded: {workflow['name']}")
    print(f"Steps: {len(workflow['steps'])}")

    for i, step in enumerate(workflow['steps']):
        print(f"  {i+1}. {step['name']} ({step['duration']}s)")

    print()
    response = input("Execute? [y/N] ")

    if response.lower() != 'y':
        print("Cancelled.")
        sys.exit(0)

    execute_workflow(workflow)


if __name__ == "__main__":
    main()
