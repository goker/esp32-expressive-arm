# AI Movement Pattern Generator

This directory contains instructions and tools for using AI (Gemini 2.5) to generate robot arm movement patterns.

## Files

- **AGENT_INSTRUCTIONS.md** - Complete instructions for AI agents to generate movement code
- **test_gemini_generator.py** - Test script that uses Gemini API to generate demos
- **README.md** - This file

## Quick Start

### 1. Get Gemini API Key

Get your free API key from: https://aistudio.google.com/app/apikey

### 2. Set Environment Variable

```bash
export GEMINI_API_KEY="your-api-key-here"
```

Or add to your `~/.bashrc` or `~/.zshrc`:
```bash
echo 'export GEMINI_API_KEY="your-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### 3. Generate a Movement Pattern

```bash
python ai/test_gemini_generator.py "Create a figure-8 motion pattern"
```

The script will:
1. Load the agent instructions
2. Send your prompt to Gemini 2.5
3. Receive generated Python code
4. Validate the code
5. Save it as `demos/XX_generated.py`
6. Make it executable

### 4. Run the Generated Demo

```bash
python demos/06_generated.py
```

## Example Prompts

```bash
# Simple motions
python ai/test_gemini_generator.py "Create a wave motion"
python ai/test_gemini_generator.py "Make the arm do a picking motion"

# Complex patterns
python ai/test_gemini_generator.py "Create a spiral motion using shoulder and elbow"
python ai/test_gemini_generator.py "Generate a dance routine with all servos"

# Coordinated motions
python ai/test_gemini_generator.py "Create a figure-8 pattern"
python ai/test_gemini_generator.py "Make smooth reaching and gripping motion"
```

## Using with Other AI Models

The `AGENT_INSTRUCTIONS.md` file can be used with any AI model:

### Claude (via API or CLI)
```python
import anthropic

client = anthropic.Anthropic(api_key="your-key")
with open("ai/AGENT_INSTRUCTIONS.md") as f:
    instructions = f.read()

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=8192,
    messages=[{
        "role": "user",
        "content": f"{instructions}\n\nCreate a wave motion pattern"
    }]
)
print(message.content[0].text)
```

### OpenAI GPT-4
```python
from openai import OpenAI

client = OpenAI(api_key="your-key")
with open("ai/AGENT_INSTRUCTIONS.md") as f:
    instructions = f.read()

response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[
        {"role": "system", "content": instructions},
        {"role": "user", "content": "Create a wave motion pattern"}
    ]
)
print(response.choices[0].message.content)
```

## Servo Calibration Limits

The AI is instructed to respect these hardware limits:

```json
{
  "base": {"min": 0, "max": 180, "default": 63},
  "shoulder": {"min": 1, "max": 121, "default": 60},
  "elbow": {"min": 0, "max": 152, "default": 100},
  "gripper": {"min": 80, "max": 180, "default": 90}
}
```

## Troubleshooting

### API Key Issues
```bash
# Check if key is set
echo $GEMINI_API_KEY

# If empty, set it
export GEMINI_API_KEY="your-key-here"
```

### Generated Code Has Issues
The script includes validation checks. If validation fails:
1. Review the generated code in `demos/XX_generated.py`
2. Manually edit if needed
3. Try a more specific prompt
4. Check that calibration limits are respected

### Gemini API Errors
- **403 Forbidden**: API key is invalid or expired
- **429 Too Many Requests**: Rate limit exceeded, wait a moment
- **500 Server Error**: Gemini service issue, try again

### Code Won't Run
1. Make sure you're in the project root directory
2. Check that `demos/utils.py` exists
3. Verify ESP32 is connected: `ls /dev/cu.usbserial-*`
4. Test with existing demos first: `python demos/01_test_servos.py`

## Modifying Instructions

To customize how the AI generates code, edit `AGENT_INSTRUCTIONS.md`:

- Change motion style preferences
- Add new example patterns
- Adjust servo limits
- Add safety constraints
- Include additional helper functions

The instructions are structured to ensure the AI:
1. Returns only executable code (no explanations)
2. Follows the exact demo structure
3. Respects hardware limits
4. Uses smooth motion functions
5. Always returns to home position

## Integration Ideas

- Create a web UI that calls the generator
- Build a library of AI-generated movements
- Use voice commands to generate motions
- Chain multiple generated demos together
- Create a feedback loop to refine movements

## Cost Considerations

Gemini 2.5 Flash is very cost-effective:
- Free tier: 15 requests per minute
- Each request generates a complete demo (~1-2KB of code)
- Instructions file is ~10KB, included in each request

Expected cost: Essentially free for development and testing.
