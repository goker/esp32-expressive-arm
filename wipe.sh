#!/bin/bash
# Wipe ESP32-C3 completely - erases all code and stops everything

echo "=== ESP32-C3 WIPE ==="
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

echo "Found port: $PORT"
echo "This will erase everything on the ESP32-C3."
echo ""

# Check if esptool is installed
if ! python3 -m esptool version &> /dev/null; then
    echo "Installing esptool..."
    pip3 install esptool
fi

echo "Erasing flash..."
python3 -m esptool --chip esp32c3 --port $PORT erase_flash

if [ $? -eq 0 ]; then
    echo ""
    echo "=== WIPE COMPLETE ==="
    echo "ESP32-C3 is now blank. To use it again, run:"
    echo "  bash setup.sh"
else
    echo ""
    echo "=== WIPE FAILED ==="
    echo "Try holding the BOOT button while running this script."
fi
