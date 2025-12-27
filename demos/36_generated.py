#!/usr/bin/env python3
"""
Demo 08: Pick Up Object (Smooth)
Reaches forward, grips, lifts slightly, and releases
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Pick Up Object (Smooth) ===\\n")

STEPS = 50
DELAY = 0.02

# Initial positions (assumed)
start_shoulder = smooth_pos[1]  # Current shoulder position
start_elbow = smooth_pos[2]     # Current elbow position
start_gripper = smooth_pos[3]   # Current gripper position

# Target positions for reaching forward
reach_shoulder = 30
reach_elbow = 140

# Gripper positions
grip_angle = 160  # Tighter grip
release_angle = 90 # More open

# Lifting positions (slight lift)
lift_shoulder = 35

print("Reaching forward...")
for i in range(STEPS):
    t = i / STEPS
    s = minimum_jerk(t)
    shoulder = start_shoulder + (reach_shoulder - start_shoulder) * s
    elbow = start_elbow + (reach_elbow - start_elbow) * s
    set_servo(1, shoulder)
    set_servo(2, elbow)
    time.sleep(DELAY)

time.sleep(0.3)

print("Gripping...")
for angle in range(int(start_gripper), grip_angle, 1):
    set_servo(3, angle)
    time.sleep(0.02)

time.sleep(0.5) # Important pause to ensure firm grip

print("Lifting slightly...")
lift_steps = 30
for i in range(lift_steps):
    t = i / lift_steps
    s = minimum_jerk(t)
    shoulder = reach_shoulder + (lift_shoulder - reach_shoulder) * s
    set_servo(1, shoulder)
    time.sleep(DELAY)

time.sleep(0.3)

print("Releasing...")
for angle in range(grip_angle, release_angle, -1):
    set_servo(3, angle)
    time.sleep(0.02)

time.sleep(0.3)

home()
print("\\n=== Pick up complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Pick Up Object (Smooth)")
    print("=" * 30)
    run_on_esp32(CODE)