#!/usr/bin/env python3
"""
Semantic Robot Arm Calibrator - Intuitive position descriptions

Instead of "min/max", use descriptive labels:
- Base: "Full Left" / "Center" / "Full Right"
- Shoulder: "Lifted Up" / "Neutral" / "Reaching Down"
- Elbow: "Pulled Back" / "Neutral" / "Extended Forward"
- Gripper: "Closed" / "Neutral" / "Open"
"""

import json
import os
import sys
import subprocess

from flask import Flask, jsonify, render_template, request

script_dir = os.path.dirname(os.path.abspath(__file__))
demos_dir = os.path.join(script_dir, "..", "demos")
sys.path.insert(0, demos_dir)

from utils import find_port

app = Flask(__name__)

# Current servo positions
current_positions = [90, 90, 90, 90]

# Semantic mapping for each servo
# Maps semantic labels to min/max/default
SERVO_SEMANTICS = {
    "base": {
        "labels": ["Full Left", "Center", "Full Right"],
        "mapping": {"Full Left": "min", "Center": "default", "Full Right": "max"},
        "help": "Rotate base all the way left, center, then all the way right"
    },
    "shoulder": {
        "labels": ["Lifted Up", "Neutral", "Reaching Down"],
        "mapping": {"Lifted Up": "min", "Neutral": "default", "Reaching Down": "max"},
        "help": "Lift arm up, find neutral middle position, then reach down toward ground"
    },
    "elbow": {
        "labels": ["Pulled Back", "Neutral", "Extended Forward"],
        "mapping": {"Pulled Back": "min", "Neutral": "default", "Extended Forward": "max"},
        "help": "Pull tip of arm back/away, find neutral, then extend tip forward/down toward ground"
    },
    "gripper": {
        "labels": ["Closed", "Neutral", "Open"],
        "mapping": {"Closed": "min", "Neutral": "default", "Open": "max"},
        "help": "Close gripper fully, find neutral position, then open fully"
    }
}

calibration_data = {
    "base": {"min": 0, "max": 180, "default": 90},
    "shoulder": {"min": 0, "max": 180, "default": 90},
    "elbow": {"min": 0, "max": 180, "default": 90},
    "gripper": {"min": 0, "max": 180, "default": 90},
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
    """Send command to move a single servo"""
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
print("Servo {servo_num} -> {angle}°")
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
    return render_template("calibrator_semantic.html", semantics=SERVO_SEMANTICS)


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


@app.route("/save_semantic", methods=["POST"])
def save_semantic():
    """Save position using semantic label - converts physical angle to logical angle"""
    try:
        data = request.json
        servo_names = ["base", "shoulder", "elbow", "gripper"]
        servo = data.get("servo")  # 0-3
        semantic_label = data.get("label")  # e.g., "Open", "Reaching Down"

        if servo is None or not semantic_label:
            return jsonify({"success": False, "error": "Missing servo or label"})

        servo_name = servo_names[servo]
        semantics = SERVO_SEMANTICS[servo_name]

        # Convert semantic label to min/max/default
        if semantic_label not in semantics["mapping"]:
            return jsonify({"success": False, "error": f"Invalid label: {semantic_label}"})

        limit_type = semantics["mapping"][semantic_label]

        # Get physical angle (what the servo is physically at)
        physical_angle = current_positions[servo]

        # Convert to logical angle if servo is inverted
        # main.py expects LOGICAL angles and applies inversions itself
        if servo_config and servo_config['servos'][servo_name].get('inverted', False):
            logical_angle = 180 - physical_angle
            print(f"Servo {servo_name} is inverted:")
            print(f"  Physical angle: {physical_angle}°")
            print(f"  Logical angle: {logical_angle}° (saved to file)")
        else:
            logical_angle = physical_angle

        calibration_data[servo_name][limit_type] = logical_angle

        print(f"Saved {servo_name}.{limit_type} = {logical_angle}° (label: {semantic_label})")

        return jsonify({
            "success": True,
            "calibration": calibration_data,
            "semantic_label": semantic_label,
            "limit_type": limit_type
        })

    except Exception as e:
        print(f"Error in save_semantic: {e}")
        return jsonify({"success": False, "error": str(e)})


@app.route("/save_calibration", methods=["POST"])
def save_calibration():
    """Save calibration to file"""
    output_file = os.path.join(script_dir, "calibration_limits.json")
    with open(output_file, "w") as f:
        json.dump(calibration_data, f, indent=2)

    print(f"\n✓ Calibration saved to {output_file}")
    print(json.dumps(calibration_data, indent=2))

    return jsonify({"success": True, "file": output_file})


@app.route("/get_data")
def get_data():
    """Get current positions, calibration, and semantics"""
    return jsonify({
        "positions": current_positions,
        "calibration": calibration_data,
        "semantics": SERVO_SEMANTICS
    })


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  🤖 Semantic Robot Arm Calibrator")
    print("=" * 60)
    print("\nIntuitive calibration with descriptive labels:")
    print("  • Gripper: Closed / Neutral / Open")
    print("  • Shoulder: Lifted / Neutral / Reaching Down")
    print("  • Elbow: Pulled Back / Neutral / Extended Forward")
    print("  • Base: Full Left / Center / Full Right")
    print("\n1. Open: http://localhost:3001")
    print("2. Move each servo to the described position")
    print("3. Click the semantic button (e.g., 'Open', 'Reaching Down')")
    print("4. Save calibration when done")
    print("\nPress Ctrl+C to stop\n")

    # Load servo config to know which servos are inverted
    load_servo_config()
    inverted_servos = [name for name, cfg in servo_config['servos'].items() if cfg.get('inverted', False)]
    if inverted_servos:
        print(f"⚠️  Note: {', '.join(inverted_servos)} servo(s) marked as inverted")
        print("   Calibrator will automatically handle this!\n")

    app.run(host="0.0.0.0", port=3001, debug=False)
