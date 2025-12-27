#!/usr/bin/env python3
"""
Demo 08: Wave to the Crowd
Simulates waving to a crowd by moving the base and shoulder servos.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Wave to the Crowd ===\\n")

WAVE_COUNT = 3
DELAY = 0.1

print("Starting wave...")
for wave in range(WAVE_COUNT):
    print(f"Wave {wave + 1}/{WAVE_COUNT}")

    # Wave right
    for angle in range(63, 90, 1):
        set_servo(0, angle)
        set_servo(1, 60 + 5 * math.sin(angle/10)) # Add some shoulder movement
        time.sleep(0.01)

    # Wave left
    for angle in range(90, 36, -1):
        set_servo(0, angle)
        set_servo(1, 60 + 5 * math.sin(angle/10)) # Add some shoulder movement
        time.sleep(0.01)

    # Back to center
    for angle in range(36, 63, 1):
        set_servo(0, angle)
        set_servo(1, 60 + 5 * math.sin(angle/10)) # Add some shoulder movement
        time.sleep(0.01)

    time.sleep(DELAY)

home()
print("\\n=== Wave complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Wave to the Crowd")
    print("=" * 30)
    run_on_esp32(CODE)