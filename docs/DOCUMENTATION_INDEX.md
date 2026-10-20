# Documentation index

SystemBench is a provider-neutral Python framework for evaluating complete AI
systems. It measures outcomes, process, operations, reliability, and failure
recovery; it is not a claim that any benchmark suite is valid by default.

## Choose a task

| Task | Read first | Continue with |
| --- | --- | --- |
| Run an offline trial | [Quick start](../README.md#quick-start) | [Technical overview](technical-overview.md) |
| Design a suite or interpret a report | [Methodology](DESIGN.md) | [Validation protocol](../VALIDATION_PROTOCOL.md), [benchmark card](../BENCHMARK_CARD_TEMPLATE.md) |
| Compare a candidate with a baseline | [Regression checks](../README.md#ci-regression-checks) | [Matched comparison rules](DESIGN.md#41-baseline-comparison-and-ci-gates) |
| Work on the adaptive workbench | [Interaction benchmark](INTERACTION_BENCHMARK.md) | [Workbench architecture](SYSTEM_ARCHITECTURE.md) |
| Add an adapter or evaluator | [Software architecture](architecture.md) | [System/model card](../MODEL_CARD_TEMPLATE.md), [provenance](../PROVENANCE.md) |
| Contribute or publish | [Contribution guide](../CONTRIBUTING.md) | [Engineering checks](../TOOLING.md), [governance](../GOVERNANCE.md), [deployment boundaries](../DEPLOYMENT_BOUNDARIES.md) |

## File and folder ownership

| Location | Purpose |
| --- | --- |
| `src/systembench/` | Runner, adapters, evaluators, statistics, comparison and report contracts |
| `src/systembench/static/` | Packaged browser workbench assets |
| `examples/`, `tests/` | Offline sample suite and deterministic contract evidence |
| `docs/DESIGN.md`, `docs/INTERACTION_BENCHMARK.md` | Evaluation methodology and adaptive interaction policy |
| `docs/architecture.md`, `docs/SYSTEM_ARCHITECTURE.md` | Software baseline and workbench component map |
| `tools/`, `scripts/` | Supervised repository audit and engineering gates |
| `runs/` | Generated local trial reports; retain safe evidence outside source files |
| `.ai/`, `AGENTS.md`, `.agents/skills/` | Task continuity, suite-design rules and independent validity-audit routing |

Keep evaluator and protocol decisions in the methodology documents, UI behavior
beside the packaged workbench, and run-specific results in report artifacts.
Link to shared policies instead of copying them into new task notes.

## Evidence, licensing and release limits

The root [Apache-2.0 license](../LICENSE) and [NOTICE](../NOTICE) are present.
Benchmark, system/model and [scenario dataset](../DATASET_CARD_TEMPLATE.md)
cards record separate evidence and provenance requirements. A green test suite
does not validate a benchmark population or scoring rubric. Freeze scenarios,
budgets and thresholds before comparison, preserve trial-level failures and
uncertainty, and retain independent methodology review before publishing claims.

