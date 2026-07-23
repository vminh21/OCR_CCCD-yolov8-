#!/usr/bin/env bash
# Helper to run the pipeline with certifi SSL bundle
set -e

# Activate venv if present
if [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

CERT_FILE=$(python3 -c "import certifi; print(certifi.where())")
export SSL_CERT_FILE="$CERT_FILE"

# Use the project virtual environment Python if available
PYTHON_EXEC=".venv/bin/python3"
if [ -x "$PYTHON_EXEC" ]; then
  "$PYTHON_EXEC" main.py
else
  python3 main.py
fi
