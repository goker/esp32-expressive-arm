#!/usr/bin/env python3
"""
Smoke Test - Quick connectivity check for ESP32-C3 robot arm
Tests connection without moving servos
"""

import subprocess
import sys
import glob

def find_port():
    """Search for ESP32 USB serial port"""
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
    return ports[0] if ports else None

# Minimal test code - just ping the device and check it responds
TEST_CODE = '''
import sys
print("PING_OK")
print(f"MicroPython version: {sys.version}")
print("Device is responsive!")
'''

def main():
    print("╔════════════════════════════════════╗")
    print("║  ESP32-C3 ROBOT ARM SMOKE TEST     ║")
    print("╚════════════════════════════════════╝\n")

    # Step 1: Check for USB port
    print("[1/3] Checking USB connection...", end=" ")
    port = find_port()

    if not port:
        print("❌ FAILED")
        print("\n⚠️  No USB serial port found!")
        print("\nPossible issues:")
        print("  • ESP32 not plugged in")
        print("  • USB cable is charge-only (need data cable)")
        print("  • Device not recognized by computer")
        print("\nTry:")
        print("  1. Unplug and replug the USB cable")
        print("  2. Try a different USB cable")
        print("  3. Check: ls /dev/cu.usb*")
        sys.exit(1)

    print(f"✓ Found: {port}")

    # Step 2: Test connection to ESP32
    print("[2/3] Testing ESP32 connection...", end=" ", flush=True)

    try:
        result = subprocess.run(
            ["mpremote", "connect", port, "exec", TEST_CODE],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0 or "PING_OK" not in result.stdout:
            print("❌ FAILED")
            print("\n⚠️  Device found but not responding!")
            print("\nPossible issues:")
            print("  • Device is OFF or out of battery")
            print("  • MicroPython not installed")
            print("  • Device in bootloader mode")
            print("\nTry:")
            print("  1. Check power switch is ON")
            print("  2. Press RESET button on ESP32")
            print("  3. Run: bash setup.sh (flash MicroPython)")
            print(f"\nError output:\n{result.stderr}")
            sys.exit(1)

        print("✓ Device responding")

    except subprocess.TimeoutExpired:
        print("❌ TIMEOUT")
        print("\n⚠️  Device not responding (timeout)")
        print("\nPossible issues:")
        print("  • Device is OFF or out of battery")
        print("  • Device frozen or crashed")
        print("\nTry:")
        print("  1. Check power switch is ON")
        print("  2. Press RESET button on ESP32")
        sys.exit(1)

    except FileNotFoundError:
        print("❌ FAILED")
        print("\n⚠️  'mpremote' command not found!")
        print("\nSetup required:")
        print("  pip install mpremote")
        sys.exit(1)

    # Step 3: Show device info
    print("[3/3] Getting device info...", end=" ", flush=True)

    # Extract version info from output
    lines = result.stdout.strip().split('\n')
    version_line = next((l for l in lines if 'MicroPython version' in l), None)

    print("✓")
    if version_line:
        print(f"\n  {version_line}")

    # Success!
    print("\n" + "="*40)
    print("✅ ALL CHECKS PASSED")
    print("="*40)
    print("\nYour device is:")
    print("  • Connected via USB")
    print("  • Powered ON")
    print("  • Running MicroPython")
    print("  • Ready to receive commands")
    print("\nYou can now run robot code!")
    print("\nNext steps:")
    print("  cd demos")
    print("  python3 01_test_servos.py")

if __name__ == "__main__":
    main()
