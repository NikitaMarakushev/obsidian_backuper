#!/usr/bin/env bash

function color_echo() {
    local color=$1
    shift
    echo -e "\e[${color}m$*\e[0m"
}

echo -e "\n"
color_echo "34" "################ RUN BUILD ##############"

echo -e "\n"

python -m build
color_echo "34" "################BULD SUCCEED###########\n"

color_echo "34" "################INSTALL OBSIDIAN BACKUPER##############\n"
pip install dist/obsidian_backuper-1.0.2-py3-none-any.whl
color_echo "34" "################OBSIDIAN BACKUPER INSTALLED#############\n"