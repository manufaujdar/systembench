# SystemBench project context

## Mission

Evaluate complete AI systems using repeatable scenarios, structured traces, evidence-producing evaluators, aggregate reliability metrics, and reproducible reports.

## Source map

- Human entry: `START_HERE.txt`
- Methodology: `docs/DESIGN.md`
- Implementation: `src/systembench/`
- Runnable examples: `examples/`
- Verification: `tests/`
- Generated reports: `runs/` (ignored)

## Invariants

Keep evaluation observable and provider-neutral; preserve trial evidence and configuration; match comparison budgets; report failures and uncertainty; do not tune after seeing results without disclosure.
