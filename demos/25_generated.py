#!/usr/bin/env python3
"""
Demo 08: Waving Base
Rotates the base back and forth to simulate waving.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Waving Base ===\\n")

WAVE_ANGLE = 30
STEPS = 30
DELAY = 0.01

# Wave Right
print("Waving right...")
for i in range(STEPS):
    t = i / STEPS
    s = minimum_jerk(t)
    angle = 63 + WAVE_ANGLE * s
    set_servo(0, angle)
    time.sleep(DELAY)

time.sleep(0.2)

# Wave Left
print("Waving left...")
for i in range(STEPS):
    t = i / STEPS
    s = minimum_jerk(t)
    angle = 63 + -WAVE_ANGLE * s
    set_servo(0, angle)
    time.sleep(DELAY)

time.sleep(0.2)

# Wave Right
print("Waving right...")
for i in range(STEPS):
    t = i / STEPS
    s = minimum_jerk(t)
    angle = 63 + WAVE_ANGLE * s
    set_servo(0, angle)
    time.sleep(DELAY)

time.sleep(0.2)

# Wave Left
print("Waving left...")
for i in range(STEPS):
    t = i / STEPS
    s = minimum_jerk(t)
    angle = 63 + -WAVE_ANGLE * s
    set_servo(0, angle)
    time.sleep(DELAY)

time.sleep(0.2)

home()
print("\\n=== Waving complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Waving Base")
    print("=" * 30)
    run_on_esp32(CODE)