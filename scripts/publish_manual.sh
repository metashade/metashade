#!/usr/bin/env bash
set -e

# Ensure we're running from the repository root
cd "$(git rev-parse --show-toplevel)"

echo "Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info

echo "Upgrading build tools..."
python3 -m pip install --upgrade pip build twine

echo "Building source distribution and wheel..."
python3 -m build

echo "Uploading to PyPI..."
# Twine will prompt for your PyPI username and password (use __token__
# as the username and your PyPI API token as the password, or set
# TWINE_USERNAME/TWINE_PASSWORD environment variables).
python3 -m twine upload dist/*

echo "Release published successfully!"
