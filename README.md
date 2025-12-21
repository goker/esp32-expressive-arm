# Siyeenove Robot Arm Controller

Smooth servo control for a 4-axis robot arm using ESP32-C3 and MicroPython.

---

## What's Actually Happening? (Architecture)

This project uses a **two-layer architecture** - code runs on BOTH your Mac and the ESP32:

```
┌─────────────────────────────────────┐
│  YOUR MAC (Python 3)                │
│  - Runs Python scripts              │
│  - Contains MicroPython code        │
│  - Uses mpremote to send commands   │
└──────────────┬──────────────────────┘
               │ USB Serial Cable
               │ (mpremote talks to ESP32)
               ▼
┌─────────────────────────────────────┐
│  ESP32-C3 (MicroPython Firmware)    │
│  - Receives code from Mac           │
│  - Executes code in real-time       │
│  - Controls servos via PWM          │
└──────────────┬──────────────────────┘
               │ GPIO pins 4,5,6,7
               ▼
          4x Servo Motors
```

### Are We Flashing Firmware Each Time?

**NO!** Here's what happens:

1. **ONE TIME SETUP** (`setup.sh`): Flash MicroPython firmware onto ESP32
   - This installs a tiny Python operating system on the chip
   - You only do this once (or when you want to update MicroPython)

2. **EVERY TIME YOU RUN A SCRIPT**:
   - Your Mac runs a Python script (e.g., `python3 01_test_servos.py`)
   - The script contains MicroPython code stored as a string
   - `mpremote` sends that code over USB to the ESP32
   - The ESP32 (which already has MicroPython) executes it immediately
   - The servos move in real-time

**Think of it like this:**
- **Your Mac** = TV remote (sends commands)
- **ESP32-C3** = Smart TV (receives and executes commands)
- **MicroPython firmware** = The TV's operating system (installed once)
- **mpremote** = The infrared signal (communication channel)

### Why This Approach?

**Pros:**
- ✅ Fast development - edit on Mac, run instantly
- ✅ No compilation needed
- ✅ Easy debugging with print statements
- ✅ Use your favorite Mac tools (VSCode, git, etc.)

**Cons:**
- ❌ Must stay plugged in via USB (unless you use WiFi mode)
- ❌ Can't run standalone without computer

---

## Hardware Required

- ESP32-C3 development board (Siyeenove kit)
- 4 servo motors (included in kit)
- USB-C cable (must support data transfer, not charge-only)
- The robot arm assembled per kit instructions

### Wiring (already done if using Siyeenove kit)

| Servo    | GPIO | Function   |
|----------|------|------------|
| Base     | 4    | Rotation   |
| Shoulder | 5    | Up/Down    |
| Elbow    | 6    | Bend       |
| Gripper  | 7    | Open/Close |

---

## Complete Setup Guide (Copy-Paste Ready)

### Step 1: Open Terminal

Press `Cmd + Space`, type `Terminal`, press Enter.

### Step 2: Navigate to Project

```bash
cd ~/repos/robotics/meow
```

(Or wherever you put this folder)

### Step 3: Create Python Virtual Environment

```bash
python3 -m venv venv
```

### Step 4: Activate Virtual Environment

```bash
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal prompt.

### Step 5: Install Python Dependencies

```bash
pip install esptool mpremote
```

### Step 6: Plug In the Robot

1. Connect ESP32-C3 to your Mac via USB-C cable
2. Turn ON the robot's power switch (if it has one)
3. Wait 2 seconds

### Step 7: Flash MicroPython Firmware

```bash
bash setup.sh
```

This downloads and flashes MicroPython to the ESP32. Takes about 30 seconds.

**If it fails with "Connecting...":**
1. Hold the **BOOT** button on the ESP32
2. Run the command again
3. Release BOOT after you see "Writing at 0x..."

### Step 8: Run a Demo!

```bash
cd demos
python3 01_test_servos.py
```

Or run all demos in sequence:
```bash
cd demos
python3 run_all.py
```

**Available demos:**
| Demo | Description |
|------|-------------|
| `01_test_servos.py` | Test each servo individually |
| `02_arm_circles.py` | Shoulder + elbow trace circles |
| `03_base_rotation.py` | Dramatic accel/decel sweeps |
| `04_gripper_moves.py` | Snap, grab, pulse, release |
| `05_wave_motion.py` | Flowing wave across all axes |
| `run_all.py` | Run all demos in sequence |

---

## Chicken Pickup Demo (Advanced)

A precision object pickup demo with calibration and smooth motion control.

```bash
cd chicken

# First time only: calibrate
python __calibrator_simple.py

