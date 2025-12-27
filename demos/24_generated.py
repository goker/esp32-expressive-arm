#!/usr/bin/env python3
"""
Demo 08: Gentle Bow
The robot arm performs a slow, gentle bowing motion
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Gentle Bow ===\\n")

STEPS = 100
DELAY = 0.02

start_shoulder = 60
start_elbow = 100

# Bow down
print("Bowing...")
for i in range(STEPS):
    t = i / STEPS
    s = minimum_jerk(t)
    shoulder = start_shoulder + (80 - start_shoulder) * s
    elbow = start_elbow + (80 - start_elbow) * s
    set_servo(1, shoulder)
    set_servo(2, elbow)
    time.sleep(DELAY)

time.sleep(0.5)

# Return to upright
print("Returning...")
for i in range(STEPS):
    t = i / STEPS
    s = minimum_jerk(t)
    shoulder = 80 + (start_shoulder - 80) * s
    elbow = 80 + (start_elbow - 80) * s
    set_servo(1, shoulder)
    set_servo(2, elbow)
    time.sleep(DELAY)

home()
print("\\n=== Bow complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Gentle Bow")
    print("=" * 30)
    run_on_esp32(CODE)