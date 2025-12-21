"""
Servo utilities - loads calibration config and provides angle mapping
"""

import json
import os

# ============================================
# GLOBAL SPEED CONTROL
# ============================================
# Adjust this number to control ALL movement speeds
# Higher = SLOWER (more steps, longer delays)
# Lower = FASTER (fewer steps, shorter delays)
#
# Examples:
#   1.0 = normal speed
#   2.0 = twice as slow (recommended for precision)
#   3.0 = three times as slow (ultra smooth)
#   0.5 = twice as fast
# ============================================
SPEED_MULTIPLIER = 0.5


def load_config():
    """Load servo calibration config"""
    config_path = os.path.join(os.path.dirname(__file__), "servo_config.json")

    if not os.path.exists(config_path):
        print("WARNING: No calibration found. Run __calibrator.py first!")
        print("Using default (non-inverted) settings...")
        return {
            "servos": {
                "base": {"pin": 0, "inverted": False},
                "shoulder": {"pin": 1, "inverted": False},
                "elbow": {"pin": 2, "inverted": False},
                "gripper": {"pin": 3, "inverted": False},
            }
        }

    with open(config_path, "r") as f:
        return json.load(f)


def get_calibrated_angles():
    """
    Returns a code snippet that defines calibrated angle mapping function
    This gets injected into the MicroPython code
    """
    config = load_config()

    # Build inversion map as Python list
    inversions = [
        config["servos"]["base"]["inverted"],
        config["servos"]["shoulder"]["inverted"],
        config["servos"]["elbow"]["inverted"],
        config["servos"]["gripper"]["inverted"],
    ]

    code = f'''
# Servo calibration data
SERVO_INVERTED = {inversions}

# Global speed multiplier
SPEED_MULTIPLIER = {SPEED_MULTIPLIER}

def calibrated_angle(servo_num, target_angle):
    """Apply calibration to convert logical angle to physical angle"""
    if SERVO_INVERTED[servo_num]:
        # Invert: 0->180, 180->0, 90->90
        return 180 - target_angle
    return target_angle
'''
    return code
