#!/usr/bin/env python3
"""
Demo: Wave
"""
from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
import time

print("\\n=== DEMO: Wave ===\\n")

def main_sequence():
    """The main execution flow for the task."""
    home()
    time.sleep(1)
    reach_forward()
    time.sleep(1)
    home()
    time.sleep(1)
    reach_forward()
    time.sleep(1)
    home()
    time.sleep(1)

main_sequence()

print("\\n=== Wave complete! ===")
'''

if __name__ == "__main__":
    print("Demo: Wave")
    print("=" * 30)
    run_on_esp32(CODE)