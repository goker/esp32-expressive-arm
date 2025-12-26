#!/usr/bin/env python3
"""
Demo 08: Base Wave
Smoothly rotates the base back and forth in a waving motion.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Base Wave ===\\n")

CENTER_BASE = 63
AMPLITUDE = 40
STEPS = 100
DELAY = 0.01
CYCLES = 3

print(f"Waving base {CYCLES} times...")
for cycle in range(CYCLES):
    print(f"Cycle {cycle + 1}/{CYCLES}")

    # Wave to the right
    for i in range(STEPS):
        t = i / STEPS
        s = minimum_jerk(t)
        angle = CENTER_BASE + AMPLITUDE * s
        set_servo(0, angle)
        time.sleep(DELAY)

    # Wave to the left
    for i in range(STEPS):
        t = i / STEPS
        s = minimum_jerk(t)
        angle = CENTER_BASE + AMPLITUDE - AMPLITUDE * s
        set_servo(0, angle)
        time.sleep(DELAY)

    # Wave back to center
    for i in range(STEPS):
        t = i / STEPS
        s = minimum_jerk(t)
        angle = CENTER_BASE + (AMPLITUDE * s)
        set_servo(0, CENTER_BASE + AMPLITUDE - (AMPLITUDE * s))
        time.sleep(DELAY)

home()
print("\\n=== Base wave complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Base Wave")
    print("=" * 30)
    run_on_esp32(CODE)