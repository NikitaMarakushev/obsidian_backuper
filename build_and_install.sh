#!/usr/bin/env bash

# Strict mode
set -euo pipefail

source ./bash_libs/log.sh

function main() {
    print_header "RUN BUILD"

    run_command \
        "python3 -m build" \
        "Build completed successfully" \
        "Build failed"

    local latest_whl
    latest_whl=$(find_latest_whl)
    color_echo "$GREEN_COLOR_CODE" "Found wheel file: $latest_whl"

    print_header "INSTALL $PACKAGE_NAME"

    run_command \
        "pip install --force-reinstall \"$latest_whl\"" \
        "Package installed successfully" \
        "Installation failed"

    print_header "SUCCESS!"
    color_echo "$GREEN_COLOR_CODE" "$PACKAGE_NAME has been built and installed"

    if command -v "$COMMAND_NAME" >/dev/null 2>&1; then
        color_echo "$CYAN_COLOR_CODE" "You can now run: $COMMAND_NAME --help"
        color_echo "$CYAN_COLOR_CODE" "Version: $($COMMAND_NAME --version 2>/dev/null || echo 'unknown')"
    else
        color_echo "$YELLOW_COLOR_CODE" "Warning: $COMMAND_NAME command not found in PATH"
        color_echo "$YELLOW_COLOR_CODE" "You may need to add Python scripts directory to your PATH"
    fi
}

main