//! Robot Arm Controller for ESP32-C3
//!
//! Smooth servo control using minimum jerk trajectories
//! 4 servos: Base (GPIO4), Shoulder (GPIO5), Elbow (GPIO6), Gripper (GPIO7)

#![no_std]
#![no_main]

use esp_backtrace as _;
use esp_hal::{
    delay::Delay,
    gpio::{Level, Output},
    ledc::{channel, timer, LSGlobalClkSource, Ledc, LowSpeed},
    prelude::*,
};
use esp_println::println;
use libm::{cosf, powf, roundf, sinf};

// Servo configuration
const SERVO_PINS: [u8; 4] = [4, 5, 6, 7];
const HOME_POS: f32 = 90.0;
const SMOOTHING: f32 = 0.5;
const MIN_DUTY: f32 = 26.0;
const MAX_DUTY: f32 = 128.0;
const PI: f32 = 3.14159265;

/// Robot arm state
struct RobotArm {
    smooth_pos: [f32; 4],
    last_duty: [u8; 4],
}

impl RobotArm {
    fn new() -> Self {
        Self {
            smooth_pos: [HOME_POS; 4],
            last_duty: [0; 4],
        }
    }
}

/// Minimum jerk trajectory - creates human-like smooth motion
/// Input: t (0.0 to 1.0)
/// Output: position factor (0.0 to 1.0)
fn minimum_jerk(t: f32) -> f32 {
    let t2 = t * t;
    let t3 = t2 * t;
    let t4 = t3 * t;
    let t5 = t4 * t;
    10.0 * t3 - 15.0 * t4 + 6.0 * t5
}

/// Convert angle (0-180) to duty cycle
fn angle_to_duty(angle: f32) -> u8 {
    let duty = MIN_DUTY + (angle / 180.0) * (MAX_DUTY - MIN_DUTY);
    roundf(duty) as u8
}

