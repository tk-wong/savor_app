#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$ROOT/logs"
mkdir -p "$LOG_DIR"

strip_ansi() {
  sed -u -E 's/\x1B\[[0-9;]*[[:alpha:]]//g'
}

# 1) infra
docker compose up -d db pgadmin

# 2) backend
(
  cd "$ROOT/backend"
  uv run -m backend.main ./test/integration_test/.env_frontend_integration \
    2>&1 | strip_ansi > "$LOG_DIR/backend.log"
) &

# 3) ngrok (for backend)
(
  cd "$ROOT"
  ngrok http 5000 2>&1 | strip_ansi > "$LOG_DIR/ngrok.log"
) &

# 4) AI cooking agent
(
  cd "$ROOT/models/AI_cooking_agent"
  uv run main.py 2>&1 | strip_ansi > "$LOG_DIR/ai_agent.log"
) &

# 5) image generation
(
  cd "$ROOT/models/image_generation_model"
  uv run main.py 2>&1 | strip_ansi > "$LOG_DIR/image_gen.log"
) &

echo "Services started."
echo "View all logs in one place:"
echo "tail -f $LOG_DIR/backend.log $LOG_DIR/ngrok.log $LOG_DIR/ai_agent.log $LOG_DIR/image_gen.log"