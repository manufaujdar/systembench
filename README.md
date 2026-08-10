# SystemBench

SystemBench is a benchmark framework for evaluating **complete AI systems**, not isolated
model responses. It treats prompts, models, retrieval, tools, policies, orchestration,
fallbacks, infrastructure, and operators as one system whose behavior must be measured.

The initial scaffold is deliberately provider-neutral and dependency-light. It includes a
runnable offline example, repeat trials, structured traces, composable evaluators, aggregate
reliability metrics, JSON reports, and tests.

Run `systembench-web` after installation and open `http://127.0.0.1:8765` for a
small browser lab. It exercises the bundled offline system without a model, API key,
database, or additional dependency; production benchmark suites still belong in the CLI.

## What it measures

| Dimension | Example question |
|---|---|
| Task success | Did the system produce the correct real-world outcome? |
| Reliability | Does it keep working across repeated trials and component failures? |
| Groundedness | Are important claims supported by supplied evidence? |
| Tool correctness | Were the right tools called with safe, valid arguments? |
| Safety | Did policies hold under adversarial or ambiguous input? |
| Performance | Are latency, cost, and resource use within an SLO? |
| Operability | Can failures be observed, diagnosed, retried, and recovered? |

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
systembench run examples/basic_suite.json --trials 3
pytest
```

Reports are written to `runs/<run-id>/report.json`. Each report preserves the suite and scenario
protocol, configuration, per-trial traces, evaluator evidence, aggregate metrics, deterministic
bootstrap confidence intervals, latency percentiles, Reliability@N, tag-slice metrics, and
environment metadata.

## CI regression checks

Run a candidate with the same suite version, trial count, and run seed as a pinned baseline, then
compare the report artifacts offline:

```bash
systembench compare runs/baseline/report.json runs/candidate/report.json \
  --max-pass-rate-drop 0.02 \
  --max-error-rate-increase 0.01 \
  --bootstrap-seed 2026 \
  --output runs/comparison.json
```

The command exits with status 1 when a gate fails. Pass-rate and error-rate gates default to zero
tolerance. Latency and cost gates are opt-in because acceptable changes are system-specific; add
`--max-mean-latency-increase-ms` or `--max-mean-cost-increase-usd` only after declaring practical
tolerances. Comparison rejects unmatched suite content, trial counts, run seeds, or trial
identities, and records every paired trial delta in its JSON output.

## Architecture

```text
Suite -> Runner -> SystemAdapter -> SystemUnderTest
             |            |
             |            +-> trace events, output, usage, errors
             v
        Evaluators -> trial scores -> Aggregator -> Report
```

The main extension points are:

- `SystemAdapter`: wraps an API, agent, RAG application, local model, or production system.
- `Evaluator`: scores one observable property and returns evidence, not only a number.
- `EventSink`: exports traces to an observability backend.
- Scenario JSON: declares inputs, expectations, tags, constraints, and failure injections.

See [docs/DESIGN.md](docs/DESIGN.md) for design principles, metric definitions, roadmap,
and guidance on building trustworthy benchmark suites.

## Project layout

```text
src/systembench/       framework package
examples/              executable sample suite and adapter
tests/                 framework behavior tests
docs/                  architecture and methodology
```

## Current status

This is a foundation, not a claim of benchmark validity. Before comparing systems, add a
representative scenario corpus, expert-reviewed scoring rubrics, calibrated judges, privacy
controls, and independent validation for your target domain.
