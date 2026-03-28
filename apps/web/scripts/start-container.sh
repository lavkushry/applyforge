#!/bin/sh
set -eu

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-3000}"
MODE="${NEXT_RUNTIME_MODE:-production}"

if [ "$MODE" = "dev" ]; then
  exec npm run dev -- -H "$HOST" -p "$PORT"
fi

npm run build
exec npm run start -- -H "$HOST" -p "$PORT"
