#!/usr/bin/env bash

#strict mode
set -euo pipefail

function color_echo() {
    local color=$1
    shift
    echo -e "\e[${color}m$*\e[0m"
}

function check_success() {
    if [ $? -eq 0 ]; then
        color_echo "32" "✓ $1"
    else
        color_echo "31" "✗ $2"
        exit 1
    fi
}

echo -e "\n"
color_echo "34" "################ RUN BUILD ##############"

python -m build
check_success "Build completed successfully" "Build failed"

LATEST_WHL=$(ls -t dist/*.whl | head -n1)
check_success "Found wheel file: $LATEST_WHL" "No wheel file found in dist/"

echo -e "\n"
color_echo "34" "################ INSTALL OBSIDIAN BACKUPER ##############"

pip install --force-reinstall "$LATEST_WHL"
check_success "Package installed successfully" "Installation failed"

echo -e "\n"
color_echo "32" "################ SUCCESS! ##############"
color_echo "32" "obsidian_backuper has been built and installed"
echo -e "\n"

if command -v obsidian-backup >/dev/null 2>&1; then
    color_echo "36" "You can now run: obsidian-backup --help"
else
    color_echo "33" "Warning: obsidian-backup command not found in PATH"
fi