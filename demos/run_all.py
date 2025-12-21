#!/usr/bin/env python3
"""
Run all demos in sequence
"""

import subprocess
import sys
import time

DEMOS = [
    ("01_test_servos.py", "Test Servos"),
    ("02_arm_circles.py", "Arm Circles"),
    ("03_base_rotation.py", "Base Rotation"),
    ("04_gripper_moves.py", "Gripper Moves"),
    ("05_wave_motion.py", "Wave Motion"),
]

def main():
    print("=" * 40)
    print("   ROBOT ARM - ALL DEMOS")
    print("=" * 40)
    print()

    for i, (script, name) in enumerate(DEMOS):
        print(f"\n[{i+1}/{len(DEMOS)}] {name}")
        print("-" * 30)

        result = subprocess.run([sys.executable, script])

        if result.returncode != 0:
            print(f"\nDemo {script} failed!")
            sys.exit(1)

        if i < len(DEMOS) - 1:
            print("\nNext demo in 2 seconds...")
            time.sleep(2)

    print("\n" + "=" * 40)
    print("   ALL DEMOS COMPLETE!")
    print("=" * 40)

if __name__ == "__main__":
    main()
