#!/usr/bin/env python3
from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
import time

print("Action: Starting sequence...")

def main_sequence():
    reach_forward()
    grip()
    time.sleep(0.5)
    lift()

main_sequence()
print("Action: Sequence complete!")
'''

if __name__ == "__main__":
    run_on_esp32(CODE)