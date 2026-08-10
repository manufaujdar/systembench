# SystemBench project context

## Mission

Evaluate complete AI systems using repeatable scenarios, structured traces, evidence-producing evaluators, aggregate reliability metrics, and reproducible reports.

## Source map

- Human entry: `START_HERE.txt`
- Methodology: `docs/DESIGN.md`
- Validation and claims: `VALIDATION_PROTOCOL.md`, `DEPLOYMENT_BOUNDARIES.md`
- Governance/provenance: `GOVERNANCE.md`, `PROVENANCE.md`
- Implementation: `src/systembench/`
- Runnable examples: `examples/`
- Verification: `tests/`
- Deterministic public-readiness audit: `tools/repository_agent/`
- Generated reports: `runs/` (ignored)

## Invariants

Keep evaluation observable and provider-neutral; preserve trial evidence and configuration; match comparison budgets; report failures and uncertainty; do not tune after seeing results without disclosure.
