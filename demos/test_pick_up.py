#!/usr/bin/env python3
"""
Manual Test: Pick Up Object
Tests the high-level blocking functions for picking and placing.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("=== Manual Test: Pick Up Object ===")

def main_sequence():
    home()
    reach_forward()
    grip()
    lift()
    home()
    release()
    home()

main_sequence()
print("=== Manual Test: Pick Up Object complete! ===")
'''

if __name__ == "__main__":
    print("Manual Test: Pick Up Object")
    print("=" * 30)
    run_on_esp32(CODE)
