# AI Agent Instructions: Generating Robot Arm Movement Patterns

## Your Mission

Generate executable Python code for robotic arm movement patterns that can run directly on an ESP32 microcontroller via MicroPython.

## Critical Rules

1. **ONLY return executable Python code** - No explanations, no markdown, no comments outside the code
2. **Follow the exact structure** shown in the examples below
3. **Respect calibration limits** - Never exceed the servo min/max ranges
4. **Use smooth motions** - Always use `set_servo()` with smoothing, not `set_servo_direct()`
5. **Return to home** - Always end with `home()` command

## Code Structure Template

```python
#!/usr/bin/env python3
"""
Demo XX: [Brief Description]
[One sentence about what the movement does]
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO XX: [Name] ===\\n")

# Your movement code here
# Use the available functions and follow patterns from examples

home()
print("\\n=== [Name] complete! ===")
'''

if __name__ == "__main__":
    print("Demo XX: [Name]")
    print("=" * 30)
    run_on_esp32(CODE)
```

## Available Hardware

- **4 Servos** with calibration limits:
  - **Base** (servo 0): min=0, max=180, default=63 (left/right rotation)
  - **Shoulder** (servo 1): min=1, max=121, default=60 (up/down)
  - **Elbow** (servo 2): min=0, max=152, default=100 (forward/backward)
  - **Gripper** (servo 3): min=80, max=180, default=90 (open/close)

## Available Functions (Pre-loaded in SERVO_HEADER)

### Servo Control
```python
set_servo(servo_num, angle)         # Smooth servo movement with jitter reduction
set_servo_direct(servo_num, angle)  # Direct movement without smoothing (use sparingly)
home()                              # Return all servos to default position
```

### Math Utilities
```python
minimum_jerk(t)  # Returns smooth trajectory value for t in [0,1]
                 # Use for natural, human-like motion interpolation
```

### Available Libraries
```python
import time
import math
```

### State Variables
```python
smooth_pos      # List of current smooth positions [base, shoulder, elbow, gripper]
current_pos     # List of integer positions
SERVO_NAMES     # ["Base", "Shoulder", "Elbow", "Gripper"]
```

## Movement Pattern Examples

### Example 1: Simple Sequential Motion
```python
CODE = SERVO_HEADER + '''
print("\\n=== DEMO: Wave Hello ===\\n")

# Move shoulder up and down 3 times
for wave in range(3):
    print(f"  Wave {wave + 1}/3")

    # Up
    for angle in range(60, 80, 1):
        set_servo(1, angle)
        time.sleep(0.01)

    # Down
    for angle in range(80, 59, -1):
        set_servo(1, angle)
        time.sleep(0.01)

    time.sleep(0.2)

home()
print("\\n=== Wave complete! ===")
'''
```

### Example 2: Coordinated Multi-Servo Motion
```python
CODE = SERVO_HEADER + '''
print("\\n=== DEMO: Smooth Reach ===\\n")

STEPS = 100
DELAY = 0.01

# Starting positions
start_shoulder = 60
start_elbow = 100

# Target positions
target_shoulder = 40
target_elbow = 120

print("Reaching forward...")
for i in range(STEPS):
    t = i / STEPS
    s = minimum_jerk(t)  # Smooth interpolation

    shoulder = start_shoulder + (target_shoulder - start_shoulder) * s
    elbow = start_elbow + (target_elbow - start_elbow) * s

    set_servo(1, shoulder)
    set_servo(2, elbow)
    time.sleep(DELAY)

time.sleep(0.5)

print("Returning home...")
home()
print("\\n=== Reach complete! ===")
'''
```

### Example 3: Circular/Wave Motion
```python
CODE = SERVO_HEADER + '''
print("\\n=== DEMO: Circular Pattern ===\\n")

RADIUS = 20
POINTS = 200
CYCLES = 5
DELAY = 0.005

center_shoulder = 60
center_elbow = 100

print(f"Drawing {CYCLES} circles...")
for cycle in range(CYCLES):
    print(f"  Circle {cycle + 1}/{CYCLES}")

    for i in range(POINTS):
        angle = (i / POINTS) * 2 * math.pi

        shoulder = center_shoulder + RADIUS * math.sin(angle)
        elbow = center_elbow + RADIUS * math.cos(angle)

        set_servo(1, shoulder)
        set_servo(2, elbow)
        time.sleep(DELAY)

home()
print("\\n=== Circles complete! ===")
'''
```

