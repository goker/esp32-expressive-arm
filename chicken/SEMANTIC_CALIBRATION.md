# Semantic Calibration Guide

## Why Semantic Labels?

Instead of abstract "min/max/default" angles, this calibrator uses **descriptive labels** that match what the robot arm is physically doing. This makes calibration intuitive and less error-prone.

## Quick Start

```bash
cd chicken
python calibrator_semantic.py
```

Open http://localhost:3001

## Calibration Process

For each servo, you'll see **3 semantic buttons** describing physical positions:

### 🔄 Base (Rotation)
- **← Full Left**: Rotate base all the way to the left
- **● Center**: Center position for base
- **Full Right →**: Rotate base all the way to the right

### 💪 Shoulder (Up/Down)
- **↑ Lifted Up**: Arm lifted up (away from ground)
- **→ Neutral**: Neutral middle position
- **↓ Reaching Down**: Arm reaching down toward ground

### 🦾 Elbow (Forward/Back)
- **← Pulled Back**: Tip of arm pulled back/away from ground
- **● Neutral**: Neutral middle position
- **→ Extended Forward**: Tip extended forward/down toward ground

### 🤏 Gripper (Open/Close)
- **🤏 Closed**: Gripper fully closed
- **● Neutral**: Neutral half-open position
- **✋ Open**: Gripper fully open

## How to Calibrate

1. **Start with one servo** (e.g., Gripper)

2. **Move to first position** using sliders or +/- buttons
   - Example: Close the gripper fully

3. **Click the semantic button** when in position
   - Click "🤏 Closed"
   - Button turns green
   - Position is saved

4. **Repeat for other positions**
   - Move to neutral position → Click "● Neutral"
   - Move to fully open → Click "✋ Open"

5. **Move to next servo** and repeat

6. **Save calibration** when all servos are done
   - Click "💾 SAVE CALIBRATION TO FILE"
   - Creates `calibration_limits.json`

## Semantic → Technical Mapping

The semantic labels map to technical values:

| Servo | Semantic | Technical | Notes |
|-------|----------|-----------|-------|
| **Base** | Full Left | `min` | Left rotation limit |
| | Center | `default` | Straight ahead |
| | Full Right | `max` | Right rotation limit |
| **Shoulder** | Lifted Up | `min` | Arm up, away from ground |
| | Neutral | `default` | Middle position |
| | Reaching Down | `max` | Arm down, toward ground |
| **Elbow** | Pulled Back | `min` | Tip away from ground |
| | Neutral | `default` | Middle position |
| | Extended Forward | `max` | Tip toward ground |
| **Gripper** | Closed | `min` | Gripping |
| | Neutral | `default` | Half open |
| | Open | `max` | Fully open |

## Example Output

After calibration, `calibration_limits.json` looks like:

```json
{
  "base": {
    "min": 0,      // Full Left
    "default": 63, // Center
    "max": 180     // Full Right
  },
  "shoulder": {
    "min": 1,      // Lifted Up
    "default": 60, // Neutral
    "max": 121     // Reaching Down
  },
  "elbow": {
    "min": 0,      // Pulled Back
    "default": 100,// Neutral
    "max": 152     // Extended Forward
  },
  "gripper": {
    "min": 80,     // Closed
    "default": 90, // Neutral
    "max": 180     // Open
  }
}
```

## Tips

- **Start with gripper** - easiest to visualize open/closed
- **Use fine adjustment** (+1/-1 buttons) for precision
- **Emergency stop** returns all servos to default positions
- **Watch the angles** displayed in gold to see current position
- **Green buttons** = position saved
- **Summary at bottom** shows all saved calibration values

## Common Scenarios

### "The arm goes the wrong direction!"
This is usually because a servo is inverted. The semantic labels still work - just physically observe which direction is "up" vs "down" for your specific hardware, then save accordingly.

### "I made a mistake!"
Just move the servo to the correct position and click the semantic button again. It will overwrite the previous value.

### "What if my arm is different?"
The semantic labels describe **logical positions** not absolute angles. The calibration captures whatever angles YOUR specific arm needs for those positions.

## Advantages Over Technical Calibration

❌ **Old way**: "Set servo 1 to max angle"
- What does "max" mean physically?
- Is max up or down?
- Hard to remember

✅ **New way**: "Move arm to Reaching Down position"
- Clear physical description
- Easy to understand
- Matches mental model

## Integration with Motion Sequences

The YAML sequences (like `correct_sequence.yaml`) use these semantic keywords:

```yaml
# Lower arm to ground
position: [default, max, min, max]
#          ^^^^^^^ ^^^ ^^^  ^^^
#          center  down back open
```

Now you know exactly what the arm will do!
