#!/usr/bin/env bash

# Strict mode
set -euo pipefail

source ./bash_libs/log.sh

function main() {
    # Setup venv if not exists
    if [ ! -d ".venv" ]; then
        print_header "SETUP VENV"
        run_command \
          "python3 -m venv .venv" \
          "Creating python3 venv succeed!" \
          "Creating python3 venv failed"
    fi

    # Activate venv
    source .venv/bin/activate

    # Install build if not installed
    if ! python3 -c "import build" &> /dev/null; then
        run_command \
          "pip install build" \
          "Installing build pip package succeed!" \
          "Installing build pip package failed"
    fi

    print_header "RUN BUILD"
    run_command \
        "python3 -m build" \
        "Build completed successfully" \
        "Build failed"

    local latest_whl
    latest_whl=$(find dist/*.whl | sort -V | tail -n 1)
    color_echo "$GREEN_COLOR_CODE" "Found wheel file: $latest_whl"

    print_header "INSTALL PACKAGE"
    run_command \
        "pip install --force-reinstall \"$latest_whl\"" \
        "Package installed successfully" \
        "Installation failed"

    print_header "SUCCESS!"
    color_echo "$GREEN_COLOR_CODE" "Package has been built and installed"
}

main