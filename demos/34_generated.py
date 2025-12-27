#!/usr/bin/env python3
"""
Demo 08: Playful Base Rotation
Rotates the base left and right in a smooth, playful manner.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Playful Base Rotation ===\\n")

DELAY = 0.015

# Rotate right
print("Rotating right...")
for angle in range(63, 150, 1):
    set_servo(0, angle)
    time.sleep(DELAY)

# Rotate left
print("Rotating left...")
for angle in range(150, 15, -1):
    set_servo(0, angle)
    time.sleep(DELAY)

# Rotate back to center
print("Returning to center...")
for angle in range(15, 63, 1):
    set_servo(0, angle)
    time.sleep(DELAY)

home()
print("\\n=== Playful rotation complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Playful Base Rotation")
    print("=" * 30)
    run_on_esp32(CODE)