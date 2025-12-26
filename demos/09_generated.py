#!/usr/bin/env python3
"""
Demo 08: Wave to Crowd
Simulates a waving motion using the shoulder and elbow joints.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Wave to Crowd ===\\n")

# Wave parameters
WAVE_CYCLES = 3
WAVE_STEPS = 50
SHOULDER_MIN = 50
SHOULDER_MAX = 70
ELBOW_MIN = 90
ELBOW_MAX = 110
DELAY = 0.015

print("Waving to the crowd...")
for cycle in range(WAVE_CYCLES):
    print(f"  Wave {cycle + 1}/{WAVE_CYCLES}")
    for i in range(WAVE_STEPS):
        t = i / WAVE_STEPS
        s = minimum_jerk(t)

        # Shoulder motion
        shoulder_angle = SHOULDER_MIN + (SHOULDER_MAX - SHOULDER_MIN) * s
        set_servo(1, shoulder_angle)

        # Elbow motion (opposite phase for waving)
        elbow_angle = ELBOW_MAX - (ELBOW_MAX - ELBOW_MIN) * s
        set_servo(2, elbow_angle)

        time.sleep(DELAY)

# Small pause between waves
    time.sleep(0.3)

home()
print("\\n=== Wave complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Wave to Crowd")
    print("=" * 30)
    run_on_esp32(CODE)