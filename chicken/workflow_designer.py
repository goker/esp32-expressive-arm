#!/usr/bin/env python3
"""
Workflow Designer - Create multi-step robot arm sequences

Design workflows by:
1. Moving servos to desired positions
2. Clicking "Add Step" to save that position
3. Building up a sequence of steps
4. Saving the complete workflow to JSON

Then run with: python chicken.py workflow_name.json
"""

import json
import os
import sys
import subprocess
from datetime import datetime

from flask import Flask, jsonify, render_template, request

script_dir = os.path.dirname(os.path.abspath(__file__))
demos_dir = os.path.join(script_dir, "..", "demos")
sys.path.insert(0, demos_dir)

from utils import find_port

app = Flask(__name__)

# Current servo positions
current_positions = [90, 90, 90, 90]

# Current workflow being designed
current_workflow = {
    "name": "Untitled Workflow",
    "description": "",
    "created": "",
    "steps": []
}

servo_config = None
PORT = None


def load_servo_config():
    """Load servo configuration with inversion settings"""
    global servo_config
    config_path = os.path.join(script_dir, "servo_config.json")
    try:
        with open(config_path, 'r') as f:
            servo_config = json.load(f)
    except:
        # Default: no inversions
        servo_config = {
            "servos": {
                "base": {"pin": 0, "inverted": False},
                "shoulder": {"pin": 1, "inverted": False},
                "elbow": {"pin": 2, "inverted": False},
                "gripper": {"pin": 3, "inverted": False}
            }
        }


