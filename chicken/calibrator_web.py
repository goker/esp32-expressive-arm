#!/usr/bin/env python3
"""
Web-based robot arm calibrator
Launch this, open browser to http://localhost:3001
"""

import json
import os
import sys

from flask import Flask, jsonify, render_template, request

script_dir = os.path.dirname(os.path.abspath(__file__))
demos_dir = os.path.join(script_dir, "..", "demos")
sys.path.insert(0, demos_dir)

import subprocess

from utils import find_port

app = Flask(__name__)

# Current servo positions
current_positions = [90, 90, 90, 90]
calibration_data = {
    "base": {"min": 0, "max": 180, "default": 90},
    "shoulder": {"min": 0, "max": 180, "default": 90},
    "elbow": {"min": 0, "max": 180, "default": 90},
    "gripper": {"min": 0, "max": 180, "default": 90},
}

PORT = None


def send_single_servo_command(servo_num, angle):
    """Send command to move a single servo ONLY (completely isolated)"""
    global PORT
    if PORT is None:
        PORT = find_port()
        if not PORT:
            print(f"No port found for servo {servo_num}")
            return False

    # Calculate the actual GPIO pin
    pin_num = servo_num + 4

    code = f"""
from machine import Pin, PWM

# Only initialize THIS servo, don't touch others
pin = {pin_num}
pwm = PWM(Pin(pin), freq=50)

def angle_to_duty(angle):
    return int(round(26 + (angle / 180) * (128 - 26)))

# Set only this servo
duty = angle_to_duty({angle})
pwm.duty(duty)
print("Servo {servo_num} (GPIO {pin_num}) -> {angle}°")
"""

    try:
        print(f"Moving servo {servo_num} (GPIO {pin_num}) to {angle}°")
        result = subprocess.run(
            ["mpremote", "connect", PORT, "exec", code],
            capture_output=True,
            timeout=5,
            text=True
        )
        if result.returncode != 0:
            print(f"Error moving servo: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Exception moving servo: {e}")
        return False


def send_servo_command(positions):
    """Send servo positions to ESP32"""
    global PORT
    if PORT is None:
        PORT = find_port()
        if not PORT:
            return False

    code = f"""
from machine import Pin, PWM
import time

SERVO_PINS = [4, 5, 6, 7]
servos = []
for pin in SERVO_PINS:
    pwm = PWM(Pin(pin), freq=50)
    servos.append(pwm)

def angle_to_duty(angle):
    return int(round(26 + (angle / 180) * (128 - 26)))

positions = {positions}
for i in range(4):
    duty = angle_to_duty(positions[i])
    servos[i].duty(duty)

print("Servos set to:", positions)
"""

    try:
        result = subprocess.run(
            ["mpremote", "connect", PORT, "exec", code], capture_output=True, timeout=5
        )
        return result.returncode == 0
    except:
        return False


@app.route("/")
def index():
    return render_template("calibrator.html")


@app.route("/move", methods=["POST"])
def move():
    """Update servo positions - only moves the single servo that changed"""
    data = request.json
    servo = data.get("servo")  # 0-3
    angle = data.get("angle")  # 0-180

    if servo is not None and angle is not None:
        current_positions[servo] = angle
        success = send_single_servo_command(servo, angle)
        return jsonify({"success": success, "positions": current_positions})

    return jsonify({"success": False})


@app.route("/move_all", methods=["POST"])
def move_all():
    """Move all servos at once"""
    data = request.json
    positions = data.get("positions")

    if positions and len(positions) == 4:
        current_positions[:] = positions
        success = send_servo_command(current_positions)
        return jsonify({"success": success, "positions": current_positions})

    return jsonify({"success": False})


@app.route("/save_limit", methods=["POST"])
def save_limit():
    """Save min/max/default limit for a servo"""
    try:
        data = request.json
        servo_names = ["base", "shoulder", "elbow", "gripper"]
        servo = data.get("servo")  # 0-3
        limit_type = data.get("type")  # 'min', 'max', or 'default'

        print(f"Received save_limit request: servo={servo}, type={limit_type}, current_pos={current_positions[servo] if servo is not None else 'N/A'}")

        if servo is None:
            return jsonify({"success": False, "error": "No servo specified"})

        if limit_type not in ["min", "max", "default"]:
            return jsonify({"success": False, "error": f"Invalid limit type: {limit_type}"})

        servo_name = servo_names[servo]
        calibration_data[servo_name][limit_type] = current_positions[servo]

        print(f"Updated calibration_data: {calibration_data[servo_name]}")

        return jsonify({"success": True, "calibration": calibration_data})

    except Exception as e:
        print(f"Error in save_limit: {e}")
        return jsonify({"success": False, "error": str(e)})


@app.route("/save_calibration", methods=["POST"])
def save_calibration():
    """Save calibration to file"""
    output_file = os.path.join(script_dir, "calibration_limits.json")
    with open(output_file, "w") as f:
        json.dump(calibration_data, f, indent=2)

    return jsonify({"success": True, "file": output_file})


@app.route("/get_positions")
def get_positions():
    """Get current positions"""
    return jsonify({"positions": current_positions, "calibration": calibration_data})


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  Robot Arm Web Calibrator")
    print("=" * 60)
    print("\n1. Open your browser to: http://localhost:3001")
    print("2. Use sliders to move servos")
    print("3. Click 'Save Min' / 'Save Max' at limits")
    print("4. Click 'Save Calibration' when done")
    print("\nPress Ctrl+C to stop\n")

    app.run(host="0.0.0.0", port=3001, debug=False)