#[entry]
fn main() -> ! {
    println!("\n=== ROBOT ARM CONTROLLER (Rust) ===\n");

    // Initialize peripherals
    let peripherals = esp_hal::init(esp_hal::Config::default());
    let delay = Delay::new();

    // Initialize LEDC for PWM
    let mut ledc = Ledc::new(peripherals.LEDC);
    ledc.set_global_slow_clock(LSGlobalClkSource::APBClk);

    // Configure timer for 50Hz (servo frequency)
    let mut timer0 = ledc.timer::<LowSpeed>(timer::Number::Timer0);
    timer0
        .configure(timer::config::Config {
            duty: timer::config::Duty::Duty14Bit,
            clock_source: timer::LSClockSource::APBClk,
            frequency: 50.Hz(),
        })
        .unwrap();

    // Configure channels for each servo
    let mut channel0 = ledc.channel(channel::Number::Channel0, peripherals.GPIO4);
    let mut channel1 = ledc.channel(channel::Number::Channel1, peripherals.GPIO5);
    let mut channel2 = ledc.channel(channel::Number::Channel2, peripherals.GPIO6);
    let mut channel3 = ledc.channel(channel::Number::Channel3, peripherals.GPIO7);

    channel0
        .configure(channel::config::Config {
            timer: &timer0,
            duty_pct: 0,
            pin_config: channel::config::PinConfig::PushPull,
        })
        .unwrap();
    channel1
        .configure(channel::config::Config {
            timer: &timer0,
            duty_pct: 0,
            pin_config: channel::config::PinConfig::PushPull,
        })
        .unwrap();
    channel2
        .configure(channel::config::Config {
            timer: &timer0,
            duty_pct: 0,
            pin_config: channel::config::PinConfig::PushPull,
        })
        .unwrap();
    channel3
        .configure(channel::config::Config {
            timer: &timer0,
            duty_pct: 0,
            pin_config: channel::config::PinConfig::PushPull,
        })
        .unwrap();

    println!("Servos initialized on GPIO 4, 5, 6, 7");

    // Robot arm state
    let mut arm = RobotArm::new();

    // Helper to set servo with smoothing
    let mut set_servo = |servo: usize, target: f32, channels: &mut [&mut dyn PwmChannel]| {
        arm.smooth_pos[servo] = arm.smooth_pos[servo] * (1.0 - SMOOTHING) + target * SMOOTHING;
        let duty = angle_to_duty(arm.smooth_pos[servo]);
        if duty != arm.last_duty[servo] {
            // Convert duty to percentage (14-bit = 16384 max)
            let duty_value = ((duty as u32) * 16384 / 255) as u32;
            channels[servo].set_duty_hw(duty_value);
            arm.last_duty[servo] = duty;
        }
    };

    // Go to home position
    println!("Moving to home position...");
    for _ in 0..50 {
        let duty = angle_to_duty(HOME_POS);
        let duty_value = ((duty as u32) * 16384 / 255) as u32;
        channel0.set_duty_hw(duty_value).unwrap();
        channel1.set_duty_hw(duty_value).unwrap();
        channel2.set_duty_hw(duty_value).unwrap();
        channel3.set_duty_hw(duty_value).unwrap();
        delay.delay_millis(20u32);
    }

    println!("\n=== SMOOTH MOTION DEMO ===\n");

    // ========================================
    // Part 1: Arm circles (shoulder + elbow)
    // ========================================
    println!("1. Arm circles...");

    let radius: f32 = 30.0;
    let points: u32 = 250;

    for _circle in 0..10 {
        for i in 0..points {
            let angle = (i as f32 / points as f32) * 2.0 * PI;

            let shoulder = 90.0 + radius * sinf(angle);
            let elbow = 90.0 + radius * cosf(angle);

            // Apply smoothing
            arm.smooth_pos[1] = arm.smooth_pos[1] * (1.0 - SMOOTHING) + shoulder * SMOOTHING;
            arm.smooth_pos[2] = arm.smooth_pos[2] * (1.0 - SMOOTHING) + elbow * SMOOTHING;

            let duty1 = angle_to_duty(arm.smooth_pos[1]);
            let duty2 = angle_to_duty(arm.smooth_pos[2]);

            if duty1 != arm.last_duty[1] {
                let duty_value = ((duty1 as u32) * 16384 / 255) as u32;
                channel1.set_duty_hw(duty_value).unwrap();
                arm.last_duty[1] = duty1;
            }
            if duty2 != arm.last_duty[2] {
                let duty_value = ((duty2 as u32) * 16384 / 255) as u32;
                channel2.set_duty_hw(duty_value).unwrap();
                arm.last_duty[2] = duty2;
            }

            delay.delay_millis(4u32);
        }
    }

    // Return to center
    for i in 0..100 {
        let t = i as f32 / 100.0;
        let s = minimum_jerk(t);

        let shoulder = arm.smooth_pos[1] + (90.0 - arm.smooth_pos[1]) * s;
        let elbow = arm.smooth_pos[2] + (90.0 - arm.smooth_pos[2]) * s;

        let duty1 = angle_to_duty(shoulder);
        let duty2 = angle_to_duty(elbow);

        let duty_value1 = ((duty1 as u32) * 16384 / 255) as u32;
        let duty_value2 = ((duty2 as u32) * 16384 / 255) as u32;

        channel1.set_duty_hw(duty_value1).unwrap();
        channel2.set_duty_hw(duty_value2).unwrap();

        arm.smooth_pos[1] = shoulder;
        arm.smooth_pos[2] = elbow;

        delay.delay_millis(4u32);
    }

    delay.delay_millis(300u32);

    // ========================================
    // Part 2: Base dramatic accel/decel
    // ========================================
    println!("2. Base rotation (dramatic accel/decel)...");

    // Sweep right: 90 -> 160
    let start = 90.0_f32;
    let end = 160.0_f32;
    for i in 0..300 {
        let t = i as f32 / 300.0;
        let s = minimum_jerk(t);
        let base = start + (end - start) * s;

        arm.smooth_pos[0] = arm.smooth_pos[0] * (1.0 - SMOOTHING) + base * SMOOTHING;
        let duty = angle_to_duty(arm.smooth_pos[0]);
        if duty != arm.last_duty[0] {
            let duty_value = ((duty as u32) * 16384 / 255) as u32;
            channel0.set_duty_hw(duty_value).unwrap();
            arm.last_duty[0] = duty;
        }
        delay.delay_millis(3u32);
    }

    delay.delay_millis(100u32);

    // Whip left: 160 -> 20
    let start = 160.0_f32;
    let end = 20.0_f32;
    for i in 0..300 {
        let t = i as f32 / 300.0;
        let s = minimum_jerk(t);
        let base = start + (end - start) * s;

        arm.smooth_pos[0] = arm.smooth_pos[0] * (1.0 - SMOOTHING) + base * SMOOTHING;
        let duty = angle_to_duty(arm.smooth_pos[0]);
        if duty != arm.last_duty[0] {
            let duty_value = ((duty as u32) * 16384 / 255) as u32;
            channel0.set_duty_hw(duty_value).unwrap();
            arm.last_duty[0] = duty;
        }
        delay.delay_millis(3u32);
    }

    delay.delay_millis(100u32);

    // Return to center: 20 -> 90
    let start = 20.0_f32;
    let end = 90.0_f32;
    for i in 0..200 {
        let t = i as f32 / 200.0;
        let s = minimum_jerk(t);
        let base = start + (end - start) * s;

        arm.smooth_pos[0] = arm.smooth_pos[0] * (1.0 - SMOOTHING) + base * SMOOTHING;
        let duty = angle_to_duty(arm.smooth_pos[0]);
        if duty != arm.last_duty[0] {
            let duty_value = ((duty as u32) * 16384 / 255) as u32;
            channel0.set_duty_hw(duty_value).unwrap();
            arm.last_duty[0] = duty;
        }
        delay.delay_millis(4u32);
    }

    delay.delay_millis(300u32);

    // ========================================
    // Part 3: Gripper movements
    // ========================================
    println!("3. Parallel gripper demo...");

    // Snap open
    println!("   - Snap open");
    for i in 0..80 {
        let t = i as f32 / 80.0;
        let s = powf(t, 0.3); // Fast start
        let gripper = 90.0 + (120.0 - 90.0) * s;

        arm.smooth_pos[3] = arm.smooth_pos[3] * (1.0 - SMOOTHING) + gripper * SMOOTHING;
        let duty = angle_to_duty(arm.smooth_pos[3]);
        if duty != arm.last_duty[3] {
            let duty_value = ((duty as u32) * 16384 / 255) as u32;
            channel3.set_duty_hw(duty_value).unwrap();
            arm.last_duty[3] = duty;
        }
        delay.delay_millis(3u32);
    }

    delay.delay_millis(200u32);

    // Gentle grab
    println!("   - Gentle grab");
    for i in 0..200 {
        let t = i as f32 / 200.0;
        let s = 1.0 - powf(1.0 - t, 0.4); // Fast then slow
        let gripper = 120.0 + (40.0 - 120.0) * s;

        arm.smooth_pos[3] = arm.smooth_pos[3] * (1.0 - SMOOTHING) + gripper * SMOOTHING;
        let duty = angle_to_duty(arm.smooth_pos[3]);
        if duty != arm.last_duty[3] {
            let duty_value = ((duty as u32) * 16384 / 255) as u32;
            channel3.set_duty_hw(duty_value).unwrap();
            arm.last_duty[3] = duty;
        }
        delay.delay_millis(5u32);
    }

    delay.delay_millis(300u32);

    // Quick release and catch
    println!("   - Quick release and catch");
    for i in 0..60 {
        let t = i as f32 / 60.0;
        let s = minimum_jerk(t);
        let gripper = 40.0 + (100.0 - 40.0) * s;

        let duty = angle_to_duty(gripper);
        let duty_value = ((duty as u32) * 16384 / 255) as u32;
        channel3.set_duty_hw(duty_value).unwrap();
        arm.smooth_pos[3] = gripper;
        delay.delay_millis(3u32);
    }

    delay.delay_millis(50u32);

    for i in 0..80 {
        let t = i as f32 / 80.0;
        let s = 1.0 - powf(1.0 - t, 0.5);
        let gripper = 100.0 + (45.0 - 100.0) * s;

        let duty = angle_to_duty(gripper);
        let duty_value = ((duty as u32) * 16384 / 255) as u32;
        channel3.set_duty_hw(duty_value).unwrap();
        arm.smooth_pos[3] = gripper;
        delay.delay_millis(4u32);
    }

    delay.delay_millis(200u32);

    // Pulsing grip
    println!("   - Pulsing grip");
    for _pulse in 0..4 {
        // Squeeze
        for i in 0..50 {
            let t = i as f32 / 50.0;
            let s = minimum_jerk(t);
            let gripper = 45.0 + (35.0 - 45.0) * s;

            let duty = angle_to_duty(gripper);
            let duty_value = ((duty as u32) * 16384 / 255) as u32;
            channel3.set_duty_hw(duty_value).unwrap();
            delay.delay_millis(4u32);
        }
        // Release slightly
        for i in 0..50 {
            let t = i as f32 / 50.0;
            let s = minimum_jerk(t);
            let gripper = 35.0 + (50.0 - 35.0) * s;

            let duty = angle_to_duty(gripper);
            let duty_value = ((duty as u32) * 16384 / 255) as u32;
            channel3.set_duty_hw(duty_value).unwrap();
            delay.delay_millis(4u32);
        }
    }

    delay.delay_millis(200u32);

    // Smooth release
    println!("   - Smooth release");
    for i in 0..150 {
        let t = i as f32 / 150.0;
        let s = minimum_jerk(t);
        let gripper = 50.0 + (90.0 - 50.0) * s;

        let duty = angle_to_duty(gripper);
        let duty_value = ((duty as u32) * 16384 / 255) as u32;
        channel3.set_duty_hw(duty_value).unwrap();
        delay.delay_millis(5u32);
    }

    // Return all to home
    let duty = angle_to_duty(90.0);
    let duty_value = ((duty as u32) * 16384 / 255) as u32;
    channel0.set_duty_hw(duty_value).unwrap();
    channel1.set_duty_hw(duty_value).unwrap();
    channel2.set_duty_hw(duty_value).unwrap();
    channel3.set_duty_hw(duty_value).unwrap();

    println!("\n=== Demo complete! ===");

    // Idle loop
    loop {
        delay.delay_millis(1000u32);
    }
}

/// Trait for PWM channel abstraction
trait PwmChannel {
    fn set_duty_hw(&mut self, duty: u32);
}
