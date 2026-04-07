#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"

kill_pid_gracefully() {
  local pid="$1"

  if ! kill -0 "$pid" 2>/dev/null; then
    return
  fi

  kill "$pid" 2>/dev/null || true

  for _ in {1..20}; do
    if ! kill -0 "$pid" 2>/dev/null; then
      return
    fi
    sleep 0.2
  done

  kill -9 "$pid" 2>/dev/null || true
}

kill_by_port() {
  local port="$1"
  local pids=""

  if command -v lsof >/dev/null 2>&1; then
    pids="$(lsof -t -iTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)"
  elif command -v ss >/dev/null 2>&1; then
    pids="$(ss -ltnp 2>/dev/null | awk -v p=":$port" '$4 ~ p {print $NF}' | sed -E 's/.*pid=([0-9]+).*/\1/' | sort -u || true)"
  fi

  if [[ -z "$pids" ]]; then
    echo "No listener found on port $port"
    return
  fi

  for pid in $pids; do
    echo "Stopping process $pid on port $port"
    kill_pid_gracefully "$pid"
  done
}

kill_by_pattern() {
  local pattern="$1"
  local pids=""

  if command -v pgrep >/dev/null 2>&1; then
    pids="$(pgrep -f "$pattern" || true)"
  fi

  if [[ -z "$pids" ]]; then
    echo "No process matched pattern: $pattern"
    return
  fi

  for pid in $pids; do
    echo "Stopping process $pid (pattern: $pattern)"
    kill_pid_gracefully "$pid"
  done
}

echo "Stopping app services..."
kill_by_port 5000
kill_by_port 5010
kill_by_port 5020

# Stop ngrok tunnel if running
kill_by_pattern "ngrok http 5000"

echo "Stopping Docker services (db, pgadmin)..."
cd "$ROOT"
docker compose down

echo "All services stopped."
