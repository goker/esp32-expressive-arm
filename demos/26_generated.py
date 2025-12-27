#!/usr/bin/env python3
"""
Demo 08: Bow
Simulates a bowing motion to the crowd.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Bow ===\\n")

STEPS = 70
DELAY = 0.01

# Initial position (standing straight)
start_shoulder = 60
start_elbow = 100

# Target position (bowed)
target_shoulder = 80  # Move shoulder up
target_elbow = 50   # Move elbow back

print("Bowing...")
for i in range(STEPS):
    t = i / STEPS
    s = minimum_jerk(t)

    shoulder = start_shoulder + (target_shoulder - start_shoulder) * s
    elbow = start_elbow + (target_elbow - start_elbow) * s

    set_servo(1, shoulder)
    set_servo(2, elbow)
    time.sleep(DELAY)

time.sleep(0.5)

# Return to upright position
print("Returning to upright...")
for i in range(STEPS):
    t = i / STEPS
    s = minimum_jerk(t)

    shoulder = target_shoulder + (start_shoulder - target_shoulder) * s
    elbow = target_elbow + (start_elbow - target_elbow) * s

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