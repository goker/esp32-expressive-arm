# Workflow Designer & Executor

Create custom robot arm sequences with an intuitive web interface!

## Quick Start

### 1. Design Your Workflow

```bash
python workflow_designer.py
```

Open http://localhost:3002

### 2. Execute Your Workflow

```bash
python chicken.py my_workflow.json
```

## How It Works

### Designing Workflows

The workflow designer lets you create multi-step sequences by:

1. **Moving servos** to desired positions using sliders
2. **Adding steps** - click "Add Step" to save that position
3. **Building sequences** - repeat to create full workflows
4. **Saving** - saves workflow as JSON file

#### Example Workflow Creation

1. **Start designer**: `python workflow_designer.py`
2. **Set workflow name**: "Pick Up Ball"
3. **Move servos** to position 1 (ready position)
4. **Add step**: Name it "Ready position", duration 2.0s
5. **Move servos** to position 2 (lowered to object)
6. **Add step**: Name it "Lower to object", duration 3.0s
7. **Move servos** to position 3 (gripper closed)
8. **Add step**: Name it "Grip object", duration 1.5s
9. **Save workflow** - creates `workflows/pick_up_ball.json`

### Executing Workflows

Run saved workflows with `chicken.py`:

```bash
# Execute a workflow
python chicken.py workflows/pick_up_ball.json

# Or just the filename (searches workflows/ directory)
python chicken.py pick_up_ball.json

# List all workflows
python chicken.py --list
```

## Workflow Designer Features

### Servo Controls
- **Sliders** for each servo (Base, Shoulder, Elbow, Gripper)
- **Fine control** buttons: +1/-1 degree
- **Coarse control** buttons: +10/-10 degrees
- **Real-time preview** on connected robot

### Step Management
- **Add steps** at current servo position
- **Name each step** descriptively
- **Set duration** for smooth motion (0.1-10s)
- **Go to step** - jump robot to any saved step
- **Remove steps** - delete unwanted steps
- **Reorder** - see all steps in sequence

### Workflow Management
- **Save workflows** to JSON files
- **Load workflows** from saved files
- **New workflow** - start fresh
- **Edit metadata** - name and description

### Interface
- **Real-time position display** in large numbers
- **Step list** showing all positions
- **Visual feedback** for all actions
- **Saved workflow browser** - click to load

## Workflow JSON Format

Workflows are saved as JSON:

```json
{
  "name": "Pick Up Ball",
  "description": "Picks up a ball from the ground",
  "created": "2025-12-26T12:30:00",
  "steps": [
    {
      "name": "Ready position",
      "position": [60, 120, 110, 100],
      "duration": 2.0,
      "description": "Move to ready position"
    },
    {
      "name": "Lower to object",
      "position": [60, 0, 0, 180],
      "duration": 3.0,
      "description": "Lower arm to ground level"
    }
  ]
}
```

### Position Format

`position: [base, shoulder, elbow, gripper]`

All angles in degrees (0-180).

### Duration

Time in seconds for the robot to smoothly move from previous position to this position.
- Faster movements: 0.5-1.5s
- Normal movements: 2.0-3.0s
- Slow/careful movements: 4.0-6.0s

## Tips & Best Practices

### Creating Smooth Workflows

1. **Start simple** - Begin with 3-4 steps
2. **Test each step** - Use "Go to step" to verify positions
3. **Use appropriate durations**:
   - Quick gripper open/close: 1.0-1.5s
   - Arm movements: 2.0-3.0s
   - Large movements: 4.0-6.0s
4. **Add pauses** - The executor adds 0.3s pause between steps

### Naming Convention

Good step names help you understand the workflow:
- ✓ "Ready position"
- ✓ "Lower to object"
- ✓ "Close gripper"
- ✗ "Step 1"
- ✗ "Position"

### Safety

- **Test positions** before saving steps
- **Watch the robot** during execution
- **Start with longer durations** (safer/smoother)
- **Use emergency stop** in calibrator if needed

## Example Workflows

### Simple Wave
```
1. Ready position [60, 120, 110, 100] - 2.0s
2. Wave left [30, 120, 110, 100] - 1.5s
3. Wave right [90, 120, 110, 100] - 1.5s
4. Center [60, 120, 110, 100] - 1.5s
```

### Pick and Place
```
1. Ready position [60, 120, 110, 100] - 2.0s
2. Lower to pickup [60, 0, 0, 180] - 3.0s
3. Close gripper [60, 0, 0, 80] - 1.5s
4. Lift object [60, 120, 110, 80] - 3.0s
5. Move to drop location [90, 120, 110, 80] - 2.0s
6. Lower to drop [90, 0, 0, 80] - 3.0s
7. Open gripper [90, 0, 0, 180] - 1.5s
8. Return home [60, 120, 110, 100] - 3.0s
```

## Troubleshooting

### Designer won't connect
- Make sure ESP32 is plugged in
- Check USB cable supports data
- Try: `ls /dev/cu.usbserial-*`

### Servos move to wrong positions
- Run calibration first: `python calibrator_semantic.py`
- Check `servo_config.json` for inversions
- Verify positions in designer match robot

### Workflow won't execute
- Check JSON file exists in `workflows/` directory
- Run with: `python chicken.py --list` to see all workflows
- Verify file is valid JSON

### Movements too fast/slow
- Adjust duration in each step
- Longer duration = slower, smoother movement
- Shorter duration = faster movement

## Advanced: Manual Workflow Editing

You can manually edit workflow JSON files:

```json
{
  "name": "My Custom Workflow",
  "description": "Hand-edited workflow",
  "steps": [
    {
      "name": "Custom position",
      "position": [45, 90, 135, 100],
      "duration": 2.5
    }
  ]
}
```

Just save in `workflows/` directory and run with `chicken.py`.

## Integration with AI

The workflow JSON format is perfect for AI generation! Use the AI agent instructions in the `ai/` folder to generate workflows automatically.

Example: Ask AI to create a "figure-8 motion" workflow, and it can generate the JSON directly.

## Comparison with main.py

| Feature | main.py | workflow_designer.py |
|---------|---------|---------------------|
| Format | YAML with keywords | JSON with angles |
| Creation | Manual editing | Visual web UI |
| Positions | Semantic (min/max) | Direct angles |
| Preview | No preview | Real-time preview |
| Best for | Pre-defined sequences | Custom sequences |

Both systems work great - use whichever fits your workflow!

## Next Steps

1. **Create your first workflow** with the designer
2. **Test it** with `chicken.py`
3. **Build a library** of useful workflows
4. **Share workflows** - just share the JSON file!
5. **Automate** - run workflows from scripts or buttons

Happy workflow designing! 🎬🤖
