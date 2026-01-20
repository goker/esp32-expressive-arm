#!/usr/bin/env python3
"""
Gemini Expressive Controller

Uses Gemini AI to interpret natural language and emotional context,
then generates appropriate expressive gestures for the robot arm.

Usage:
    python gemini_expressive.py "Say hello to my friend"
    python gemini_expressive.py "Show me you're happy"
    python gemini_expressive.py "React surprised then wave"

Environment:
    export GEMINI_API_KEY="your-api-key"
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import List, Dict, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from expressive.gestures import (
    Gesture, Keyframe, Emotion, get_gesture, list_gestures,
    get_gesture_for_emotion, GESTURE_REGISTRY
)


# Gemini prompt for interpreting emotional intent
EXPRESSIVE_AGENT_PROMPT = """You are an expressive robot arm controller. Your job is to interpret what the user wants the robot arm to express emotionally, then select appropriate gestures.

## Available Gestures

You can use these gestures (call them by name):

GREETINGS & SOCIAL:
- wave_friendly: Friendly wave greeting
- wave_excited: Enthusiastic excited wave
- salute: Respectful military salute
- bow: Respectful bowing motion
- beckoning: "Come here" gesture

RESPONSES:
- nod_yes: Nodding agreement
- shake_no: Shaking disagreement
- shrug: "I don't know" shrug
- point_forward: Pointing at something
- thinking: Thoughtful pondering pose

EMOTIONS:
- excited_bounce: Happy bouncing up and down
- celebrate: Victory arm pump
- sad_droop: Sad drooping posture
- surprised: Startled reaction
- angry_shake: Angry fist shaking
- shy_retreat: Timid retreating motion
- curious_look: Examining something curiously
- tired_stretch: Tired stretching

FUN:
- dance_groove: Fun dancing motion

UTILITY:
- home: Return to neutral position

## Response Format

Return a JSON object with:
1. "interpretation": Brief explanation of what emotion/intent you detected
2. "gestures": Array of gesture objects to execute in sequence

Each gesture object has:
- "name": gesture name from the list above
- "speed": speed multiplier (0.5=slow, 1.0=normal, 1.5=fast, 2.0=very fast)
- "repetitions": how many times to repeat (1-3)

## Examples

User: "Greet my friend warmly"
Response:
{
  "interpretation": "Friendly greeting - warm and welcoming",
  "gestures": [
    {"name": "wave_friendly", "speed": 1.0, "repetitions": 1}
  ]
}

User: "Show excitement then calm down"
Response:
{
  "interpretation": "Excitement transitioning to calm",
  "gestures": [
    {"name": "excited_bounce", "speed": 1.3, "repetitions": 2},
    {"name": "home", "speed": 0.7, "repetitions": 1}
  ]
}

User: "React like you just heard surprising news"
Response:
{
  "interpretation": "Surprised reaction to news",
  "gestures": [
    {"name": "surprised", "speed": 1.2, "repetitions": 1},
    {"name": "thinking", "speed": 0.8, "repetitions": 1}
  ]
}

User: "Say no firmly"
Response:
{
  "interpretation": "Firm disagreement/refusal",
  "gestures": [
    {"name": "shake_no", "speed": 1.2, "repetitions": 2}
  ]
}

## Rules

1. Return ONLY valid JSON, no other text
2. Use only gestures from the list above
3. Chain multiple gestures for complex expressions
4. Adjust speed based on emotion intensity (excited=faster, sad=slower)
5. Keep sequences to 1-4 gestures maximum
6. Always consider the emotional context
"""


def interpret_with_gemini(user_request: str, api_key: Optional[str] = None) -> Dict:
    """
    Use Gemini to interpret the user's request and select gestures.

    Returns:
        Dict with 'interpretation' and 'gestures' list
    """
    if api_key is None:
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not set.\n"
                "Get your key from: https://aistudio.google.com/app/apikey\n"
                "Set with: export GEMINI_API_KEY='your-key'"
            )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"

    full_prompt = f"""{EXPRESSIVE_AGENT_PROMPT}

---

USER REQUEST: {user_request}