### Example 4: Phase-Shifted Wave Motion
```python
CODE = SERVO_HEADER + '''
print("\\n=== DEMO: Flowing Wave ===\\n")

POINTS = 300
CYCLES = 3
AMPLITUDE = 15
DELAY = 0.006

base_center = 63
shoulder_center = 60
elbow_center = 100

print(f"Running {CYCLES} wave cycles...")
for cycle in range(CYCLES):
    print(f"  Cycle {cycle + 1}/{CYCLES}")

    for i in range(POINTS):
        t = (i / POINTS) * 2 * math.pi

        # Each servo has phase offset for flowing effect
        base = base_center + AMPLITUDE * math.sin(t)
        shoulder = shoulder_center + AMPLITUDE * math.sin(t + 1.0)
        elbow = elbow_center + AMPLITUDE * math.sin(t + 2.0)

        set_servo(0, base)
        set_servo(1, shoulder)
        set_servo(2, elbow)
        time.sleep(DELAY)

home()
print("\\n=== Wave complete! ===")
'''
```

## Motion Design Guidelines

### 1. Smooth Trajectories
- Use small increments (1-2 degrees) with short delays (0.01-0.02s)
- Use `minimum_jerk()` for natural acceleration/deceleration
- Avoid sudden jumps between positions

### 2. Timing
- **Fast movements**: DELAY = 0.004 - 0.006s
- **Normal movements**: DELAY = 0.01 - 0.02s
- **Slow movements**: DELAY = 0.03 - 0.05s
- Add pauses with `time.sleep()` between movement sequences

### 3. Safety
- Always check servo limits before generating angles
- Start movements from default positions (base=63, shoulder=60, elbow=100, gripper=90)
- Never exceed calibration ranges
- Always end with `home()` to return to safe position

### 4. Patterns
- **Sequential**: One servo at a time
- **Parallel**: Multiple servos move simultaneously
- **Circular**: Use sin/cos with same frequency, phase offset
- **Wave**: Use sin/cos with different frequencies/phases
- **Interpolated**: Use `minimum_jerk()` for point-to-point

## Common Mistakes to Avoid

1. ❌ Don't include explanatory text outside code
2. ❌ Don't use markdown code blocks in your output
3. ❌ Don't add docstrings inside the CODE string
4. ❌ Don't exceed servo calibration limits
5. ❌ Don't forget to import from utils
6. ❌ Don't forget the `if __name__ == "__main__"` block
7. ❌ Don't forget to call `home()` at the end
8. ❌ Don't use `set_servo_direct()` for motion sequences

## Output Format

When you receive a request like "Create a figure-8 motion pattern", respond ONLY with:

```python
#!/usr/bin/env python3
"""
Demo 06: Figure-8 Pattern
Traces a figure-8 shape using shoulder and elbow
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 06: Figure-8 Pattern ===\\n")

# [Your implementation here]

home()
print("\\n=== Figure-8 complete! ===")
'''

if __name__ == "__main__":
    print("Demo 06: Figure-8 Pattern")
    print("=" * 30)
    run_on_esp32(CODE)
```

## Validation Checklist

Before returning code, verify:
- [ ] Code starts with `#!/usr/bin/env python3`
- [ ] Has proper docstring with demo name
- [ ] Imports from utils correctly
- [ ] CODE variable includes SERVO_HEADER prefix
- [ ] All servo angles within calibration limits
- [ ] Uses `set_servo()` for smooth motion
- [ ] Ends with `home()` call
- [ ] Has proper `if __name__ == "__main__"` block
- [ ] No explanatory text outside the code
- [ ] No markdown formatting in output

## Example Request/Response

**Request:** "Create a demo where the arm does a picking motion - reach forward, grip, pull back, release"

**Response:** (ONLY the code below, nothing else)
```python
#!/usr/bin/env python3
"""
Demo 07: Pick and Place
Simulates picking up an object and pulling it back
"""

from utils import run_on_esp32, SERVO_HEADER

CODE = SERVO_HEADER + '''
print("\\n=== DEMO 07: Pick and Place ===\\n")

STEPS = 80

print("Reaching forward...")
for i in range(STEPS):
    t = i / STEPS
    s = minimum_jerk(t)
    set_servo(1, 60 + (40 - 60) * s)
    set_servo(2, 100 + (130 - 100) * s)
    time.sleep(0.01)

time.sleep(0.3)

print("Gripping...")
for angle in range(90, 150, 2):
    set_servo(3, angle)
    time.sleep(0.01)

time.sleep(0.3)

print("Pulling back...")
for i in range(STEPS):
    t = i / STEPS
    s = minimum_jerk(t)
    set_servo(1, 40 + (60 - 40) * s)
    set_servo(2, 130 + (100 - 130) * s)
    time.sleep(0.01)

time.sleep(0.3)

print("Releasing...")
for angle in range(150, 89, -2):
    set_servo(3, angle)
    time.sleep(0.01)

home()
print("\\n=== Pick and place complete! ===")
'''

if __name__ == "__main__":
    print("Demo 07: Pick and Place")
    print("=" * 30)
    run_on_esp32(CODE)
```

---

Remember: Your output should be EXECUTABLE PYTHON CODE ONLY. No explanations, no markdown, just the code.
