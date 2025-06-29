#!/usr/bin/env bash

# Color const section
readonly BLUE_COLOR_CODE="34"
readonly GREEN_COLOR_CODE="32"
readonly RED_COLOR_CODE="31"
readonly YELLOW_COLOR_CODE="33"
readonly CYAN_COLOR_CODE="36"

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