Return only the JSON response:"""

    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 1024,
        }
    }

    print(f"Interpreting: \"{user_request}\"")
    print("-" * 50)

    response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})

    if response.status_code != 200:
        raise Exception(f"API Error {response.status_code}: {response.text}")

    result = response.json()
    generated_text = result['candidates'][0]['content']['parts'][0]['text']

    # Clean up response (remove markdown if present)
    if '```json' in generated_text:
        start = generated_text.find('```json') + 7
        end = generated_text.rfind('```')
        generated_text = generated_text[start:end].strip()
    elif '```' in generated_text:
        start = generated_text.find('```') + 3
        end = generated_text.rfind('```')
        generated_text = generated_text[start:end].strip()

    try:
        return json.loads(generated_text)
    except json.JSONDecodeError as e:
        print(f"Failed to parse response: {generated_text}")
        raise ValueError(f"Invalid JSON from Gemini: {e}")


def generate_micropython_code(gestures_data: List[Dict]) -> str:
    """
    Generate MicroPython code to execute the gesture sequence.
    """
    code_parts = []

    # Header with servo setup
    code_parts.append('''
from machine import Pin, PWM
import time
import math

# Servo setup
SERVO_PINS = [4, 5, 6, 7]
servos = []
smooth_pos = [90.0, 90.0, 90.0, 90.0]

for pin in SERVO_PINS:
    pwm = PWM(Pin(pin), freq=50)
    servos.append(pwm)

def angle_to_duty(angle):
    """Convert angle to PWM duty cycle"""
    return int(round(26 + (angle / 180) * (128 - 26)))

def minimum_jerk(t):
    """Minimum jerk trajectory for smooth motion"""
    return 10 * (t ** 3) - 15 * (t ** 4) + 6 * (t ** 5)

def set_servo(servo_num, angle):
    """Set servo with exponential smoothing"""
    global smooth_pos
    angle = max(0, min(180, angle))
    smooth_pos[servo_num] = smooth_pos[servo_num] * 0.5 + angle * 0.5
    duty = angle_to_duty(smooth_pos[servo_num])
    servos[servo_num].duty(duty)

def move_to(base, shoulder, elbow, gripper, duration=0.5, speed=1.0):
    """Move all servos smoothly to target position"""
    actual_duration = duration / speed
    steps = max(int(actual_duration / 0.02), 10)

    start = [smooth_pos[i] for i in range(4)]
    target = [base, shoulder, elbow, gripper]

    for step in range(steps + 1):
        t = step / steps
        s = minimum_jerk(t)

        for i in range(4):
            pos = start[i] + (target[i] - start[i]) * s
            set_servo(i, pos)

        time.sleep(actual_duration / steps)

def home():
    """Return to home position"""
    move_to(90, 90, 90, 60, duration=0.8)

print("\\n=== Expressive Gesture Sequence ===\\n")
''')

    # Generate code for each gesture
    for gesture_info in gestures_data:
        gesture_name = gesture_info.get("name", "home")
        speed = gesture_info.get("speed", 1.0)
        reps = gesture_info.get("repetitions", 1)

        gesture = get_gesture(gesture_name)
        if gesture is None:
            print(f"Warning: Unknown gesture '{gesture_name}', skipping")
            continue

        code_parts.append(f'\nprint("Gesture: {gesture.name} ({gesture.description})")')

        for rep in range(reps):
            if reps > 1:
                code_parts.append(f'print("  Repetition {rep + 1}/{reps}")')

            for kf in gesture.keyframes:
                adjusted_duration = kf.duration / (speed * gesture.speed_multiplier)
                code_parts.append(
                    f'move_to({kf.base}, {kf.shoulder}, {kf.elbow}, {kf.gripper}, '
                    f'duration={adjusted_duration:.3f}, speed=1.0)'
                )

        if gesture.return_home:
            code_parts.append('time.sleep(0.2)')

    # Return home at end
    code_parts.append('''
print("\\nReturning home...")
home()
print("\\n=== Sequence complete! ===")
''')

    return '\n'.join(code_parts)


def execute_on_robot(micropython_code: str):
    """Execute the generated code on the ESP32 robot"""
    import subprocess

    # Find port
    demos_dir = Path(__file__).parent.parent / "demos"
    sys.path.insert(0, str(demos_dir))
    from utils import find_port

    port = find_port()
    if not port:
        raise Exception("No ESP32 found! Check USB connection.")

    print(f"\nExecuting on {port}...")
    print("-" * 50)

    result = subprocess.run(
        ["mpremote", "connect", port, "exec", micropython_code],
        capture_output=False
    )

    return result.returncode == 0


def express(user_request: str, execute: bool = True) -> Dict:
    """
    Main function: interpret user request and optionally execute gestures.

    Args:
        user_request: Natural language description of what to express
        execute: Whether to execute on the physical robot

    Returns:
        Dict with interpretation and gesture sequence
    """
    # Get Gemini interpretation
    result = interpret_with_gemini(user_request)

    print(f"\nInterpretation: {result.get('interpretation', 'N/A')}")
    print(f"Gestures: {[g['name'] for g in result.get('gestures', [])]}")

    if execute:
        # Generate and execute code
        code = generate_micropython_code(result.get('gestures', []))

        print("\n" + "=" * 50)
        print("Generated MicroPython code:")
        print("=" * 50)
        print(code[:500] + "..." if len(code) > 500 else code)
        print("=" * 50)

        success = execute_on_robot(code)
        result['executed'] = success

    return result


def interactive_mode():
    """Run in interactive mode for continuous conversation"""
    print("\n" + "=" * 60)
    print("  Expressive Robot Arm - Interactive Mode")
    print("=" * 60)
    print("\nTell me what to express! Examples:")
    print("  - 'Wave hello to everyone'")
    print("  - 'Show that you're thinking hard'")
    print("  - 'React surprised then happy'")
    print("  - 'Do a little dance'")
    print("\nType 'quit' to exit, 'list' to see gestures\n")

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            if user_input.lower() == 'quit':
                print("Goodbye!")
                break

            if user_input.lower() == 'list':
                print("\nAvailable gestures:")
                for name in sorted(set(GESTURE_REGISTRY.keys())):
                    gesture = get_gesture(name)
                    if gesture:
                        print(f"  - {name}: {gesture.description}")
                continue

            express(user_input)

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    if len(sys.argv) < 2:
        # Interactive mode
        interactive_mode()
    else:
        # Single command mode
        user_request = " ".join(sys.argv[1:])
        express(user_request)


if __name__ == "__main__":
    main()
