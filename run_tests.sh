#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"  # project root
python -m unittest discover -s tests -p "test_*.py"