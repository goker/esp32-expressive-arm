# Chicken - Robot Arm Control

Precision robot arm control with multiple ways to create sequences:
- **Pre-defined sequences** (`main.py`) - YAML-based with semantic keywords
- **Custom workflows** (`workflow_designer.py`) - Visual web designer for custom sequences
- **Semantic calibration** (`calibrator_semantic.py`) - Intuitive servo calibration

## Quick Start Options

### Option A: Pre-defined Pickup Sequence (main.py)

```bash
cd chicken

# 1. Calibrate (first time only)
python calibrator_semantic.py
# Open http://localhost:3001 and follow the intuitive prompts

# 2. Run pickup sequence
python main.py 01    # Lower arm
# <-- PLACE OBJECT HERE
python main.py 02    # Baseline
python main.py 03    # Pick up object
python main.py 04    # Drop object
```

### Option B: Design Custom Workflows (NEW!)

Create your own sequences with a visual web interface - exactly like the calibrator:

```bash
cd chicken

# 1. Calibrate (first time only)
python calibrator_semantic.py

# 2. Design your workflow
python workflow_designer_simple.py
# Open http://localhost:3002
# - Move servos to position (just like calibrator!)
# - Click "Add Step"
# - Repeat to build sequence
# - Save workflow

# 3. Execute your workflow
python chicken_simple.py my_workflow.json
```

**Works exactly like the calibrator - no inversion logic, just save positions!**

**Speed too fast?** Edit `servo_utils.py` and increase `SPEED_MULTIPLIER` (e.g., `2.0` for half speed).

## First Time Setup: Calibration

**IMPORTANT:** Run calibration before using any chicken scripts!

### NEW: Semantic Web Calibrator (Recommended!)

The semantic calibrator uses **intuitive descriptions** instead of abstract angles:

```bash
python calibrator_semantic.py
```

Then open http://localhost:3001

**Features:**
- 🎯 **Intuitive labels**: "Gripper Open/Closed", "Arm Reaching Down"
- 🖱️ **Visual interface**: Sliders + fine control buttons
- 💡 **Help text**: Describes what each position means
- ✅ **Visual feedback**: Buttons turn green when saved
- 🛑 **Emergency stop**: Returns to safe position instantly

**Example labels:**
- Gripper: "🤏 Closed" / "● Neutral" / "✋ Open"
- Shoulder: "↑ Lifted Up" / "→ Neutral" / "↓ Reaching Down"
- Elbow: "← Pulled Back" / "● Neutral" / "→ Extended Forward"

See [SEMANTIC_CALIBRATION.md](SEMANTIC_CALIBRATION.md) for detailed guide.

### Alternative: Simple Terminal Calibrator

```bash
python __calibrator_simple.py
```

Terminal-based, tests shoulder & elbow only. Saves to `servo_config.json`.

You only need to calibrate once (unless servos get rewired).

### Adjust Movement Speed:
Edit `servo_utils.py` and change `SPEED_MULTIPLIER`:
```python
SPEED_MULTIPLIER = 1.0  # Higher = slower, Lower = faster
```
- `1.0` = normal speed (current default)
- `2.0` = twice as slow (better for precision)
- `3.0` = ultra smooth and slow
- `0.5` = twice as fast

This affects ALL movements globally.

### Full Calibration (All 4 Servos):
```bash
python __calibrator.py
```
Use this if you also need to calibrate base rotation and gripper.

## Usage

### Main Script Method (Recommended)
All stages in one file with proper state management:

```bash
cd chicken

python main.py 01  # Lower arm for placement
# <-- PLACE CHICKEN HERE
python main.py 02  # Return to baseline
python main.py 03  # Pick up chicken
python main.py 04  # Drop chicken

# Emergency stop
python main.py 00
```

### Emergency Stop
```bash
python main.py 00
```
or
```bash
python 00_red_button.py
```
Returns all servos to safe home position without rotating base.

## Detailed Stage Breakdown

### Stage 01: Lower for Placement
```bash
python main.py 01
```
- Smoothly lowers arm from home (90,90,90,90) to ground (90,175,80,120)
- Opens gripper fully
- **STOP and place your object in front of the gripper**

### Stage 02: Return to Baseline
```bash
python main.py 02
```
- Uses `home()` function to snap arm back to (90,90,90,90)
- Slowly opens gripper from 90° to 120° (fully open)
- Sets clean reference point for pickup

### Stage 03: Pick Up Object
```bash
python main.py 03
```
1. **Phase 1**: Lowers arm smoothly to object position (90,175,80,120)
2. **Phase 2**: Closes gripper around object (120° → 40°)
3. **Phase 3**: Lifts arm smoothly back to home with object (90,90,90,40)

### Stage 04: Drop Object
```bash
python main.py 04
```
- Opens gripper slowly (40° → 120°)
- Arm already at home position from stage 03

## Complete Workflow

```bash
# 1. Calibrate (first time only)
python __calibrator_simple.py

# 2. Run the sequence
python main.py 01    # Lower
# <-- Place object
python main.py 02    # Baseline
python main.py 03    # Pick up
python main.py 04    # Drop

# If something goes wrong:
python main.py 00    # Emergency stop
```

## Tips

- Use a lightweight object (toy, eraser, small block, rubber chicken)
- Place object 2-3 inches in front of gripper when lowered
- If grip fails, adjust object position and try again
- Gripper works best with objects 1-3 inches wide
- All movements use minimum jerk trajectory for smooth motion
- Base never rotates during pickup sequence

## Technical Details

### Servo Positions (Base, Shoulder, Elbow, Gripper)

| Stage | Starting Position | Ending Position | Notes |
|-------|------------------|-----------------|-------|
| **01 Lower** | (90, 90, 90, 90) | (90, 175, 80, 120) | Lower arm, open gripper |
| **02 Baseline** | (90, 175, 80, 120) | (90, 90, 90, 120) | `home()` snaps arm, then smooth gripper |
| **03 Pickup** | | | Three phases |
| └─ Phase 1 | (90, 90, 90, 90) | (90, 175, 80, 120) | Lower to object |
| └─ Phase 2 | (90, 175, 80, 120) | (90, 175, 80, 40) | Close gripper |
| └─ Phase 3 | (90, 175, 80, 40) | (90, 90, 90, 40) | Lift with object |
| **04 Drop** | (90, 90, 90, 40) | (90, 90, 90, 120) | Open gripper only |

### Movement Algorithm
- **Minimum Jerk Trajectory**: `10t³ - 15t⁴ + 6t⁵` (smooth acceleration/deceleration)
- **Direct Servo Control**: Uses `set_servo_direct()` for immediate response
- **Calibration Applied**: All angles automatically adjusted based on `servo_config.json`
- **Speed Control**: All movements respect `SPEED_MULTIPLIER` from `servo_utils.py`

### Files
- `main.py` - All stages in one script (recommended)
- `servo_utils.py` - Calibration loading and speed control
- `servo_config.json` - Generated by calibrator, stores servo inversions
- `__calibrator_simple.py` - Shoulder/elbow calibration wizard
- `00_red_button.py` - Emergency stop (legacy)
