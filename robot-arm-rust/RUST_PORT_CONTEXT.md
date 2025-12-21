# Robot Arm Controller - Rust Port Context

This document contains all context needed to port the Python/MicroPython robot arm controller to Rust for ESP32-C3.

## Hardware

### Board
- **MCU**: ESP32-C3 (RISC-V single core, 160MHz)
- **Flash**: 4MB embedded
- **Connectivity**: WiFi 2.4GHz, BLE 5
- **USB**: USB-to-serial chip (not native USB JTAG)
- **Port**: `/dev/cu.usbserial-1140` (macOS)

### Servos (4 total)
| Index | Name     | GPIO | Function        | Range   |
|-------|----------|------|-----------------|---------|
| 0     | Base     | 4    | Rotation        | 0-180°  |
| 1     | Shoulder | 5    | Up/Down         | 30-150° |
| 2     | Elbow    | 6    | Bend            | 30-150° |
| 3     | Gripper  | 7    | Open/Close      | 30-120° |

### Servo PWM Specifications
- **Frequency**: 50Hz (20ms period)
- **Pulse width**: 0.5ms (0°) to 2.5ms (180°)
- **Duty cycle calculation**:
  ```
  min_duty = 26   (corresponds to ~0.5ms at 50Hz)
  max_duty = 128  (corresponds to ~2.5ms at 50Hz)
  duty = min_duty + (angle / 180) * (max_duty - min_duty)
  ```

## Core Algorithms

### 1. Minimum Jerk Trajectory
Creates human-like smooth motion with bell-shaped velocity profile.

```python
def minimum_jerk(t):
    """
    Input: t (0.0 to 1.0 normalized time)
    Output: position factor (0.0 to 1.0)

    Creates:
    - Zero velocity at start and end
    - Zero acceleration at start and end
    - Natural human-like motion
    """
    return 10 * (t ** 3) - 15 * (t ** 4) + 6 * (t ** 5)
```

**Rust equivalent:**
```rust
fn minimum_jerk(t: f32) -> f32 {
    let t2 = t * t;
    let t3 = t2 * t;
    let t4 = t3 * t;
    let t5 = t4 * t;
    10.0 * t3 - 15.0 * t4 + 6.0 * t5
}
```

### 2. Exponential Smoothing (Anti-Jitter)
Reduces servo jitter by smoothing position changes.

```python
SMOOTHING = 0.5  # 0.1 = very smooth, 0.5 = responsive
smooth_pos = [90.0, 90.0, 90.0, 90.0]

def set_servo_smooth(servo_num, target_angle):
    global smooth_pos, last_duty

    # Exponential moving average
    smooth_pos[servo_num] = smooth_pos[servo_num] * (1 - SMOOTHING) + target_angle * SMOOTHING

    duty = angle_to_duty(smooth_pos[servo_num])

    # Only update PWM if duty actually changed (reduces jitter)
    if duty != last_duty[servo_num]:
        servos[servo_num].duty(duty)
        last_duty[servo_num] = duty
```

### 3. Angle to Duty Cycle Conversion
```python
def angle_to_duty(angle: float) -> int:
    min_duty = 26
    max_duty = 128
    return int(round(min_duty + (angle / 180.0) * (max_duty - min_duty)))
```

**Rust equivalent:**
```rust
fn angle_to_duty(angle: f32) -> u32 {
    const MIN_DUTY: f32 = 26.0;
    const MAX_DUTY: f32 = 128.0;
    (MIN_DUTY + (angle / 180.0) * (MAX_DUTY - MIN_DUTY)).round() as u32
}
```

## Motion Patterns

### 1. Circular Motion (Arm)
Shoulder and elbow move together to trace circles.

```python
radius = 30  # degrees
points = 250
delay = 0.004  # 4ms between updates

for i in range(points):
    angle = (i / points) * 2 * math.pi

    shoulder = 90 + radius * math.sin(angle)
    elbow = 90 + radius * math.cos(angle)

    set_servo_smooth(1, shoulder)
    set_servo_smooth(2, elbow)

    time.sleep(delay)
```

### 2. Accel/Decel Motion (Base)
Uses minimum jerk for smooth start/stop.

