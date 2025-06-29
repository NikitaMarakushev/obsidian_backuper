#!/usr/bin/env bash

# Strict mode
set -euo pipefail

source ./bash_libs/log.sh

function main() {
    print_header "RUN INSTALL VENV"

    run_command \
      "python3 -m venv .venv" \
      "Creating python3 venv succeed!" \
      "Creating python3 venv failed"

    run_command \
      "source .venv/bin/activate" \
      "Python3 venv activation succeed!" \
      "Python3 venv activation failed"

    run_command \
      "pip install -e .[test]" \
      "Installing dependencies from `pyproject.toml` succeed!" \
      "Installing dependencies from `pyproject.toml` failed"

    run_command \
      "pip install build" \
      "Installing build pip package succeed!" \
      "Installing build pip package failed"
}

main