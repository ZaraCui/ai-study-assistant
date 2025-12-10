#!/bin/bash
set -e

echo "Installing project as package..."
pip install -e .

echo "Installing backend dependencies..."
pip install -r backend/requirements.txt

echo "Build complete!"
