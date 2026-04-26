#!/usr/bin/env bash
set -e

# 
# Script to find (via pattern matching) and execute all tests in the tests directory.
# Usage: ./run_tests.sh
#
#

cd "$(dirname "$0")"  # project root
python -m unittest discover -s tests -p "test_*.py"