#!/usr/bin/env python3
"""
Demo 08: Wave to Crowd
The robot arm waves to simulate greeting a crowd.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Wave to Crowd ===\\n")

WAVE_CYCLES = 3
WAVE_STEPS = 50
WAVE_DELAY = 0.015

print(f"Waving {WAVE_CYCLES} times...")
for wave in range(WAVE_CYCLES):
    print(f"  Wave {wave + 1}/{WAVE_CYCLES}")

    # Wave Out
    for i in range(WAVE_STEPS):
        t = i / WAVE_STEPS
        s = minimum_jerk(t)
        base_angle = 63 + 30 * s
        shoulder_angle = 60 + 20 * s
        set_servo(0, base_angle)
        set_servo(1, shoulder_angle)
        time.sleep(WAVE_DELAY)

    time.sleep(0.2)

    # Wave In
    for i in range(WAVE_STEPS):
        t = i / WAVE_STEPS
        s = minimum_jerk(t)
        base_angle = (63 + 30) - 30 * s
        shoulder_angle = (60 + 20) - 20 * s
        set_servo(0, base_angle)
        set_servo(1, shoulder_angle)
        time.sleep(WAVE_DELAY)

    time.sleep(0.3)

home()
print("\\n=== Wave complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Wave to Crowd")
    print("=" * 30)
    run_on_esp32(CODE)