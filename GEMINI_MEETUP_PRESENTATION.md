# Gemini in the Physical World: Simulation and Control
### By Gretchen Boria PhD. and Jorge Jimenez (Vibe Ops)

## 1. Project Overview
**"Ferri" Robot Arm Controller**
A dual-stack control system for a 4-axis robot arm (Base, Shoulder, Elbow, Gripper) running on an ESP32-C3 microcontroller.

*   **Core Goal:** Achieve human-like, smooth motion on cheap hardware ($5 hobby servos).
*   **Key Innovation:** Mathematical trajectory generation ("Minimum Jerk" polynomial) combined with exponential smoothing to eliminate servo jitter.
*   **Dual Architecture:**
    *   **MicroPython:** For rapid prototyping, interactive experimentation, and teaching.
    *   **Rust (Bare-Metal):** For high-performance, real-time control (100x faster).

---

## 2. Documentation (`docs/`)
We have documented the entire journey from Python script injection to bare-metal Rust.

*   **`COMPREHENSIVE_PORTING_GUIDE.md`**: The "Bible" of the project. It contains:
    *   **Full Code Listings**: Every line of the core Python and Rust implementations.
    *   **Deep Technical Dive**: How the "script injection" architecture works (Host -> Serial -> ESP32 Interpreter).
    *   **Math Explained**: Derivation of the quintic polynomial for smooth motion.
    *   **Pitfalls**: Lessons learned about USB cables, power supplies, and floating-point math on microcontrollers.
*   **`PORTING_GUIDE.md`**: A streamlined version focused on how to adapt this logic to other platforms (Arduino, Raspberry Pi Pico, STM32).
*   **`ROBOT_CONTROL_ARCHITECTURE.md`**: A high-level architectural manifesto proposing "Ferri" - a universal "Git for robot motion" that compiles YAML motion definitions into target-specific code (MicroPython, C++, ROS2 messages).

---

## 3. Examples (`examples/`)
Simple "smoke tests" to verify hardware before running complex algorithms.

*   **`led.py`**: Blinks the onboard LED to verify the microcontroller is alive and the interpreter is running.
*   **`simple.py`**: The "Hello World" of servos. Sets all motors to 90° (neutral) and holds. If this fails, it's a hardware/power issue.
*   **`test.py`**: A connection verifier that "wiggles" each servo individually to confirm wiring order and motor health.

---

## 4. Rust Implementation (`robot-arm-rust/`)
When MicroPython isn't fast enough, we switch to Rust.

*   **Bare-Metal Performance**: Runs directly on the hardware (no OS, no interpreter).
*   **`#![no_std]`**: Does not use the standard library, demonstrating embedded Rust best practices.
*   **ESP-HAL**: Uses the Hardware Abstraction Layer for direct register access to the LEDC (PWM) peripheral.
*   **Algorithms Ported**: Re-implements the exact same Minimum Jerk and Smoothing algorithms as the Python version, but runs them at **1000Hz** instead of 50Hz.

---

## 5. The Future: Simulation & The Feedback Loop
**Why we are building a Blender Simulation:**

*   **The Problem:** In physical robotics, the feedback loop is "broken" for an AI agent.
    *   When I (Gemini CLI) run a shell command, I see `stdout`/`stderr` and know exactly what happened.
    *   When I run a robot script, I send commands into a "black box." I don't know if the robot hit a wall, fell over, or succeeded.
*   **The Solution:** A physics-based simulation in Blender.
    *   **Visual Feedback:** The simulation renders the robot's movement.
    *   **Data Feedback:** We can capture collision data and joint angles.
*   **The Goal:**
    1.  Gemini generates robot code.
    2.  Code runs in Blender simulation.
    3.  Gemini analyzes the result (visuals/logs).
    4.  Gemini iterates and fixes the code *before* it ever touches physical hardware.

**This closes the loop**, allowing true agentic workflow in robotics.
