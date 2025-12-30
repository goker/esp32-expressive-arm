# Robot Arm Controller

Smooth servo control for a 4-axis robot arm using ESP32-C3 and MicroPython, with AI-powered natural language control.

## Quick Start

```bash
# Clone and setup
cd servo-poc
python3 -m venv .venv
source .venv/bin/activate
pip install mpremote esptool pyyaml flask requests

# Flash MicroPython firmware (one-time setup)
bash setup.sh

# Run a demo
python3 demos/01_test_servos.py
```

## What This Does

This project lets you control a 4-servo robot arm in three ways:

1. **Basic Demos** - Pre-programmed motions (`demos/` folder)
2. **Web Calibration** - Interactive web UI to calibrate and test servos (`chicken/calibrator_web.py`)
3. **AI Control** - Natural language commands via Rust CLI (`robot-arm-rust/` - experimental)

## Architecture

```
Your Computer (Python)
  ↓ USB Serial (mpremote)
ESP32-C3 (MicroPython)
  ↓ GPIO 4,5,6,7 (PWM)
4 Servo Motors
```

**One-time setup:** Flash MicroPython firmware to ESP32
**Every run:** Python script sends MicroPython code via USB, ESP32 executes it immediately

No compilation. No reflashing. Just edit and run.

## Hardware

- ESP32-C3 development board
- 4 servo motors wired to GPIO pins 4, 5, 6, 7
- USB-C cable (must support data, not just charging)
- 5V power for servos (battery or external supply)

| Servo    | GPIO | Function   |
|----------|------|------------|
| Base     | 4    | Rotation   |
| Shoulder | 5    | Up/Down    |
| Elbow    | 6    | Bend       |
| Gripper  | 7    | Open/Close |

## Basic Demos

```bash
cd demos
python3 01_test_servos.py      # Test each servo individually
python3 02_arm_circles.py      # Circular shoulder+elbow motion
python3 03_base_rotation.py    # Smooth base rotation with accel/decel
python3 04_gripper_moves.py    # Gripper actions (snap, grab, release)
python3 05_wave_motion.py      # Wave across all joints
python3 run_all.py             # Run all demos in sequence
```

All demos use **minimum jerk trajectories** for smooth, human-like motion.

## Web Calibration Tool

Interactive web interface for servo calibration and testing:

```bash
cd chicken
python3 calibrator_web.py
# Open http://localhost:3001
```

**Features:**
- Live servo control with coarse/fine adjustments
- Set min/max/default positions for each servo
- Emergency stop (smooth return to safe position)
- Save calibration to `calibration_limits.json`
- Real-time position visualization

Alternative semantic calibrator:
```bash
python3 calibrator_semantic.py
# Open http://localhost:3002
```

Uses intuitive position names instead of angles (e.g., "arm extended" vs "90 degrees").

## Workflow System

Create multi-step motion sequences using the workflow designer:

```bash
cd chicken
python3 workflow_designer.py
# Open http://localhost:3000
```

1. Move servos to desired position
2. Click "Add Step" to save position
3. Build sequence of steps
4. Save workflow to JSON
5. Execute with: `python3 chicken.py workflow_name.json`

**See:** `chicken/WORKFLOW_DESIGNER.md` for full documentation

## AI Control (Experimental)

Natural language robot control using Gemini AI:

```bash
cd robot-arm-rust
cargo run -- do "pick up the object"
cargo run -- listen   # Voice input via OpenAI Whisper
```

The Rust CLI:
- Takes natural language commands
- Generates MicroPython code via Gemini API
- Executes code on ESP32
- Supports voice input

**See:** `robot-arm-rust/README.md` for setup

## Project Structure

```
servo-poc/
├── demos/                    # Basic motion demos
│   ├── utils.py             # Shared MicroPython code
│   ├── 01_test_servos.py    # Individual servo tests
│   ├── 02-05_*.py           # Motion demos
│   └── run_all.py           # Run all demos
│
├── chicken/                  # Advanced control & calibration
│   ├── calibrator_web.py    # Web-based calibrator
│   ├── calibrator_semantic.py   # Semantic position calibrator
│   ├── workflow_designer.py     # Workflow creation tool
│   ├── chicken.py           # Workflow executor
│   ├── main.py              # YAML-based pickup sequences
│   ├── calibration_limits.json  # Servo calibration data
│   ├── servo_config.json    # Servo configuration
│   ├── templates/           # HTML templates for web UIs
│   ├── workflows/           # Saved workflow JSON files
│   └── README.md            # Detailed chicken docs
│
├── robot-arm-rust/          # AI-powered CLI (Rust)
│   ├── src/main.rs         # Gemini API integration
│   └── README.md           # Setup instructions
│
├── examples/                # Quick diagnostic scripts
│   ├── test.py             # Full connection test
│   ├── simple.py           # Minimal servo test
│   └── led.py              # LED blink test
│
├── ai/                      # AI agent instructions
│   └── AGENT_INSTRUCTIONS.md
│
├── setup.sh                 # Flash MicroPython firmware
└── wipe.sh                  # Factory reset ESP32
```

## Motion Algorithms

### Minimum Jerk Trajectory
Smooth, human-like motion using quintic polynomial:
```
s(t) = 10t³ - 15t⁴ + 6t⁵
```

### Exponential Smoothing
Reduces servo jitter:
```
smooth_pos = old_pos × 0.5 + new_pos × 0.5
```

### Safety Watchdog
Automatically detaches servos after 10 seconds of inactivity to prevent overheating.

## Troubleshooting

**No USB device found:**
```bash
ls /dev/cu.usb*  # Check if device is visible
```
- Try different USB cable or port
- Close other programs using the port

**Stuck at "Connecting...":**
1. Hold BOOT button on ESP32
2. Run command
3. Release BOOT when upload starts

**Servos don't move:**
- Check 5V power supply to servos
- Verify wiring to GPIO 4, 5, 6, 7
- Run `python3 examples/test.py`

**Factory reset:**
```bash
bash wipe.sh      # Erase everything
bash setup.sh     # Reflash MicroPython
```

## Development

**Dependencies:**
```bash
pip install mpremote esptool pyyaml flask requests
```

**Project guidelines:** See `CLAUDE.md` for code style

**Virtual environment:**
```bash
source .venv/bin/activate   # Activate
deactivate                   # Deactivate when done
```

## How It Works

When you run a Python script:

1. Mac Python reads the script
2. Script contains MicroPython code as a string
3. `mpremote` sends code over USB to ESP32
4. ESP32 executes code in real-time
5. Servos respond immediately

**Two Pythons:**
- **Mac:** CPython 3.x - sends code, finds USB port
- **ESP32:** MicroPython 1.x - runs on chip, controls hardware

MicroPython is flashed **once**. After that, you just send code.

## Advanced Usage

**Run code on boot (standalone mode):**
```bash
mpremote fs cp my_script.py :main.py
mpremote reset
```
Now the robot runs independently with battery power.

**Interactive REPL:**
```bash
mpremote connect /dev/cu.usbserial-1140
# Now you can type MicroPython commands directly
```

## Documentation

- **[Chicken/Workflow System](chicken/README.md)** - Advanced workflows and calibration
- **[Workflow Designer](chicken/WORKFLOW_DESIGNER.md)** - Creating motion sequences
- **[Semantic Calibration](chicken/SEMANTIC_CALIBRATION.md)** - Intuitive position naming
- **[Rust AI CLI](robot-arm-rust/README.md)** - Natural language control

## License

MIT