```python
# Move from start to end with natural accel/decel
start = 90
end = 160
points = 300

for i in range(points):
    t = i / points  # 0.0 to 1.0
    s = minimum_jerk(t)
    position = start + (end - start) * s
    set_servo_smooth(0, position)
    time.sleep(0.003)
```

### 3. Gripper Curves

**Fast-then-slow (gentle grab):**
```python
# Square root curve: fast start, slow finish
s = 1 - (1 - t) ** 0.5
# or with exponent 0.4 for even gentler finish
s = 1 - (1 - t) ** 0.4
```

**Snap open (fast start):**
```python
s = t ** 0.3  # Power < 1 = fast start, gradual end
```

## Timing Guidelines

| Motion Type | Points | Delay (ms) | Total Time |
|-------------|--------|------------|------------|
| Circle      | 250    | 4          | 1.0s       |
| Base sweep  | 300    | 3          | 0.9s       |
| Gripper     | 80-200 | 3-6        | 0.3-1.0s   |

**Key insight**: Too slow = jitter (servo constantly micro-correcting). Use momentum - faster is often smoother.

## Rust Crate Recommendations

### For ESP32-C3
- `esp-hal` - Hardware abstraction layer
- `esp-wifi` - WiFi support
- `embassy-executor` - Async runtime (optional)
- `embedded-hal` - Traits for embedded systems

### PWM Setup (esp-hal example)
```rust
use esp_hal::{
    gpio::IO,
    ledc::{LEDC, LowSpeed, channel, timer},
    prelude::*,
};

// LEDC (LED Controller) is used for PWM on ESP32
let ledc = LEDC::new(peripherals.LEDC, &clocks);
let mut timer = ledc.get_timer::<LowSpeed>(timer::Number::Timer0);
timer.configure(timer::config::Config {
    duty: timer::config::Duty::Duty14Bit,
    clock_source: timer::LSClockSource::APBClk,
    frequency: 50.Hz(),  // 50Hz for servos
});

let mut channel = ledc.get_channel(channel::Number::Channel0, gpio4);
channel.configure(channel::config::Config {
    timer: &timer,
    duty_pct: 0,  // Will be set dynamically
});
```

### Delay
```rust
use esp_hal::delay::Delay;

let delay = Delay::new(&clocks);
delay.delay_millis(4u32);
```

## WiFi Web Server (Optional)

The Python version runs a web server on port 80 with:
- Sliders for each servo
- HOME, DEMO, WAVE buttons
- AJAX endpoints: `/move?s=0&a=90`, `/home`, `/demo`, `/wave`

For Rust, consider:
- `esp-wifi` + `smoltcp` for networking
- `picoserve` or custom HTTP handling
- Serve static HTML with embedded JavaScript

## State to Track

```rust
struct RobotArm {
    current_pos: [i32; 4],      // Current angles (integer)
    smooth_pos: [f32; 4],       // Smoothed positions (float)
    last_duty: [u32; 4],        // Last sent duty cycles (for jitter reduction)
}

impl Default for RobotArm {
    fn default() -> Self {
        Self {
            current_pos: [90, 90, 90, 90],
            smooth_pos: [90.0, 90.0, 90.0, 90.0],
            last_duty: [0, 0, 0, 0],
        }
    }
}
```

## Demo Sequence Summary

1. **Arm circles**: 10 circles at radius 30°, shoulder+elbow only
2. **Base rotation**: Sweep right (90→160), whip left (160→20), return center (20→90)
3. **Gripper moves**:
   - Snap open
   - Gentle grab (egg-like)
   - Quick release and catch
   - Pulsing grip (4 pulses)
   - Smooth release

## Key Constants

```rust
const SERVO_PINS: [u8; 4] = [4, 5, 6, 7];
const HOME_POS: [i32; 4] = [90, 90, 90, 90];
const SMOOTHING: f32 = 0.5;
const PWM_FREQ_HZ: u32 = 50;
const MIN_DUTY: u32 = 26;
const MAX_DUTY: u32 = 128;
```

## Files Reference

- `robot_arm.py` - Main USB demo with smooth_demo()
- `robot_arm_wifi.py` - WiFi web server version
- `setup.sh` - Flash MicroPython
- `wipe.sh` - Erase ESP32
