#!/usr/bin/env python3
"""
Demo 08: Wave to the Crowd
The robot arm waves to the crowd by moving its base and shoulder.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Wave to the Crowd ===\\n")

WAVE_CYCLES = 3
BASE_SWEEP = 20  # degrees
SHOULDER_SWEEP = 15 # degrees
DELAY = 0.015

print("Waving to the crowd...")

for wave in range(WAVE_CYCLES):
    print(f"  Wave {wave + 1}/{WAVE_CYCLES}")

    # Wave right
    for base_angle in range(63, 63 + BASE_SWEEP, 1):
        set_servo(0, base_angle)
        time.sleep(DELAY)
    for shoulder_angle in range(60, 60 + SHOULDER_SWEEP, 1):
        set_servo(1, shoulder_angle)
        time.sleep(DELAY)

    # Wave left
    for base_angle in range(63 + BASE_SWEEP, 63 - BASE_SWEEP, -1):
        set_servo(0, base_angle)
        time.sleep(DELAY)
    for shoulder_angle in range(60 + SHOULDER_SWEEP, 60 - SHOULDER_SWEEP, -1):
        set_servo(1, shoulder_angle)
        time.sleep(DELAY)

    # Back to center
    for base_angle in range(63 - BASE_SWEEP, 63, 1):
        set_servo(0, base_angle)
        time.sleep(DELAY)
    for shoulder_angle in range(60 - SHOULDER_SWEEP, 60, 1):
        set_servo(1, shoulder_angle)
        time.sleep(DELAY)

    time.sleep(0.2)  # Pause between waves

home()
print("\\n=== Waving complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Wave to the Crowd")
    print("=" * 30)
    run_on_esp32(CODE)