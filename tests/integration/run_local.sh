#!/usr/bin/env bash
set -euo pipefail

echo "[0/6] Stopping any existing serverless-offline processes"
pkill -f "serverless offline" >/dev/null 2>&1 || true

if command -v nvm >/dev/null 2>&1; then
  echo "[0/6] Switching to Node 20 via nvm"
  nvm use 20
fi

PYTHON_BIN="python3.10"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python"
fi

echo "[1/6] Installing integration npm deps"
(cd tests/integration/api && npm ci)

echo "[2/6] Building wheel"
pipenv run python -m pip install --upgrade build
pipenv run python -m build

echo "[3/6] Creating integration venv"
"$PYTHON_BIN" -m venv .integration-venv

# shellcheck source=/dev/null
echo "[4/6] Installing built wheel into integration venv"
. .integration-venv/bin/activate
pip install dist/*.whl

echo "[5/6] Starting serverless offline (logs: /tmp/sls.log)"
(. .integration-venv/bin/activate && cd tests/integration/api && npm run start) >/tmp/sls.log 2>&1 &
SLS_PID=$!
trap 'kill $SLS_PID 2>/dev/null || true' EXIT INT TERM
sleep 5

echo "[6/6] Running Postman collection"
postman collection run tests/integration/api/postman/collection.json --bail failure --verbose
