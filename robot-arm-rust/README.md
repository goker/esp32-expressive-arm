# Robot Arm Controller - ESP32-C3 Rust

Smooth servo control for ESP32-C3 robot arm using Rust and esp-hal.

## Project Overview

This is an **ESP32-C3 embedded Rust project** that controls a 4-servo robot arm with smooth motion trajectories. It demonstrates:
- **Bare-metal Rust** (`#![no_std]`, `#![no_main]`)
- **ESP HAL** (Hardware Abstraction Layer)
- **PWM control** for servos using LEDC peripheral
- **Mathematical algorithms** (minimum jerk trajectories, exponential smoothing)

## Understanding the Code Structure

### Key Components

1. **No Standard Library (`#![no_std]`)**
   - Cannot use `std::` features (Vec, String, HashMap, etc.)
   - Must use `core::` primitives only
   - Uses `libm` for math functions (sin, cos, pow)

2. **Entry Point (`#[entry]`)**
   - `main()` is marked with `#[entry]` macro (not standard Rust `fn main()`)
   - Returns `!` (never type) because embedded systems run forever

3. **Hardware Abstraction**
   - `esp_hal` provides access to ESP32-C3 peripherals
   - LEDC (LED Control) peripheral repurposed for servo PWM
   - 4 GPIO pins (4, 5, 6, 7) control 4 servos

4. **Motion Algorithms**
   - **Minimum Jerk**: Creates smooth human-like motion with bell-curved velocity
   - **Exponential Smoothing**: Reduces servo jitter by blending positions

## Prerequisites

Before building, you need:

### 1. Rust Toolchain
```bash
# Check if Rust is installed
rustc --version
cargo --version

# If not installed:
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

### 2. ESP32 Rust Toolchain
```bash
# Install espup (ESP toolchain manager)
cargo install espup

# Install the ESP32 toolchain
espup install

# CRITICAL: Source the environment (do this every time in new terminal)
source ~/export-esp.sh

# Or add to your shell profile for persistence
echo 'source ~/export-esp.sh' >> ~/.zshrc  # or ~/.bashrc
```

### 3. RISC-V Target
```bash
# The ESP32-C3 uses a RISC-V processor
rustup target add riscv32imc-unknown-none-elf
```

### 4. Flash Tool
```bash
# Install espflash for uploading to hardware
cargo install espflash
```

## Building the Project

### Understanding the Build Process

1. **Cargo.toml** defines dependencies:
   - `esp-hal` (hardware abstraction)
   - `esp-backtrace` (panic handler)
   - `esp-println` (serial output)
   - `libm` (math functions for no_std)

2. **.cargo/config.toml** configures the build:
   - Sets target to `riscv32imc-unknown-none-elf`
   - Links with `riscv32-esp-elf-gcc`

3. **rust-toolchain.toml** forces nightly Rust:
   - Embedded features require unstable features
   - Pins to nightly channel

### Build Commands

```bash
# Development build (faster compile, larger binary, some optimizations)
cargo build

# Release build (optimized for size and speed)
cargo build --release
```

### What Happens During Build

1. **Cargo fetches dependencies** from crates.io
2. **Rust compiler** generates RISC-V machine code
3. **Linker** creates an ELF binary at:
   - Debug: `target/riscv32imc-unknown-none-elf/debug/robot-arm`
   - Release: `target/riscv32imc-unknown-none-elf/release/robot-arm`

### Understanding Build Output

```
   Compiling esp-hal v0.22.0
   Compiling robot-arm v0.1.0
    Finished release [optimized] target(s) in 45.2s
```

The binary is **NOT** a normal executable! It's firmware for ESP32-C3 hardware.

## Testing Without Hardware

**Important**: This code REQUIRES ESP32-C3 hardware. You cannot run it on your computer because:
- It's compiled for RISC-V architecture (not x86/ARM)
- It directly accesses ESP32-C3 hardware registers
- It's bare-metal (no operating system)

### What You Can Test

1. **Syntax and Type Checking**
```bash
cargo check
```

2. **Clippy Linting** (Rust's best-practice checker)
```bash
cargo clippy
```

3. **Code Review** - Understand what the code does:
   - Read through main.rs:60-403
   - Study the motion algorithms (minimum_jerk at line 45)
   - Trace servo control logic (angle_to_duty at line 54)

## Testing With Hardware

### Hardware Setup
| Servo    | GPIO | Function   |
|----------|------|------------|
| Base     | 4    | Rotation   |
| Shoulder | 5    | Up/Down    |
| Elbow    | 6    | Bend       |
| Gripper  | 7    | Open/Close |

Connect servo signal wires to these GPIO pins, and power servos separately (5V).

### Flashing to Hardware

```bash
# Build and flash in one command (easiest)
cargo run --release

# This will:
# 1. Build the release binary
# 2. Flash to ESP32-C3 via USB
# 3. Open serial monitor to see println! output
```

### Manual Flashing

```bash
# Build first
cargo build --release

# Flash with espflash
espflash flash --monitor target/riscv32imc-unknown-none-elf/release/robot-arm

