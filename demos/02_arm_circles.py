#!/usr/bin/env python3
"""
Demo 02: Arm Circles
Shoulder and elbow trace smooth circles together
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 02: Arm Circles ===\\n")

RADIUS = 30
POINTS = 250
CIRCLES = 10
DELAY = 0.004

print(f"Drawing {CIRCLES} circles...")

for circle in range(CIRCLES):
    print(f"  Circle {circle + 1}/{CIRCLES}")
    for i in range(POINTS):
        angle = (i / POINTS) * 2 * math.pi

        shoulder = 90 + RADIUS * math.sin(angle)
        elbow = 90 + RADIUS * math.cos(angle)

        set_servo(1, shoulder)
        set_servo(2, elbow)

        time.sleep(DELAY)

# Smooth return to center
print("Returning to center...")
for i in range(100):
    t = i / 100
    s = minimum_jerk(t)
    set_servo(1, smooth_pos[1] + (90 - smooth_pos[1]) * s)
    set_servo(2, smooth_pos[2] + (90 - smooth_pos[2]) * s)
    time.sleep(0.004)

home()
print("\\n=== Circles complete! ===")
'''

if __name__ == "__main__":
    print("Demo 02: Arm Circles")
    print("=" * 30)
    run_on_esp32(CODE)
