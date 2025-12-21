#!/usr/bin/env python3
"""
Demo 03: Base Rotation
Dramatic acceleration/deceleration sweeps using minimum jerk
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 03: Base Rotation ===\\n")

def sweep(start, end, points=300, delay=0.003):
    """Sweep with minimum jerk accel/decel"""
    for i in range(points):
        t = i / points
        s = minimum_jerk(t)
        pos = start + (end - start) * s
        set_servo(0, pos)
        time.sleep(delay)

# Sweep right
print("Sweeping right (90 -> 160)...")
sweep(90, 160)
time.sleep(0.1)

# Whip left past center
print("Sweeping left (160 -> 20)...")
sweep(160, 20)
time.sleep(0.1)

# Return to center
print("Returning to center (20 -> 90)...")
sweep(20, 90, points=200, delay=0.004)

home()
print("\\n=== Base rotation complete! ===")
'''

if __name__ == "__main__":
    print("Demo 03: Base Rotation")
    print("=" * 30)
    run_on_esp32(CODE)
