#!/usr/bin/env bash
# Helper to run the pipeline with certifi SSL bundle
set -e

# Activate venv if present
if [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

# Build React frontend if dist or JS assets not found
if [ ! -f "frontend/dist/index.html" ] || [ -z "$(ls -A frontend/dist/assets/*.js 2>/dev/null)" ]; then
  if command -v npm &> /dev/null; then
    echo "📦 Đang build mã nguồn React frontend..."
    npm --prefix frontend run build
  fi
fi

CERT_FILE=$(python3 -c "import certifi; print(certifi.where())")
export SSL_CERT_FILE="$CERT_FILE"

# Tự động giải phóng cổng 8000 nếu đang có tiến trình cũ chiếm dụng
PORT="${PORT:-8000}"
EXISTING_PID=$(lsof -ti :"$PORT" 2>/dev/null || true)
if [ -n "$EXISTING_PID" ]; then
  echo "⚠️ Cổng $PORT đang có tiến trình chạy (PID: $EXISTING_PID). Đang giải phóng cổng..."
  kill -9 $EXISTING_PID 2>/dev/null || true
  sleep 1
fi

# Use the project virtual environment Python if available
PYTHON_EXEC=".venv/bin/python3"
if [ -x "$PYTHON_EXEC" ]; then
  exec "$PYTHON_EXEC" main.py
else
  exec python3 main.py
fi
