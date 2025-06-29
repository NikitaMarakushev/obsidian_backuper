#!/usr/bin/env bash

# Strict mode
set -euo pipefail

python3 -m venv .venv

source .venv/bin/activate

pip install -e .[test]

pip install build
