#!/usr/bin/env bash

set -euo pipefail

pip uninstall obsidian-backuper -y
pip install -e .