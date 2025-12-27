#!/usr/bin/env python3
"""
Demo 08: Funny Base Rotation
Rotates the base servo back and forth with varying speeds.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Funny Base Rotation ===\\n")

def wobble(center, amplitude, duration, delay):
    start_time = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start_time) < duration:
        t = (time.ticks_ms() - start_time) / duration
        angle = center + amplitude * math.sin(2 * math.pi * t)
        set_servo(0, angle)
        time.sleep(delay)

print("Starting funny base rotation...")
wobble(63, 40, 2000, 0.01)  # Quick wobble
time.sleep(0.5)
wobble(63, 60, 3000, 0.02)  # Slower, wider wobble
time.sleep(0.5)
wobble(63, 20, 1000, 0.005) # Very fast, small wobble

home()
print("\\n=== Funny base rotation complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Funny Base Rotation")
    print("=" * 30)
    run_on_esp32(CODE)