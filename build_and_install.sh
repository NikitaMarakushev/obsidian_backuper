#!/usr/bin/env bash


echo "################RUN BUILD##############\n"
python -m build
echo "################BULD SUCCEED###########\n"

echo "################INSTALL OBSIDIAN BACKUPER##############\n"
pip install dist/obsidian_backuper-1.0.2-py3-none-any.whl
echo "################OBSIDIAN BACKUPER INSTALLED#############\n"