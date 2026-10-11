#!/usr/bin/env bash
# Existing quality checks followed by bounded synthetic/tooling gates.
set -euo pipefail
cd "$(dirname "$0")/.."
python -m pytest
ruff check .
mypy src tests
python -m compileall -q src tests tools
python tools/repository_agent/repository_agent.py audit --json
python -m unittest discover -s tools -p 'test_*.py'
python -m pip check
python -m pip_audit --local
python scripts/browser_regressions.py
python scripts/engineering_checks.py "$@"
