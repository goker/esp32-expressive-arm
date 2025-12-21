#!/usr/bin/env python3
"""
Demo 05: Wave Motion
Flowing wave across all axes with phase offsets
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 05: Wave Motion ===\\n")

POINTS = 300
CYCLES = 3
AMPLITUDE = 30
DELAY = 0.006

print(f"Running {CYCLES} wave cycles...")

for cycle in range(CYCLES):
    print(f"  Cycle {cycle + 1}/{CYCLES}")
    for i in range(POINTS):
        t = (i / POINTS) * 2 * math.pi

        # Each axis has offset phase for flowing effect
        base = 90 + AMPLITUDE * 0.5 * math.sin(t)
        shoulder = 90 + AMPLITUDE * 0.4 * math.sin(t + 0.8)
        elbow = 90 + AMPLITUDE * 0.5 * math.sin(t + 1.6)
        gripper = 75 + AMPLITUDE * 0.4 * math.sin(t + 2.4)

        set_servo(0, base)
        set_servo(1, shoulder)
        set_servo(2, elbow)
        set_servo(3, gripper)

        time.sleep(DELAY)

# Smooth return home
print("Returning home...")
start_pos = [smooth_pos[i] for i in range(4)]
for i in range(100):
    t = i / 100
    s = minimum_jerk(t)
    for servo in range(4):
        pos = start_pos[servo] + (90 - start_pos[servo]) * s
        set_servo(servo, pos)
    time.sleep(0.005)

home()
print("\\n=== Wave motion complete! ===")
'''

if __name__ == "__main__":
    print("Demo 05: Wave Motion")
    print("=" * 30)
    run_on_esp32(CODE)
