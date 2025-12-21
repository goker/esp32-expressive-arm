"""
Shared utilities for robot arm demos
"""

import subprocess
import sys
import glob

def find_port():
    """Auto-discover ESP32 serial port"""
    patterns = [
        '/dev/cu.usbserial-*',
        '/dev/cu.wchusbserial*',
        '/dev/cu.SLAB_USBtoUART*',
        '/dev/ttyUSB*',
        '/dev/ttyACM*',
    ]
    ports = []
    for pattern in patterns:
        ports.extend(glob.glob(pattern))

    if not ports:
        return None
    if len(ports) == 1:
        return ports[0]

    print("Multiple ports found:")
    for i, p in enumerate(ports):
        print(f"  {i+1}. {p}")
    choice = input("Enter number (or press Enter for first): ").strip()
    if choice == "":
        return ports[0]
    try:
        return ports[int(choice) - 1]
    except:
        return ports[0]

def run_on_esp32(micropython_code, port=None):
    """Send MicroPython code to ESP32 and run it"""
    if port is None:
        port = find_port()

    if port is None:
        print("ERROR: No USB serial port found!")
        print("\nMake sure:")
        print("  1. ESP32-C3 is plugged in via USB")
        print("  2. USB cable supports data (not charge-only)")
        sys.exit(1)

    print(f"Connected to: {port}\n")

    result = subprocess.run(
        ["mpremote", "connect", port, "exec", micropython_code],
        capture_output=False
    )

    if result.returncode != 0:
        print("\nError! Try:")
        print("  1. Close any program using the port")
        print("  2. Press RESET on ESP32")
        print("  3. Run: bash setup.sh")
        sys.exit(1)

# Shared MicroPython code header for servo control
SERVO_HEADER = '''
from machine import Pin, PWM
import time
import math

# Servo pins: Base=4, Shoulder=5, Elbow=6, Gripper=7
SERVO_PINS = [4, 5, 6, 7]
SERVO_NAMES = ["Base", "Shoulder", "Elbow", "Gripper"]

# State
current_pos = [90, 90, 90, 90]
smooth_pos = [90.0, 90.0, 90.0, 90.0]
last_duty = [0, 0, 0, 0]
SMOOTHING = 0.5

# Initialize servos
servos = []
for pin in SERVO_PINS:
    pwm = PWM(Pin(pin), freq=50)
    servos.append(pwm)

def angle_to_duty(angle):
    """Convert angle (0-180) to duty cycle"""
    return int(round(26 + (angle / 180) * (128 - 26)))

def set_servo(servo_num, target):
    """Set servo with smoothing and jitter reduction"""
    global smooth_pos, last_duty
    smooth_pos[servo_num] = smooth_pos[servo_num] * (1 - SMOOTHING) + target * SMOOTHING
    duty = angle_to_duty(smooth_pos[servo_num])
    if duty != last_duty[servo_num]:
        servos[servo_num].duty(duty)
        last_duty[servo_num] = duty
    current_pos[servo_num] = int(smooth_pos[servo_num])

def set_servo_direct(servo_num, angle):
    """Set servo directly without smoothing"""
    duty = angle_to_duty(angle)
    servos[servo_num].duty(duty)
    current_pos[servo_num] = angle
    smooth_pos[servo_num] = float(angle)

def minimum_jerk(t):
    """Minimum jerk trajectory: smooth human-like motion"""
    return 10 * (t ** 3) - 15 * (t ** 4) + 6 * (t ** 5)

def home():
    """Move all servos to home position"""
    for i in range(4):
        set_servo_direct(i, 90)
    time.sleep(0.5)

# Initialize to home
home()
print("Servos initialized")
'''
