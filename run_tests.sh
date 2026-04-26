#!/usr/bin/env bash
set -e

# 
# Finds (via pattern matching) and executes all tests in the tests directory.
# Usage: ./run_tests.sh
#
#

cd "$(dirname "$0")"  # project root
python -m unittest discover -s tests -p "test_*.py"