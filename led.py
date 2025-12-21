#!/usr/bin/env python3
"""Blink onboard LED"""

import subprocess
import glob

port = glob.glob('/dev/cu.usbserial-*')[0]
print(f"Port: {port}")

CODE = '''
from machine import Pin
import time

print("Trying common ESP32-C3 LED pins...")

# Try common LED pins on ESP32-C3 boards
pins_to_try = [8, 2, 3, 10, 18, 19]

for p in pins_to_try:
    try:
        led = Pin(p, Pin.OUT)
        print(f"Blinking GPIO {p}...")
        for _ in range(5):
            led.value(1)
            time.sleep(0.2)
            led.value(0)
            time.sleep(0.2)
    except:
        pass

print("Done blinking!")
'''

subprocess.run(["mpremote", "connect", port, "exec", CODE])
