#!/bin/bash
# Setup script for ESP32-C3 Rust development

echo "=== Robot Arm Rust Setup ==="
echo ""

# Check if Rust is installed
if ! command -v rustc &> /dev/null; then
    echo "Installing Rust..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
else
    echo "Rust already installed: $(rustc --version)"
fi

# Install espup if not present
if ! command -v espup &> /dev/null; then
    echo ""
    echo "Installing espup (ESP Rust toolchain manager)..."
    cargo install espup
fi

# Install ESP toolchain
echo ""
echo "Installing ESP32 Rust toolchain..."
espup install

# Source the ESP environment
if [ -f ~/export-esp.sh ]; then
    source ~/export-esp.sh
fi

# Install espflash
if ! command -v espflash &> /dev/null; then
    echo ""
    echo "Installing espflash..."
    cargo install espflash
fi

# Add RISC-V target
echo ""
echo "Adding RISC-V target..."
rustup target add riscv32imc-unknown-none-elf

# Set nightly
echo ""
echo "Setting nightly toolchain..."
rustup override set nightly
rustup component add rust-src

echo ""
echo "=== Setup complete! ==="
echo ""
echo "To build and flash:"
echo "  cd robot-arm-rust"
echo "  source ~/export-esp.sh"
echo "  cargo run --release"
echo ""
echo "If using a new terminal, always run first:"
echo "  source ~/export-esp.sh"
