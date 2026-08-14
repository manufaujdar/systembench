# Technical overview

Status: offline alpha benchmark foundation.

## Runtime and package map

- Python 3.10 or newer; source package is under src/systembench.
- Core has no required runtime dependencies.
- Development uses pytest, Ruff, and mypy.
- Entrypoints are systembench and systembench-web.
- JSON examples are under examples/; CLI reports use runs/.

## Code responsibilities

- models.py: typed public contracts.
- adapters.py: APIs, agents, RAG systems, local models, or production-system boundary.
- runner.py: repeated trials, traces, and evidence.
- evaluators.py: scores, decisions, explanations, and evidence.
- statistics.py: pass/error/latency/cost/reliability/slice metrics and intervals.
- comparison.py: paired baseline gates.
- io.py and integrity.py: reproducible artifacts.
- cli.py and web.py: local operator surfaces.

## Operations and methodology

Run an example suite with repeated trials, compare baseline and candidate
reports with declared thresholds, and run pytest. Keep suite content, scenario
identities, trial counts, seeds, report schema, and runner versions matched.

Evaluator validity, representative sampling, human labels, judge calibration,
privacy-safe transformation, load behavior, distributed execution, signed
artifacts, and domain governance remain outside the offline foundation. Do not
report a single leaderboard number without distributions, uncertainty, failure
slices, and protocol provenance.

