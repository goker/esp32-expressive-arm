#!/usr/bin/env python3
from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
import time

print("Action: Starting sequence...")

def main_sequence():
    home()
    time.sleep(1)
    reach_forward()
    time.sleep(1)
    home()
    time.sleep(1)
    reach_forward()
    time.sleep(1)
    home()

main_sequence()
print("Action: Sequence complete!")
'''

if __name__ == "__main__":
    run_on_esp32(CODE)