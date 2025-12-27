#!/usr/bin/env python3
"""
Demo: Pick something up
"""
from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
import time

print("\\n=== DEMO: Pick something up ===\\n")

def main_sequence():
    """The main execution flow for the task."""
    reach_forward()
    grip()
    time.sleep(0.5)
    lift()

main_sequence()

print("\\n=== Pick something up complete! ===")
'''

if __name__ == "__main__":
    print("Demo: Pick something up")
    print("=" * 30)
    run_on_esp32(CODE)