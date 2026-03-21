#!/usr/bin/env bash
set -e

echo "Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info

echo "Upgrading build tools..."
python3 -m pip install --upgrade pip build twine

echo "Building source distribution and wheel..."
python3 -m build

echo "Uploading to PyPI..."
# This will prompt for a PyPI API token
python3 -m twine upload dist/*

echo "Alpha release 0.6.0a1 published successfully!"
