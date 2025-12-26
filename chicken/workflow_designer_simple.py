#!/usr/bin/env python3
"""
Simple Workflow Designer - Clone of calibrator but saves positions as steps

Usage:
    python workflow_designer_simple.py
    Open http://localhost:3002
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

# Current workflow
current_workflow = {
    "name": "Untitled Workflow",
    "description": "",
    "steps": []
}

PORT = None


def send_single_servo_command(servo_num, angle):
    """Send command to move a single servo ONLY"""
    global PORT
    if PORT is None:
        PORT = find_port()
        if not PORT:
            return False

    pin_num = servo_num + 4

    code = f"""
from machine import Pin, PWM

pin = {pin_num}
pwm = PWM(Pin(pin), freq=50)

def angle_to_duty(angle):
    return int(round(26 + (angle / 180) * (128 - 26)))

duty = angle_to_duty({angle})
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
    return render_template("workflow_designer_simple.html")


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
    """Add current position as a step"""
    try:
        data = request.json
        step_name = data.get("name", f"Step {len(current_workflow['steps']) + 1}")
        duration = data.get("duration", 2.0)

        step = {
            "name": step_name,
            "position": current_positions.copy(),
            "duration": duration
        }

        current_workflow["steps"].append(step)

        print(f"Added step: {step_name}")
        print(f"  Position: {current_positions}")
        print(f"  Duration: {duration}s")

        return jsonify({
            "success": True,
            "workflow": current_workflow
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "error": str(e)})


@app.route("/remove_step", methods=["POST"])
def remove_step():
    """Remove a step"""
    try:
        data = request.json
        index = data.get("index")

        if index is not None and 0 <= index < len(current_workflow["steps"]):
            removed = current_workflow["steps"].pop(index)
            return jsonify({"success": True, "workflow": current_workflow})

        return jsonify({"success": False, "error": "Invalid index"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/goto_step", methods=["POST"])
def goto_step():
    """Move servos to a step's position"""
    try:
        data = request.json
        index = data.get("index")

        if index is not None and 0 <= index < len(current_workflow["steps"]):
            step = current_workflow["steps"][index]
            target = step["position"]

            for i in range(4):
                current_positions[i] = target[i]
                send_single_servo_command(i, target[i])

            return jsonify({
                "success": True,
                "positions": current_positions
            })

        return jsonify({"success": False})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/update_meta", methods=["POST"])
def update_meta():
    """Update workflow name/description"""
    data = request.json
    if "name" in data:
        current_workflow["name"] = data["name"]
    if "description" in data:
        current_workflow["description"] = data["description"]
    return jsonify({"success": True, "workflow": current_workflow})


@app.route("/save_workflow", methods=["POST"])
def save_workflow():
    """Save workflow to JSON"""
    try:
        current_workflow["created"] = datetime.now().isoformat()

        filename = current_workflow["name"].lower().replace(" ", "_")
        filename = "".join(c for c in filename if c.isalnum() or c == "_")
        filename = f"{filename}.json"

        os.makedirs(os.path.join(script_dir, "workflows"), exist_ok=True)
        output_file = os.path.join(script_dir, "workflows", filename)

        with open(output_file, "w") as f:
            json.dump(current_workflow, f, indent=2)

        print(f"\n✓ Saved: {output_file}")

        return jsonify({"success": True, "file": output_file, "filename": filename})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/new_workflow", methods=["POST"])
def new_workflow():
    """Start new workflow"""
    current_workflow["name"] = "Untitled Workflow"
    current_workflow["description"] = ""
    current_workflow["steps"] = []
    return jsonify({"success": True, "workflow": current_workflow})


@app.route("/load_workflow", methods=["POST"])
def load_workflow():
    """Load workflow from file"""
    try:
        data = request.json
        filename = data.get("filename")

        filepath = os.path.join(script_dir, "workflows", filename)
        if not os.path.exists(filepath):
            return jsonify({"success": False, "error": "File not found"})

        with open(filepath, "r") as f:
            loaded = json.load(f)

        current_workflow.clear()
        current_workflow.update(loaded)

        return jsonify({"success": True, "workflow": current_workflow})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/list_workflows")
def list_workflows():
    """List saved workflows"""
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
                    wf = json.load(f)
                    workflows.append({
                        "filename": filename,
                        "name": wf.get("name", "Untitled"),
                        "steps": len(wf.get("steps", []))
                    })
            except:
                pass

        return jsonify({"success": True, "workflows": workflows})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/get_data")
def get_data():
    """Get current state"""
    return jsonify({
        "positions": current_positions,
        "workflow": current_workflow
    })


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  🎬 Simple Workflow Designer")
    print("=" * 60)
    print("\nJust like the calibrator but saves workflow steps:")
    print("  1. Move servos to desired position")
    print("  2. Click 'Add Step'")
    print("  3. Repeat to build sequence")
    print("  4. Save workflow")
    print("\nThen run: python chicken_simple.py workflow.json")
    print("\n→ Open: http://localhost:3002")
    print("\nPress Ctrl+C to stop\n")

    app.run(host="0.0.0.0", port=3002, debug=False)
