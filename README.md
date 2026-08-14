# SystemBench

SystemBench is a reproducible evaluation framework for **complete AI systems**,
including clinical-AI research systems, rather than isolated model responses. It
treats prompts, models, retrieval, tools, policies, orchestration, fallbacks,
infrastructure, and operators as one system whose behavior must be measured.

The framework is deliberately provider-neutral and dependency-light. It includes a
runnable offline example, repeat trials, structured traces, composable evaluators, aggregate
reliability metrics, JSON reports, and tests.

Run `systembench-web` after installation and open `http://127.0.0.1:8765` for the adaptive
evaluation workbench. It critiques proposed benchmarks for LLMs, agents, frameworks, harnesses,
loops, and complete systems; generates observable human-interaction probes; and adapts a local
session after pass, partial, or failed outcomes. It uses no model, API key, database, network
dependency, or persistence. Production benchmark execution still belongs behind a reviewed adapter.

> **Research boundary:** SystemBench is not a certification service. A passing score or regression
> gate is evidence only for the frozen, declared protocol. It does not prove safety, fairness,
> compliance, equivalence, human capability, or fitness for high-impact use.

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
| Human interaction | Can people clarify, correct, interrupt, recover, and complete goals without excessive effort? |

## Adaptive interaction workbench

The browser workbench addresses common weaknesses in static benchmarks:

- model-only grading that excludes tools, retrieval, policies, infrastructure, and operators;
- one-shot clean-room prompts that omit clarification, interruption, correction, and recovery;
- aggregate scores that hide failure counts, worst-user slices, tail latency, and unsafe actions;
- unmatched tokens, tools, retries, time, or human assistance;
- circular model judges, public-task contamination, and deployment conditions that disappear.

The workbench produces a protocol-coverage assessment, construct map, evidence gaps, matched-
baseline guidance, statistical plan, and three target-specific probes. During an adaptive session,
a pass advances to a different construct, a partial result triggers a human-repair probe, and a
failure triggers a lower-complexity diagnostic replay. This policy is deterministic and visible.
See [docs/INTERACTION_BENCHMARK.md](docs/INTERACTION_BENCHMARK.md) and
[docs/SYSTEM_ARCHITECTURE.md](docs/SYSTEM_ARCHITECTURE.md).

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

## Building a defensible evaluation

Start with [VALIDATION_PROTOCOL.md](VALIDATION_PROTOCOL.md), then complete a
[benchmark card](BENCHMARK_CARD_TEMPLATE.md), an evaluated
[system/model card](MODEL_CARD_TEMPLATE.md), and a
[scenario dataset card](DATASET_CARD_TEMPLATE.md). Deployment and high-impact-use limits are in
[DEPLOYMENT_BOUNDARIES.md](DEPLOYMENT_BOUNDARIES.md); provenance requirements are in
[PROVENANCE.md](PROVENANCE.md).

Run the deterministic local project audit before release:

```bash
python tools/repository_agent/repository_agent.py audit
```

It checks repository signals and makes no external model calls. A clean audit does not validate a
benchmark; independent methodology, security, legal, accessibility, and domain review remain
necessary.

## Project layout

```text
src/systembench/       framework package
examples/              executable sample suite and adapter
tests/                 framework behavior tests
docs/                  architecture and methodology
tools/                 deterministic local review tooling
```

## Current status

This is a foundation, not a claim of benchmark validity. Before comparing systems, add a
representative scenario corpus, expert-reviewed scoring rubrics, calibrated judges, privacy
controls, and independent validation for your target domain.

SystemBench is available under the [Apache License 2.0](LICENSE). See
[GOVERNANCE.md](GOVERNANCE.md), [CONTRIBUTING.md](CONTRIBUTING.md), and
[SECURITY.md](SECURITY.md) before public or sensitive work.
