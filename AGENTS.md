# SystemBench agent guide

Read `START_HERE.txt`, `.ai/CONTEXT.md`, `.ai/MEMORY.md`, `README.md`, `docs/DESIGN.md`, the relevant source module, and related tests before editing.

- Evaluate complete observable system behavior, not hidden reasoning or unsupported proxies for success.
- Keep adapters, evaluators, event sinks, aggregation, and reports modular and provider-neutral.
- Preserve trial-level evidence and configuration so aggregate results remain auditable.
- Compare systems under matched scenarios and budgets; report uncertainty and failure counts, not only averages.
- Do not tune scenarios, rubrics, thresholds, or exclusions after seeing results without recording the change.
- Keep the default example runnable offline and avoid unnecessary runtime dependencies.

Validate changes with `pytest`, `ruff check .`, and relevant typing checks when interfaces change.

Use `.ai/HANDOFF.md` only for active-task continuity. Durable methodology decisions belong in memory; individual run output does not.

## Project skills

- Use `$systembench-design-suite` before creating or materially changing scenarios,
  baselines, budgets, evaluators, rubrics, trial plans, or acceptance thresholds.
- Use `$systembench-audit-validity` for an independent, report-only review of a
  suite, evaluator, comparison, report, or benchmark claim.

The designer must not serve as the only validity auditor for the same comparison.

## Startup team

Read `.ai/TEAM.md` before multi-role or idea-to-release work. Use its explicit
gears and keep the task contract in `.ai/HANDOFF.md`; this guide's methodology
and validation requirements remain authoritative.
