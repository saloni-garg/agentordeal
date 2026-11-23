#!/bin/sh
# Verify the Dockerfile's exact steps without a Docker daemon.
#
# The Dockerfile does: copy pyproject.toml/README.md/LICENSE + agentordeal/,
# `pip install --no-cache-dir .`, entrypoint `agentordeal`. This script
# performs precisely those steps in a clean directory with a clean venv
# and then exercises the entrypoint. It verifies the build's *contents
# and install logic*; it does NOT verify the python:3.12-slim base
# image, layer caching, or daemon behaviour -- that still needs a real
# `docker build` on a machine with Docker (see docs/ADOPTION_ITERATIONS.md
# iteration 19).
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$WORK/app"
cp "$ROOT/pyproject.toml" "$ROOT/README.md" "$ROOT/LICENSE" "$WORK/app/"
cp -r "$ROOT/agentordeal" "$WORK/app/agentordeal"
python3 -m venv "$WORK/venv"
"$WORK/venv/bin/pip" install --no-cache-dir -q "$WORK/app"
cd "$WORK"
"$WORK/venv/bin/agentordeal" --help >/dev/null
"$WORK/venv/bin/agentordeal" list | tail -1
"$WORK/venv/bin/agentordeal" quickstart --out "$WORK/out" | tail -2
echo "DOCKER-EQUIVALENT OK: clean copy + pip install + entrypoint verified"
