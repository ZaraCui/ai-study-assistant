#!/bin/bash
# Render deployment script
# Ensures the project is properly set up before starting the server

set -e

echo "=== AI Study Assistant Deployment ==="
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"

# Check if we need to set PYTHONPATH
if [ -z "$PYTHONPATH" ]; then
    echo "Setting PYTHONPATH to $(pwd)"
    export PYTHONPATH="$(pwd)"
fi

echo "PYTHONPATH: $PYTHONPATH"

# Verify backend module can be imported
echo "Verifying backend module..."
python -c "from backend.app import app; print('✓ Backend module imports successfully')" || {
    echo "✗ Failed to import backend module"
    exit 1
}

echo "Starting uvicorn..."
exec uvicorn backend.app:app --host 0.0.0.0 --port $PORT
