# MicroPython code template - this gets sent to ESP32
# Gets formatted with: calibration data, waypoints, stage info

TEMPLATE = '''
from machine import Pin, PWM
import time

SERVO_PINS = [4, 5, 6, 7]
current_pos = [90, 90, 90, 90]

servos = []
for pin in SERVO_PINS:
    pwm = PWM(Pin(pin), freq=50)
    servos.append(pwm)

def angle_to_duty(angle):
    return int(round(26 + (angle / 180) * (128 - 26)))

def set_servo(servo_num, angle):
    duty = angle_to_duty(angle)
    servos[servo_num].duty(duty)
    current_pos[servo_num] = angle

# Calibration data
{calibration_code}

def move_to_position(target, duration):
    start = [current_pos[i] for i in range(4)]

    steps = int(duration / 0.05)
    if steps == 0:
        steps = 1

    for step in range(steps + 1):
        progress = step / steps
        smooth = 10 * (progress ** 3) - 15 * (progress ** 4) + 6 * (progress ** 5)

        for i in range(4):
            angle = start[i] + (target[i] - start[i]) * smooth
            calibrated = calibrated_angle(i, int(angle))
            set_servo(i, calibrated)

        time.sleep(0.05)

# Stage execution
print("\\n=== STAGE {stage_num}: {stage_name} ===\\n")
print(f"Starting from: {{current_pos}}")

{waypoint_commands}

print(f"\\nFinal position: {{current_pos}}")
print("=== COMPLETE ===")
'''
