#!/usr/bin/env python3
"""
Test script for using Gemini 2.5 API to generate robot arm movement patterns.

Usage:
    python test_gemini_generator.py "Create a wave motion that moves all servos"

Set your API key:
    export GEMINI_API_KEY="your-api-key-here"
"""

import os
import sys
import json
import requests
from pathlib import Path


def load_instructions():
    """Load the AI agent instructions"""
    instructions_path = Path(__file__).parent / "AGENT_INSTRUCTIONS.md"
    with open(instructions_path, 'r') as f:
        return f.read()


def generate_movement_pattern(prompt, api_key=None):
    """
    Use Gemini 2.5 API to generate a movement pattern

    Args:
        prompt: Description of the movement pattern to generate
        api_key: Gemini API key (or uses GEMINI_API_KEY env var)

    Returns:
        Generated Python code as string
    """
    if api_key is None:
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable not set.\n"
                "Get your API key from: https://aistudio.google.com/app/apikey\n"
                "Set it with: export GEMINI_API_KEY='your-key-here'"
            )

    # Load instructions
    instructions = load_instructions()

    # Construct the full prompt
    full_prompt = f"""{instructions}

---

USER REQUEST: {prompt}

Remember: Return ONLY the executable Python code. No explanations, no markdown blocks, just the raw Python code.
"""

    # Gemini API endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"

    # Request payload
    payload = {
        "contents": [{
            "parts": [{
                "text": full_prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 8192,
        }
    }

    # Make request
    print(f"Requesting movement pattern from Gemini 2.5...")
    print(f"Prompt: {prompt}")
    print("-" * 60)

    response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})

    if response.status_code != 200:
        error_data = response.json()
        raise Exception(f"API Error {response.status_code}: {json.dumps(error_data, indent=2)}")

    # Extract generated text
    result = response.json()
    generated_code = result['candidates'][0]['content']['parts'][0]['text']

    # Clean up code (remove markdown if present despite instructions)
    if '```python' in generated_code:
        # Extract code from markdown block
        start = generated_code.find('```python') + 9
        end = generated_code.rfind('```')
        generated_code = generated_code[start:end].strip()
    elif '```' in generated_code:
        # Extract from generic code block
        start = generated_code.find('```') + 3
        end = generated_code.rfind('```')
        generated_code = generated_code[start:end].strip()

    return generated_code


def save_demo(code, output_file):
    """Save generated code to a file"""
    with open(output_file, 'w') as f:
        f.write(code)
    print(f"\nGenerated code saved to: {output_file}")

    # Make executable
    os.chmod(output_file, 0o755)
    print(f"Made executable: chmod +x {output_file}")


def validate_code(code):
    """Basic validation of generated code"""
    checks = {
        "Has shebang": code.startswith("#!/usr/bin/env python3"),
        "Has docstring": '"""' in code[:200],
        "Imports from utils": "from utils import" in code,
        "Has SERVO_HEADER": "SERVO_HEADER" in code,
        "Calls home()": "home()" in code,
        "Has main block": 'if __name__ == "__main__"' in code,
    }

    print("\nValidation Results:")
    print("-" * 60)
    all_passed = True
    for check, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"{status} {check}")
        if not passed:
            all_passed = False

    return all_passed


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nExample prompts:")
        print('  "Create a figure-8 motion pattern"')
        print('  "Make the arm do a dance with all servos"')
        print('  "Create a smooth reaching motion that grips"')
        print('  "Generate a spiral motion using shoulder and elbow"')
        sys.exit(1)

    prompt = " ".join(sys.argv[1:])

    try:
        # Generate code
        code = generate_movement_pattern(prompt)

        print("\n" + "=" * 60)
        print("GENERATED CODE:")
        print("=" * 60)
        print(code)
        print("=" * 60)

        # Validate
        is_valid = validate_code(code)

        # Save to file
        # Find next available demo number
        demos_dir = Path(__file__).parent.parent / "demos"
        existing_demos = list(demos_dir.glob("*.py"))
        demo_numbers = [int(f.stem.split("_")[0]) for f in existing_demos if f.stem[0].isdigit()]
        next_num = max(demo_numbers) + 1 if demo_numbers else 6

        output_file = demos_dir / f"{next_num:02d}_generated.py"
        save_demo(code, output_file)

        if is_valid:
            print("\n✓ Code validation passed!")
            print(f"\nTo run: python {output_file}")
        else:
            print("\n⚠ Some validation checks failed. Review code before running.")

    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
