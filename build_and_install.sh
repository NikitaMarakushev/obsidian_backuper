#!/usr/bin/env bash

# Color const section
readonly BLUE_COLOR_CODE="34"
readonly GREEN_COLOR_CODE="32"
readonly RED_COLOR_CODE="31"
readonly YELLOW_COLOR_CODE="33"
readonly CYAN_COLOR_CODE="36"

# Strict mode
set -euo pipefail

readonly PACKAGE_NAME="obsidian_backuper"
readonly COMMAND_NAME="obsidian-backup"

function color_echo() {
    local color=$1
    shift
    local message="$*"
    echo -e "\e[${color}m${message}\e[0m"
}

function run_command() {
    local command="$1"
    local success_msg="$2"
    local error_msg="$3"

    if eval "$command"; then
        color_echo "$GREEN_COLOR_CODE" "✓ $success_msg"
    else
        color_echo "$RED_COLOR_CODE" "✗ $error_msg"
        exit 1
    fi
}

function print_header() {
    echo -e "\n"
    color_echo "$BLUE_COLOR_CODE" "################ $1 ##############"
}

function find_latest_whl() {
    local whl_file
    whl_file=$(ls -t dist/*.whl 2>/dev/null | head -n1)

    if [[ -z "$whl_file" ]]; then
        color_echo "$RED_COLOR_CODE" "No wheel files found in dist/"
        exit 1
    fi

    echo "$whl_file"
}

function main() {
    print_header "RUN BUILD"

    run_command \
        "python -m build" \
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