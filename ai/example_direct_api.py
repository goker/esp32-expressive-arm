#!/usr/bin/env python3
"""
Simple example showing direct Gemini API usage for movement generation.

This is a minimal example you can adapt for your own integration.
"""

import os
import requests
import json


def generate_with_gemini(prompt, instructions_text, api_key):
    """
    Call Gemini API with instructions and user prompt

    Args:
        prompt: User's movement request
        instructions_text: The full AGENT_INSTRUCTIONS.md content
        api_key: Gemini API key

    Returns:
        Generated Python code
    """
    # Combine instructions with user prompt
    full_prompt = f"{instructions_text}\n\n---\n\nUSER REQUEST: {prompt}\n\nRemember: Return ONLY executable Python code."

    # API endpoint for Gemini 2.5
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"

    # Request payload
    payload = {
        "contents": [{
            "parts": [{"text": full_prompt}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 8192,
        }
    }

    # Make request
    response = requests.post(
        url,
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code != 200:
        raise Exception(f"API Error: {response.status_code}\n{response.text}")

    # Extract generated code
    result = response.json()
    code = result['candidates'][0]['content']['parts'][0]['text']

    # Clean up markdown if present
    if '```python' in code:
        start = code.find('```python') + 9
        end = code.rfind('```')
        code = code[start:end].strip()

    return code


# Example usage
if __name__ == "__main__":
    # Load instructions
    with open('AGENT_INSTRUCTIONS.md', 'r') as f:
        instructions = f.read()

    # Get API key
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("Error: Set GEMINI_API_KEY environment variable")
        print("Get key from: https://aistudio.google.com/app/apikey")
        exit(1)

    # Generate movement
    prompt = "Create a smooth wave motion across all servos"
    print(f"Generating: {prompt}")
    print("-" * 60)

    code = generate_with_gemini(prompt, instructions, api_key)

    print("Generated Code:")
    print("=" * 60)
    print(code)
    print("=" * 60)

    # Save to file
    with open('generated_demo.py', 'w') as f:
        f.write(code)

    print("\nSaved to: generated_demo.py")
