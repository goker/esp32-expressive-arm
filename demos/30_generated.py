#!/usr/bin/env python3
"""
Demo 08: Bow
Simulates a bowing motion.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Bow ===\\n")

STEPS = 50
DELAY = 0.02

# Initial positions
start_shoulder = 60
start_elbow = 100

# Target positions for bowing
bow_shoulder = 80
bow_elbow = 70

print("Bowing...")
for i in range(STEPS):
    t = i / STEPS
    s = minimum_jerk(t)

    shoulder = start_shoulder + (bow_shoulder - start_shoulder) * s
    elbow = start_elbow + (bow_elbow - start_elbow) * s

    set_servo(1, shoulder)
    set_servo(2, elbow)
    time.sleep(DELAY)

time.sleep(0.5)

print("Returning to upright position...")
for i in range(STEPS):
    t = i / STEPS
    s = minimum_jerk(t)

    shoulder = bow_shoulder + (start_shoulder - bow_shoulder) * s
    elbow = bow_elbow + (start_elbow - bow_elbow) * s

    set_servo(1, shoulder)
    set_servo(2, elbow)
    time.sleep(DELAY)

home()
print("\\n=== Bow complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Bow")
    print("=" * 30)
    run_on_esp32(CODE)