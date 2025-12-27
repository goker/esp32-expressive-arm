# Project Restart Context: Robot Arm Control

## Current Goal
The primary objective is to establish a reliable, state-machine-like control system for the robot arm. This involves moving from low-level, time-based scripting to a high-level, blocking function interface for robot actions, improving robustness and reducing errors.

## Architectural Changes Implemented (and Intended)

### 1. `demos/utils.py` (The Robot Control Library)
*   **Intention:** To encapsulate all low-level servo control, smoothing, and timing logic into a set of robust, blocking functions. The AI should *not* generate this low-level code directly.
*   **Changes Made:**
    *   **`move_servos_to(targets, duration)` function:** Introduced as the core motion primitive. It takes a dictionary of target servo angles and a duration, then smoothly moves the specified servos using `minimum_jerk` interpolation. This function is designed to be **blocking**, meaning it returns only when the movement is physically complete.
    *   **High-level action functions:** Created `home()`, `reach_forward()`, `grip()`, `release()`, and `lift()`. These are built on `move_servos_to()` and are intended to be the *only* functions the AI calls for robot movements. These are also blocking.
    *   **MicroPython compatibility fixes:**
        *   Modified `minimum_jerk` to use `t*t*t` instead of `t**3` etc., for broader MicroPython compatibility.
        *   Replaced a dictionary comprehension with a `for` loop in `move_servos_to` for MicroPython compatibility.

### 2. `ai/AGENT_INSTRUCTIONS.md` (AI's Directive)
*   **Intention:** To drastically simplify the AI's role. It should no longer generate complex motion loops or timing. Instead, it should translate user requests directly into a sequence of calls to the high-level blocking functions defined in `demos/utils.py`.
*   **Changes Made:** The instructions were largely rewritten to:
    *   Strictly enforce the use of *only* the pre-defined high-level action functions.
    *   Forbid writing custom functions, loops, variables, or low-level motion logic.
    *   Provide a minimal example demonstrating how to call `reach_forward()`, `grip()`, `lift()`, `release()`, and `home()` sequentially.

### 3. `robot-arm-rust/src/main.rs` (Main Application Logic)
*   **Intention:** To provide the CLI interface for the robot control, including an interactive voice mode.
*   **Changes Made:**
    *   **Optional subcommand:** Modified `Opts` struct to allow `abel` to run without subcommands, defaulting to the interactive mode.
    *   **Interactive Voice Mode:** Implemented a loop that greets the user, records input (via Whisper), sends it to Gemini for script generation, executes the script, and speaks back (via Deepgram TTS).
    *   **Environment Variable Integration:** Ensures `GEMINI_API_KEY` and `DEEPGRAM_API_KEY` are used.
    *   **Path Corrections:** Adjusted internal file paths (`AGENT_INSTRUCTIONS.md`, `demos` directory) to be relative to the project root.
    *   **Python Interpreter Specification:** Ensured generated Python scripts are executed using the project's virtual environment (`.venv/bin/python`).
    *   **Gemini Prompt Enhancement:** Added explicit instructions to the Gemini prompt for smoother movements and proper gripper timing.
    *   **Exit Command:** Added "no" (case-insensitive) as an exit command for the interactive session.
    *   **TLS Backend:** Switched `reqwest` to use `rustls-tls` to resolve "bad MAC" errors.

## Current Problem & Last Attempt

The most recent issue is a persistent `SyntaxError: invalid syntax` when running `test_pick_up.py` (which uses the `SERVO_HEADER` from `demos/utils.py`) on the ESP32 via `mpremote`.

My last attempt was to replace a dictionary comprehension within `move_servos_to` (in `demos/utils.py`) with a standard `for` loop, as dictionary comprehensions are known to cause `SyntaxError` in some MicroPython versions. This fix **did not resolve the error**, meaning there's another, or multiple, MicroPython syntax incompatibilities within the `SERVO_HEADER` content.

## Next Steps (After CLI Restart)

1.  **Thorough MicroPython Syntax Review of `demos/utils.py`:** The highest priority is to meticulously go through the entire `SERVO_HEADER` block in `demos/utils.py` and identify *any and all* Python syntax that might not be compatible with the specific MicroPython version running on the ESP32. This might include:
    *   `f-strings` (if used, replace with `.format()`)
    *   Tuple unpacking in loops (if used, replace with explicit indexing)
    *   Any advanced Python 3 features.
    *   The `move_servos_to` function itself might have subtle issues.
2.  **Isolated Testing:** Continue using `test_pick_up.py` from the project root.
3.  **Validate `ai/AGENT_INSTRUCTIONS.md`:** Once `demos/utils.py` is stable and working correctly, verify that `ai/AGENT_INSTRUCTIONS.md` is strictly enforcing the use of the new high-level blocking functions and contains no contradictory advice.
4.  **Re-test Gemini Integration:** Only after the underlying robot control is solid should we re-engage Gemini to ensure it generates correct scripts using the new high-level actions.
