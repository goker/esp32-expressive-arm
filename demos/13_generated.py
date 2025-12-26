#!/usr/bin/env python3
"""
Demo 08: To The Crowd
Moves the base servo back and forth in a sweeping motion.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: To The Crowd ===\\n")

DELAY = 0.01
SWEEP_RANGE = 45
CENTER_ANGLE = 63
SWEEPS = 3

print("Sweeping motion...")
for sweep in range(SWEEPS):
    print(f"Sweep {sweep + 1}/{SWEEPS}")

    # Sweep right
    for angle in range(CENTER_ANGLE, CENTER_ANGLE + SWEEP_RANGE, 1):
        set_servo(0, angle)
        time.sleep(DELAY)

    # Sweep left
    for angle in range(CENTER_ANGLE + SWEEP_RANGE, CENTER_ANGLE - SWEEP_RANGE, -1):
        set_servo(0, angle)
        time.sleep(DELAY)

    # Return to center
    for angle in range(CENTER_ANGLE - SWEEP_RANGE, CENTER_ANGLE, 1):
        set_servo(0, angle)
        time.sleep(DELAY)

home()
print("\\n=== To the crowd complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: To The Crowd")
    print("=" * 30)
    run_on_esp32(CODE)