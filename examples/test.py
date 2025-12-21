#!/usr/bin/env python3
"""
Quick test - verifies ESP32 connection and servo movement
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
    return ports[0] if ports else None

CODE = '''
from machine import Pin, PWM
import time

print("\\n=== CONNECTION TEST ===\\n")

# Setup servos
PINS = [4, 5, 6, 7]
NAMES = ["Base", "Shoulder", "Elbow", "Gripper"]
servos = []

for i, pin in enumerate(PINS):
    pwm = PWM(Pin(pin), freq=50)
    servos.append(pwm)
    print(f"Servo {NAMES[i]} on GPIO {pin} - OK")

def angle_to_duty(angle):
    return int(26 + (angle / 180) * (128 - 26))

# Move all to 90
print("\\nMoving all servos to 90 degrees...")
for s in servos:
    s.duty(angle_to_duty(90))
time.sleep(1)

# Quick test - wiggle each servo
print("\\nTesting each servo:")
for i, name in enumerate(NAMES):
    print(f"  {name}...", end=" ")
    servos[i].duty(angle_to_duty(70))
    time.sleep(0.3)
    servos[i].duty(angle_to_duty(110))
    time.sleep(0.3)
    servos[i].duty(angle_to_duty(90))
    time.sleep(0.2)
    print("OK")

print("\\n=== TEST COMPLETE ===")
print("If servos moved, everything is working!")
'''

def main():
    print("=== Robot Arm Test ===\n")

    port = find_port()
    if not port:
        print("ERROR: No USB port found!")
        print("Make sure ESP32 is plugged in.")
        sys.exit(1)

    print(f"Found: {port}\n")

    subprocess.run(["mpremote", "connect", port, "exec", CODE])

if __name__ == "__main__":
    main()
