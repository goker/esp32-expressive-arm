#!/bin/bash
# Complete setup for Robot Arm WiFi Control
# Run this from a clean install to get everything working

FIRMWARE_URL="https://micropython.org/resources/firmware/ESP32_GENERIC_C3-20241129-v1.24.1.bin"
FIRMWARE_FILE="ESP32_GENERIC_C3-20241129-v1.24.1.bin"

echo "=========================================="
echo "   ROBOT ARM SETUP - ESP32-C3"
echo "=========================================="
echo ""

# Auto-discover port
PORT=$(ls /dev/cu.usbserial-* /dev/cu.wchusbserial* /dev/ttyUSB* 2>/dev/null | head -1)

if [ -z "$PORT" ]; then
    echo "ERROR: No USB serial port found!"
    echo ""
    echo "Make sure:"
    echo "  1. ESP32-C3 is plugged in via USB"
    echo "  2. USB cable supports data (not charge-only)"
    echo ""
    echo "Available ports:"
    ls /dev/cu.usb* 2>/dev/null || echo "  No USB ports found"
    exit 1
fi

echo "Found ESP32-C3 at $PORT"
echo ""

# Step 1: Install Python dependencies
echo "=== Step 1/5: Installing Python tools ==="
pip3 install esptool mpremote --quiet
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install Python tools"
    exit 1
fi
echo "Done!"
echo ""

# Step 2: Download MicroPython firmware
echo "=== Step 2/5: Downloading MicroPython firmware ==="
if [ -f "$FIRMWARE_FILE" ]; then
    echo "Firmware already downloaded, skipping..."
else
    curl -O "$FIRMWARE_URL"
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to download firmware"
        exit 1
    fi
fi
echo "Done!"
echo ""

# Step 3: Erase flash
echo "=== Step 3/5: Erasing ESP32-C3 flash ==="
echo "(If this fails, hold the BOOT button and try again)"
python3 -m esptool --chip esp32c3 --port $PORT erase_flash
if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Erase failed. Try:"
    echo "  1. Hold BOOT button on ESP32"
    echo "  2. Run this script again"
    exit 1
fi
echo "Done!"
echo ""

# Step 4: Flash MicroPython
echo "=== Step 4/5: Flashing MicroPython ==="
python3 -m esptool --chip esp32c3 --port $PORT --baud 460800 write_flash -z 0x0 $FIRMWARE_FILE
if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Flash failed. Try:"
    echo "  1. Hold BOOT button on ESP32"
    echo "  2. Run this script again"
    exit 1
fi
echo "Done!"
echo ""

# Step 5: Verify
echo "=== Step 5/5: Verifying installation ==="
sleep 2  # Wait for ESP32 to reboot
python3 -m esptool --chip esp32c3 --port $PORT chip_id
if [ $? -ne 0 ]; then
    echo "WARNING: Could not verify, but flash may have succeeded"
fi
echo ""

echo "=========================================="
echo "   SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "  1. Run the smooth demo (USB only):"
echo "     python3 robot_arm.py"
echo ""
echo "  2. Run WiFi control (wireless from phone/computer):"
echo "     python3 robot_arm_wifi.py"
echo ""
echo "  3. To wipe and start over:"
echo "     bash wipe.sh"
echo ""
