#!/usr/bin/env python3
"""
Demo 08: Pick Up
Reaches forward, grips, and lifts an imaginary object.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Pick Up ===\\n")

STEPS = 100
DELAY = 0.01

# Starting positions
start_base = 63
start_shoulder = 60
start_elbow = 100

# Target positions for reaching forward
target_base = 63
target_shoulder = 30
target_elbow = 140

print("Reaching forward...")
for i in range(STEPS):
    t = i / STEPS
    s = minimum_jerk(t)

    base = start_base + (target_base - start_base) * s
    shoulder = start_shoulder + (target_shoulder - start_shoulder) * s
    elbow = start_elbow + (target_elbow - start_elbow) * s

    set_servo(0, base)
    set_servo(1, shoulder)
    set_servo(2, elbow)
    time.sleep(DELAY)

time.sleep(0.5)

print("Gripping...")
for angle in range(90, 181, 2):
    set_servo(3, angle)
    time.sleep(0.01)

time.sleep(0.5)

# Starting positions for lifting
start_base = target_base
start_shoulder = target_shoulder
start_elbow = target_elbow

# Target positions for lifting
target_base = 63
target_shoulder = 50
target_elbow = 120

print("Lifting...")
for i in range(STEPS):
    t = i / STEPS
    s = minimum_jerk(t)

    base = start_base + (target_base - start_base) * s
    shoulder = start_shoulder + (target_shoulder - start_shoulder) * s
    elbow = start_elbow + (target_elbow - start_elbow) * s

    set_servo(0, base)
    set_servo(1, shoulder)
    set_servo(2, elbow)
    time.sleep(DELAY)

time.sleep(0.5)

home()
print("\\n=== Pick Up complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Pick Up")
    print("=" * 30)
    run_on_esp32(CODE)