def send_single_servo_command(servo_num, angle):
    """Send command to move a single servo - handles inversions"""
    global PORT
    if PORT is None:
        PORT = find_port()
        if not PORT:
            return False

    # Apply inversion if needed (convert logical angle to physical angle)
    servo_names = ["base", "shoulder", "elbow", "gripper"]
    servo_name = servo_names[servo_num]

    if servo_config and servo_config['servos'][servo_name].get('inverted', False):
        physical_angle = 180 - angle
        # Don't print for every move, only on request
    else:
        physical_angle = angle

    pin_num = servo_num + 4

    code = f"""
from machine import Pin, PWM

pin = {pin_num}
pwm = PWM(Pin(pin), freq=50)

def angle_to_duty(angle):
    return int(round(26 + (angle / 180) * (128 - 26)))

duty = angle_to_duty({physical_angle})
pwm.duty(duty)
"""

    try:
        result = subprocess.run(
            ["mpremote", "connect", PORT, "exec", code],
            capture_output=True,
            timeout=5,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error: {e}")
        return False


@app.route("/")
def index():
    return render_template("workflow_designer.html")


@app.route("/move", methods=["POST"])
def move():
    """Update servo position"""
    data = request.json
    servo = data.get("servo")
    angle = data.get("angle")

    if servo is not None and angle is not None:
        current_positions[servo] = angle
        success = send_single_servo_command(servo, angle)
        return jsonify({"success": success, "positions": current_positions})

    return jsonify({"success": False})


@app.route("/add_step", methods=["POST"])
def add_step():
    """Add current position as a step in the workflow"""
    try:
        data = request.json
        step_name = data.get("name", f"Step {len(current_workflow['steps']) + 1}")
        duration = data.get("duration", 2.0)

        step = {
            "name": step_name,
            "position": current_positions.copy(),
            "duration": duration,
            "description": data.get("description", "")
        }

        current_workflow["steps"].append(step)

        print(f"Added step: {step_name}")
        print(f"  Position: {current_positions}")
        print(f"  Duration: {duration}s")

        return jsonify({
            "success": True,
            "workflow": current_workflow,
            "step_index": len(current_workflow["steps"]) - 1
        })

    except Exception as e:
        print(f"Error adding step: {e}")
        return jsonify({"success": False, "error": str(e)})


@app.route("/remove_step", methods=["POST"])
def remove_step():
    """Remove a step from the workflow"""
    try:
        data = request.json
        index = data.get("index")

        if index is not None and 0 <= index < len(current_workflow["steps"]):
            removed = current_workflow["steps"].pop(index)
            print(f"Removed step {index}: {removed['name']}")

            return jsonify({
                "success": True,
                "workflow": current_workflow
            })

        return jsonify({"success": False, "error": "Invalid step index"})

    except Exception as e:
        print(f"Error removing step: {e}")
        return jsonify({"success": False, "error": str(e)})


@app.route("/goto_step", methods=["POST"])
def goto_step():
    """Move servos to a specific step's position"""
    try:
        data = request.json
        index = data.get("index")

        if index is not None and 0 <= index < len(current_workflow["steps"]):
            step = current_workflow["steps"][index]
            target_positions = step["position"]

            # Move all servos to step position
            for i, angle in enumerate(target_positions):
                current_positions[i] = angle
                send_single_servo_command(i, angle)

            print(f"Moved to step {index}: {step['name']}")

            return jsonify({
                "success": True,
                "positions": current_positions,
                "step": step
            })

        return jsonify({"success": False, "error": "Invalid step index"})

    except Exception as e:
        print(f"Error going to step: {e}")
        return jsonify({"success": False, "error": str(e)})


@app.route("/update_workflow_meta", methods=["POST"])
def update_workflow_meta():
    """Update workflow name and description"""
    try:
        data = request.json
        if "name" in data:
            current_workflow["name"] = data["name"]
        if "description" in data:
            current_workflow["description"] = data["description"]

        return jsonify({"success": True, "workflow": current_workflow})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/save_workflow", methods=["POST"])
def save_workflow():
    """Save workflow to JSON file"""
    try:
        current_workflow["created"] = datetime.now().isoformat()

        # Generate filename from workflow name
        filename = current_workflow["name"].lower().replace(" ", "_")
        filename = "".join(c for c in filename if c.isalnum() or c == "_")
        filename = f"{filename}.json"

        output_file = os.path.join(script_dir, "workflows", filename)

        # Create workflows directory if needed
        os.makedirs(os.path.join(script_dir, "workflows"), exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(current_workflow, f, indent=2)

        print(f"\n✓ Workflow saved to {output_file}")
        print(json.dumps(current_workflow, indent=2))

        return jsonify({
            "success": True,
            "file": output_file,
            "filename": filename
        })

    except Exception as e:
        print(f"Error saving workflow: {e}")
        return jsonify({"success": False, "error": str(e)})


@app.route("/load_workflow", methods=["POST"])
def load_workflow():
    """Load a workflow from JSON file"""
    try:
        data = request.json
        filename = data.get("filename")

        if not filename:
            return jsonify({"success": False, "error": "No filename provided"})

        filepath = os.path.join(script_dir, "workflows", filename)

        if not os.path.exists(filepath):
            return jsonify({"success": False, "error": "File not found"})

        with open(filepath, "r") as f:
            loaded_workflow = json.load(f)

        current_workflow.clear()
        current_workflow.update(loaded_workflow)

        print(f"Loaded workflow: {current_workflow['name']}")
        print(f"  Steps: {len(current_workflow['steps'])}")

        return jsonify({
            "success": True,
            "workflow": current_workflow
        })

    except Exception as e:
        print(f"Error loading workflow: {e}")
        return jsonify({"success": False, "error": str(e)})


@app.route("/list_workflows")
def list_workflows():
    """List all saved workflows"""
    try:
        workflows_dir = os.path.join(script_dir, "workflows")
        if not os.path.exists(workflows_dir):
            return jsonify({"success": True, "workflows": []})

        files = [f for f in os.listdir(workflows_dir) if f.endswith(".json")]

        workflows = []
        for filename in files:
            filepath = os.path.join(workflows_dir, filename)
            try:
                with open(filepath, "r") as f:
                    workflow = json.load(f)
                    workflows.append({
                        "filename": filename,
                        "name": workflow.get("name", "Untitled"),
                        "steps": len(workflow.get("steps", [])),
                        "description": workflow.get("description", "")
                    })
            except:
                pass

        return jsonify({"success": True, "workflows": workflows})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/get_data")
def get_data():
    """Get current positions and workflow"""
    return jsonify({
        "positions": current_positions,
        "workflow": current_workflow
    })


@app.route("/new_workflow", methods=["POST"])
def new_workflow():
    """Start a new workflow"""
    current_workflow["name"] = "Untitled Workflow"
    current_workflow["description"] = ""
    current_workflow["created"] = ""
    current_workflow["steps"] = []

    return jsonify({"success": True, "workflow": current_workflow})


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  🎬 Robot Arm Workflow Designer")
    print("=" * 60)
    print("\nDesign multi-step sequences:")
    print("  1. Move servos to desired position")
    print("  2. Click 'Add Step' to save position")
    print("  3. Repeat to build sequence")
    print("  4. Save workflow to JSON")
    print("\nThen run with: python chicken.py workflow_name.json")
    print("\n→ Open: http://localhost:3002")
    print("\nPress Ctrl+C to stop\n")

    # Load servo config to handle inversions
    load_servo_config()
    inverted_servos = [name for name, cfg in servo_config['servos'].items() if cfg.get('inverted', False)]
    if inverted_servos:
        print(f"⚠️  Note: {', '.join(inverted_servos)} servo(s) marked as inverted")
        print("   Designer will automatically handle this!\n")

    app.run(host="0.0.0.0", port=3002, debug=False)
