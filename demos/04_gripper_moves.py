#!/usr/bin/env python3
"""
Demo 04: Gripper Movements
Various gripper motions: snap, grab, pulse, release
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 04: Gripper Moves ===\\n")

# 1. Snap open
print("Snap open...")
for i in range(80):
    t = i / 80
    s = t ** 0.3  # Fast start, slow end
    gripper = 90 + (120 - 90) * s
    set_servo(3, gripper)
    time.sleep(0.003)
time.sleep(0.2)

# 2. Gentle grab (like grabbing an egg)
print("Gentle grab...")
for i in range(200):
    t = i / 200
    s = 1 - (1 - t) ** 0.4  # Fast then slow
    gripper = 120 + (40 - 120) * s
    set_servo(3, gripper)
    time.sleep(0.005)
time.sleep(0.3)

# 3. Quick release and catch
print("Quick release and catch...")
for i in range(60):
    t = i / 60
    s = minimum_jerk(t)
    gripper = 40 + (100 - 40) * s
    set_servo(3, gripper)
    time.sleep(0.003)

time.sleep(0.05)

for i in range(80):
    t = i / 80
    s = 1 - (1 - t) ** 0.5
    gripper = 100 + (45 - 100) * s
    set_servo(3, gripper)
    time.sleep(0.004)
time.sleep(0.2)

# 4. Pulsing grip
print("Pulsing grip...")
for pulse in range(4):
    # Squeeze
    for i in range(50):
        t = i / 50
        s = minimum_jerk(t)
        gripper = 45 + (35 - 45) * s
        set_servo(3, gripper)
        time.sleep(0.004)
    # Release slightly
    for i in range(50):
        t = i / 50
        s = minimum_jerk(t)
        gripper = 35 + (50 - 35) * s
        set_servo(3, gripper)
        time.sleep(0.004)
time.sleep(0.2)

# 5. Smooth release
print("Smooth release...")
for i in range(150):
    t = i / 150
    s = minimum_jerk(t)
    gripper = 50 + (90 - 50) * s
    set_servo(3, gripper)
    time.sleep(0.005)

home()
print("\\n=== Gripper demo complete! ===")
'''

if __name__ == "__main__":
    print("Demo 04: Gripper Moves")
    print("=" * 30)
    run_on_esp32(CODE)
