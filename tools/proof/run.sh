#!/bin/sh
# The whole proof kit in one command, from the repo root: tests (results for the claims table),
# narration (local Kokoro when its venv exists, silent timing otherwise), headless recording, mux,
# video checks, claims table and GIF.        VIDEO_LIMIT=120 sh tools/proof/run.sh
set -e
LIMIT="${VIDEO_LIMIT:-120}"
PY="${PYTHON:-python3}"   # a Python with api/requirements.txt installed
KOKORO="$HOME/.local/share/liminal-tts/.venv/bin/python"
TRASH=/usr/local/opt/trash/bin/trash
pkill -f "next start -p 3100" || true
trap 'pkill -f "next start -p 3100" || true' EXIT   # stop the server even when a check fails
if [ -x "$TRASH" ] && [ -d proof ]; then "$TRASH" proof; else rm -rf proof; fi
mkdir proof
(cd api && DEMO_MODE=1 "$PY" -m pytest -q --junitxml=../proof/pytest.xml >/dev/null) || { echo "API TESTS FAILED"; exit 1; }
(cd web && npx playwright test --reporter=json > ../proof/playwright.json) || { echo "WEB TESTS FAILED"; exit 1; }
(cd web && DEMO_MODE=1 exec npx next start -p 3100) > /dev/null 2>&1 &
export PROOF_DIR="$PWD/proof"
if [ -x "$KOKORO" ]; then "$KOKORO" tools/proof/narrate.py prepare tools/proof/demo-path.json | tail -1
else python3 tools/proof/narrate.py prepare --silent tools/proof/demo-path.json | tail -1; fi
sleep 3
(cd web && node ../tools/proof/record.mjs ../tools/proof/demo-path.json) | tail -1
python3 tools/proof/narrate.py build | tail -1
sh tools/proof/mux.sh proof | tail -1
python3 tools/proof/check_video.py --limit "$LIMIT"
python3 tools/proof/proof_table.py tools/proof/claims.json > proof/proven.md
mkdir -p docs && cp proof/demo.gif docs/demo.gif