# Run the pickup sequence
python main.py 01    # Lower arm
# <-- Place object here
python main.py 02    # Return to baseline
python main.py 03    # Pick up object
python main.py 04    # Drop object
```

**Features:**
- Servo calibration system (handles inverted servos)
- Global speed control (`SPEED_MULTIPLIER` in `servo_utils.py`)
- Minimum jerk trajectory for smooth motion
- Emergency stop function
- Complete documentation in `chicken/README.md`

---

## Quick Reference (After Initial Setup)

Every time you open a new terminal:

```bash
cd ~/repos/robotics/meow
source venv/bin/activate
cd demos
python3 02_arm_circles.py   # or any demo
```

---

## Other Commands

### Factory Reset ESP32
```bash
bash wipe.sh
```
Erases everything. Run `bash setup.sh` again after.

---

## Troubleshooting

### "No USB serial port found"
```bash
# Check if device is connected:
ls /dev/cu.usb*
```
- If nothing shows: try different USB cable or port
- If something shows: close any other program using the port (Arduino IDE, screen, etc.)

### "Failed to connect" or stuck at "Connecting..."
1. Hold **BOOT** button on ESP32
2. Run your command
3. Release BOOT when upload starts

### Servos don't move but code runs
1. Check power - servos need 5V (battery or external supply)
2. Run diagnostic: `python3 test_connection.py`
3. Check wiring to GPIO 4, 5, 6, 7

### "Permission denied" on serial port
```bash
# Usually not needed on macOS, but try:
sudo chmod 666 /dev/cu.usbserial-*
```

### Need to reflash everything
```bash
bash wipe.sh
bash setup.sh
```

---

## Project Files

```
meow/
├── demos/                      # Motion demos
│   ├── utils.py                # Shared utilities
│   ├── 01_test_servos.py       # Test each servo
│   ├── 02_arm_circles.py       # Arm circle motion
│   ├── 03_base_rotation.py     # Base accel/decel
│   ├── 04_gripper_moves.py     # Gripper actions
│   ├── 05_wave_motion.py       # Wave across all axes
│   └── run_all.py              # Run all demos
├── chicken/                    # Object pickup demo (advanced)
│   ├── main.py                 # Unified pickup script
│   ├── servo_utils.py          # Calibration & speed control
│   ├── servo_config.json       # Generated by calibrator
│   ├── __calibrator_simple.py  # Calibration wizard
│   ├── 00_red_button.py        # Emergency stop
│   └── README.md               # Chicken demo docs
├── legacy/                     # Older versions
├── archive/                    # Archived code
├── setup.sh                    # First-time setup
├── wipe.sh                     # Factory reset
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── venv/                       # Virtual environment (you create this)
```

---

## How It Works: Step-by-Step Example

Let's trace what happens when you run `python3 01_test_servos.py`:

1. **Your Mac's Python** reads the script
2. Script finds the USB port (e.g., `/dev/cu.usbserial-1234`)
3. Script has MicroPython code stored in a `CODE` variable (it's just a big string)
4. Script calls: `mpremote connect /dev/cu.usbserial-1234 exec <CODE>`
5. **mpremote** sends that code over USB serial to the ESP32
6. **ESP32's MicroPython** receives and executes the code line by line
7. Code sets up PWM on GPIO pins 4, 5, 6, 7
8. Code moves servos by changing PWM duty cycles
9. Servos respond in real-time

**Key insight:** The Python script on your Mac is like a "code delivery system" - it packages up MicroPython code and ships it to the ESP32 for execution.

### Two Python Environments

This is the confusing part - there are **two different Pythons** at work:

| Where | What | Version | Purpose |
|-------|------|---------|---------|
| **Your Mac** | CPython | 3.x | Find USB port, send code via mpremote |
| **ESP32** | MicroPython | 1.x | Execute code, control hardware |

When you see this in a script:
```python
CODE = '''
from machine import Pin, PWM  # This is MicroPython code!
servo = PWM(Pin(4), freq=50)
'''

subprocess.run(["mpremote", "exec", CODE])  # This is Mac Python code!
```

The outer code runs on your Mac. The inner `CODE` string runs on the ESP32.

---

## Math & Motion Algorithms

### Minimum Jerk Trajectory
The robot uses a mathematical formula that mimics human arm movement:
```
position = 10t³ - 15t⁴ + 6t⁵
```
This creates smooth acceleration and deceleration - no jerky stops.

### Anti-Jitter Smoothing
Cheap servos jitter. We fix this with exponential smoothing:
```
smooth_position = old_position × 0.5 + new_position × 0.5
```
Only updates the servo when the value actually changes.

---

## One-Liner Setup (For the Impatient)

```bash
cd ~/repos/robotics/meow && python3 -m venv venv && source venv/bin/activate && pip install esptool mpremote && bash setup.sh && cd demos && python3 run_all.py
```

---

## FAQ / Common Confusion

### Q: "Do I need to flash firmware every time I run a script?"
**A:** NO! You only flash MicroPython firmware once (using `setup.sh`). After that, scripts just send code to the already-running MicroPython.

### Q: "Can the robot work without my computer?"
**A:** Not by default. But you can upload code to run on boot:
```bash
mpremote fs cp my_script.py :main.py
mpremote reset
```
Now it runs standalone! Power it with a battery and it's independent.

### Q: "What's the difference between flashing and running?"
- **Flashing** = Installing the MicroPython OS (one-time, uses `setup.sh`)
- **Running** = Sending Python code to execute (every time, uses `mpremote`)

### Q: "Why two Python versions?"
Because MicroPython is tiny (fits on a chip with 4MB) while regular Python needs gigabytes. Your Mac ships code, ESP32 runs it.

---

## Deactivate Virtual Environment

When you're done:
```bash
deactivate
```

---

## License

MIT - Do whatever you want with it.

Built with Claude Code.
