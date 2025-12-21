#!/usr/bin/env python3
"""Simplest possible test - just set servos to 90 and hold"""

import subprocess
import glob

port = glob.glob('/dev/cu.usbserial-*')[0]
print(f"Port: {port}")

CODE = '''
from machine import Pin, PWM
import time

# Just set up and hold position - nothing fancy
s0 = PWM(Pin(4), freq=50)
s1 = PWM(Pin(5), freq=50)
s2 = PWM(Pin(6), freq=50)
s3 = PWM(Pin(7), freq=50)

# 77 duty = 90 degrees
s0.duty(77)
s1.duty(77)
s2.duty(77)
s3.duty(77)

print("All servos set to 90 degrees")
print("Holding for 10 seconds... watch/listen!")

# Keep running so PWM stays active
for i in range(10):
    print(f"  {10-i}...")
    time.sleep(1)

print("Done")
'''

subprocess.run(["mpremote", "connect", port, "exec", CODE])
print("\nIf nothing happened - it's power, not code.")
