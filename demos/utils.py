"""
Shared utilities for robot arm demos
"""

import subprocess
import sys
import glob

def find_port():
    """Auto-discover ESP32 serial port"""
    patterns = [
        '/dev/cu.usbserial-*',
        '/dev/cu.wchusbserial*',
        '/dev/cu.SLAB_USBtoUART*',
        '/dev/ttyUSB*',
        '/dev/ttyACM*',
    ]
    ports = []
    for pattern in patterns:
        ports.extend(glob.glob(pattern))

    if not ports:
        return None
    if len(ports) == 1:
        return ports[0]

    print("Multiple ports found:")
    for i, p in enumerate(ports):
        print(f"  {i+1}. {p}")
    choice = input("Enter number (or press Enter for first): ").strip()
    if choice == "":
        return ports[0]
    try:
        return ports[int(choice) - 1]
    except:
        return ports[0]

def run_on_esp32(micropython_code, port=None):
    """Send MicroPython code to ESP32 and run it"""
    if port is None:
        port = find_port()

    if port is None:
        print("ERROR: No USB serial port found!")
        print("\nMake sure:")
        print("  1. ESP32-C3 is plugged in via USB")
        print("  2. USB cable supports data (not charge-only)")
        sys.exit(1)

    print(f"Connected to: {port}\n")

    result = subprocess.run(
        [sys.executable, "-m", "mpremote", "connect", port, "exec", micropython_code],
        capture_output=False
    )

    if result.returncode != 0:
        print("\nError! Try:")
        print("  1. Close any program using the port")
        print("  2. Press RESET on ESP32")
        print("  3. Run: bash setup.sh")
        sys.exit(1)

# Shared MicroPython code header for servo control
SERVO_HEADER = '''
from machine import Pin, PWM
import time

# --- Core Setup ---
SERVO_PINS = [4, 5, 6, 7]
servos = [PWM(Pin(p), freq=50) for p in SERVO_PINS]
# Global state to track current smoothed positions
smooth_pos = [90.0, 90.0, 90.0, 90.0]
# Track last time each servo was moved (for watchdog)
last_move = [time.ticks_ms()] * 4

def watchdog_callback(t):
    """Automatically detaches servos that haven't moved in 10 seconds."""
    now = time.ticks_ms()
    for i in range(4):
        if time.ticks_diff(now, last_move[i]) > 10000:
            servos[i].duty(0)

# Start background watchdog (checks every second)
from machine import Timer
watchdog_timer = Timer(-1)
watchdog_timer.init(period=1000, mode=Timer.PERIODIC, callback=watchdog_callback)

# --- Low-Level Control ---

def angle_to_duty(angle):
    """Converts angle (0-180) to PWM duty cycle."""
    return int(round(26 + (angle / 180.0) * (128 - 26)))

def set_servo_direct(servo_num, angle):
    """Sets a servo to a specific angle immediately."""
    duty = angle_to_duty(angle)
    servos[servo_num].duty(duty)
    smooth_pos[servo_num] = float(angle)
    last_move[servo_num] = time.ticks_ms()

def stop_servo(servo_num):
    """Stops the PWM signal to a servo, allowing it to relax/detach."""
    servos[servo_num].duty(0)
    # Set timestamp to "way in the past" so watchdog doesn't fight it
    last_move[servo_num] = time.ticks_ms() - 20000

def minimum_jerk(t):
    """Calculates a smooth, human-like motion profile."""
    t2 = t * t
    t3 = t2 * t
    return 10 * t3 - 15 * t3 * t + 6 * t3 * t2

# --- NEW: State Machine Core Function ---

def move_servos_to(targets, duration):
    """
    Moves servos to target positions over a specified duration.
    This is a BLOCKING function. It will not return until the move is complete.
    `targets` is a dictionary like {0: 90, 1: 45}
    """
    global smooth_pos
    
    start_pos = {}
    for s_num in targets.keys():
        start_pos[s_num] = smooth_pos[s_num]
    
    steps = int(duration / 0.02) # Aim for a 50Hz update rate (20ms)
    if steps < 1:
        steps = 1
        
    for i in range(steps):
        t = (i + 1) / steps
        s = minimum_jerk(t)
        for s_num, target_angle in targets.items():
            start_angle = start_pos[s_num]
            current_angle = start_angle + (target_angle - start_angle) * s
            # Use a simplified, direct smoothing approach for this model
            set_servo_direct(s_num, current_angle) 
        time.sleep(0.02)
        
    # After the loop, guarantee the final position
    for s_num, target_angle in targets.items():
        set_servo_direct(s_num, target_angle)

# --- High-Level Action Library (State Machine Actions) ---

def home():
    print("Action: Homing arm...")
    # Move arm to neutral, but preserve current gripper state (servo 3)
    move_servos_to({0: 90, 1: 90, 2: 90}, 1.0)
    print("Homing complete.")

def reach_forward():
    print("Action: Reaching forward...")
    # Ensure base is centered when reaching forward
    move_servos_to({0: 90, 1: 30, 2: 140}, 1.5)
    print("Reach complete.")

def grip():
    print("Action: Gripping (Incremental)...")
    # We move in a few discrete steps until "pinzed"
    # This avoids the continuous hard driving of a single long move to 0
    # and keeps the torque on as requested.
    target_angles = [120, 80, 50]
    for angle in target_angles:
        move_servos_to({3: angle}, 0.3)
        time.sleep(0.1)
    print("Grip complete.")

def release():
    print("Action: Releasing...")
    # Re-engage is automatic when we set a new position
    move_servos_to({3: 180}, 0.75)
    print("Release complete.")
    
def lift():
    print("Action: Lifting...")
    move_servos_to({1: 50, 2: 120}, 1.0)
    print("Lift complete.")

# --- Initialization ---
print("Initializing servos to home position...")
home()
print("Initialization complete. Ready for commands.")
'''
