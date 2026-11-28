#!/usr/bin/env bash
# Run the whole app locally with one command: API + ingestion worker + UI.
# Ctrl+C stops all of them. Usage: ./dev.sh
set -uo pipefail

cd "$(dirname "$0")"

VENV_DIR="${VENV_DIR:-.venv}"
if [[ -x "$VENV_DIR/bin/python" ]]; then
  PYTHON=("$VENV_DIR/bin/python")
  UVICORN=("$VENV_DIR/bin/uvicorn")
  STREAMLIT=("$VENV_DIR/bin/streamlit")
else
  PYTHON=(python3)
  UVICORN=(python3 -m uvicorn)
  STREAMLIT=(python3 -m streamlit)
fi

API_HOST="${API_HOST:-127.0.0.1}"
API_PORT="${API_PORT:-8000}"
UI_PORT="${UI_PORT:-8501}"

# Refuse to start on top of something that is already listening.
for port in "$API_PORT" "$UI_PORT"; do
  if command -v ss >/dev/null 2>&1 && ss -ltn "sport = :$port" 2>/dev/null | grep -q LISTEN; then
    echo "Port $port is already in use. Stop that process first." >&2
    exit 1
  fi
done

pids=()

cleanup() {
  trap - EXIT INT TERM
  echo
  echo "Shutting down..."
  for pid in "${pids[@]}"; do
    kill "$pid" 2>/dev/null
  done
  wait 2>/dev/null
  echo "All services stopped."
}
trap cleanup EXIT INT TERM

start() {
  local name="$1"
  shift
  "$@" > >(sed -u "s/^/[$name] /") 2>&1 &
  pids+=("$!")
}

echo "Starting API      -> http://$API_HOST:$API_PORT"
start api "${UVICORN[@]}" backend.main:app --host "$API_HOST" --port "$API_PORT"

echo "Starting worker   -> ingestion jobs"
start worker "${PYTHON[@]}" -m backend.worker

echo "Starting UI       -> http://$API_HOST:$UI_PORT"
start ui "${STREAMLIT[@]}" run frontend/app.py --server.address "$API_HOST" --server.port "$UI_PORT"

echo "Press Ctrl+C to stop everything."
echo

# Exit (and clean up the rest) as soon as any service dies.
wait -n
status=$?
echo "A service exited (status $status); stopping the others." >&2
exit "$status"
