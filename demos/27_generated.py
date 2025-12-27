```python
#!/usr/bin/env python3
"""
Demo 08: Idle
Does nothing.
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 08: Idle ===\\n")

print("Idling...")
time.sleep(1)

home()
print("\\n=== Idle complete! ===")
'''

if __name__ == "__main__":
    print("Demo 08: Idle")
    print("=" * 30)
    run_on_esp32(CODE)
```