# Specify port if needed
espflash flash --monitor -p /dev/cu.usbserial-1140 target/riscv32imc-unknown-none-elf/release/robot-arm
```

### Troubleshooting Flashing

**If upload fails:**
1. Hold **BOOT** button on ESP32-C3
2. Run flash command
3. Release BOOT after "Connecting..." appears

**Check connected devices:**
```bash
espflash board-info
```

## Learning Points for Rust

### 1. Ownership and Borrowing (lines 122-131)
```rust
let mut set_servo = |servo: usize, target: f32, channels: &mut [&mut dyn PwmChannel]| {
    // Closure captures `arm` by mutable reference
    arm.smooth_pos[servo] = ...
};
```
- Closures can capture variables from outer scope
- `&mut` means mutable borrow

### 2. Traits (lines 405-409)
```rust
trait PwmChannel {
    fn set_duty_hw(&mut self, duty: u32);
}
```
- Traits define shared behavior (like interfaces)
- Used for abstraction over different channel types

### 3. Type Conversions
```rust
let duty = roundf(duty) as u8;  // Explicit cast
let duty_value = ((duty as u32) * 16384 / 255) as u32;  // Multi-step conversion
```
- Rust requires explicit type conversions
- `as` keyword for primitive casts

### 4. No Standard Library
```rust
use libm::{cosf, sinf, powf, roundf};  // Can't use std::f32::cos!
```
- Embedded Rust can't use heap allocations
- Must use specialized libraries like `libm`

### 5. Error Handling
```rust
.configure(timer::config::Config { ... })
.unwrap();  // Panic if configuration fails
```
- `.unwrap()` extracts `Ok(value)` or panics on `Err`
- In embedded, panic calls `esp_backtrace` to print stack trace

### 6. Infinite Loops
```rust
loop {
    delay.delay_millis(1000u32);
}
```
- Embedded systems never exit
- Return type is `!` (never returns)

## What the Demo Does

When flashed, the robot arm automatically performs:

1. **Arm Circles** (10 circles)
   - Shoulder and elbow trace circular path
   - Demonstrates coordinated multi-servo motion

2. **Base Rotation**
   - Dramatic acceleration/deceleration sweeps
   - Shows minimum jerk trajectory in action

3. **Gripper Demo**
   - Snap open
   - Gentle grab (egg-holding simulation)
   - Quick release and catch
   - Pulsing grip (4 pulses)
   - Smooth release

## Next Steps for Learning

1. **Modify motion parameters**:
   - Change `SMOOTHING` constant (line 22)
   - Adjust circle radius (line 152)
   - Experiment with motion timing

2. **Add new motions**:
   - Create your own trajectory functions
   - Combine servo movements differently

3. **Study embedded Rust**:
   - Read the esp-hal documentation
   - Learn about RISC-V architecture
   - Understand PWM and servo control

4. **Compare with Python version**:
   - See how Rust's type safety prevents bugs
   - Notice the performance difference
   - Understand memory usage (no heap!)

## Common Build Issues

### "linker `riscv32-esp-elf-gcc` not found"
```bash
source ~/export-esp.sh
```

### "Permission denied" on serial port
```bash
# macOS - shouldn't need this usually
# Linux:
sudo usermod -a -G dialout $USER
# Then log out and back in
```

### Build fails with "esp-hal" errors
Make sure you're using nightly:
```bash
rustup override set nightly
rustup target add riscv32imc-unknown-none-elf
rustup component add rust-src
```

### "error: could not compile for target riscv32imc-unknown-none-elf"
```bash
rustup target add riscv32imc-unknown-none-elf
```

### Port busy
Make sure no other program (Arduino IDE, screen, etc.) is using the serial port.

### "esp-hal" version mismatch
Check that Cargo.toml dependencies match esp-hal version 0.22.

## Project Structure

```
robot-arm-rust/
├── Cargo.toml           # Dependencies
├── rust-toolchain.toml  # Rust nightly + target
├── .cargo/
│   └── config.toml      # Build config for ESP32-C3
└── src/
    └── main.rs          # Main code
```

## Key Algorithms

### Minimum Jerk Trajectory
```rust
fn minimum_jerk(t: f32) -> f32 {
    10.0 * t³ - 15.0 * t⁴ + 6.0 * t⁵
}
```
Creates human-like smooth motion with bell-shaped velocity profile.

### Exponential Smoothing
```rust
smooth_pos = smooth_pos * (1.0 - SMOOTHING) + target * SMOOTHING;
```
Reduces servo jitter by blending positions.

## Comparison with Python Version

| Feature | Python | Rust |
|---------|--------|------|
| Runtime | MicroPython interpreter | Native machine code |
| Speed | ~100x slower | Full speed |
| Size | Needs MicroPython firmware | ~100KB binary |
| Development | Quick iteration | Compile step |
| WiFi | Easy with sockets | Requires esp-wifi crate |

## Resources

- [Rust Embedded Book](https://rust-embedded.github.io/book/)
- [ESP Rust Documentation](https://docs.esp-rs.org/)
- [esp-hal Repository](https://github.com/esp-rs/esp-hal)
