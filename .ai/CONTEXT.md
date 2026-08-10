# SystemBench project context

## Mission

Evaluate complete AI systems using repeatable scenarios, structured traces, evidence-producing evaluators, aggregate reliability metrics, and reproducible reports.

## Source map

- Human entry: `START_HERE.txt`
- Methodology: `docs/DESIGN.md`
- Validation and claims: `VALIDATION_PROTOCOL.md`, `DEPLOYMENT_BOUNDARIES.md`
- Governance/provenance: `GOVERNANCE.md`, `PROVENANCE.md`
- Implementation: `src/systembench/`
- Adaptive workbench: `src/systembench/interaction.py`, `src/systembench/static/`
- Interaction method/system design: `docs/INTERACTION_BENCHMARK.md`, `docs/SYSTEM_ARCHITECTURE.md`
- Runnable examples: `examples/`
- Verification: `tests/`
- Deterministic public-readiness audit: `tools/repository_agent/`
- Generated reports: `runs/` (ignored)

## Invariants

Keep evaluation observable and provider-neutral; preserve trial evidence and configuration; match comparison budgets; report failures, human effort, repair behavior, and uncertainty; do not tune after seeing results without disclosure. Adaptive session routing may diagnose behavior but must not rewrite a frozen comparison protocol.
