# SystemBench startup team

Mission: make complete AI-system evaluations reproducible, comparable, and
useful for decisions without overstating benchmark validity.

| Gear | Team role | Accountable for |
|---|---|---|
| Founder review | Evaluation product lead | Decision to support, target user, and useful evaluation scope |
| Product review | Methodology lead | Constructs, scenarios, rubrics, budgets, uncertainty, and validity threats |
| Execution plan | Evaluation architect | Adapters, trials, traces, evaluators, aggregation, and failure injection |
| Execute | Framework engineer | Runner, schemas, reports, examples, and tests |
| Red-team review | Independent quality auditor | Leakage, unmatched comparisons, post-hoc tuning, weak evidence, and missing failures |
| Release | Reproducibility lead | `pytest`, `ruff`, typing checks, methodology docs, and runnable examples |
| Retro | Evaluation lead | Invalid assumptions, evaluator drift, and next calibration work |

Use `.ai/HANDOFF.md` for the task contract. `docs/DESIGN.md`, scenario inputs,
trial evidence, and run configuration are authoritative. Follow `AGENTS.md`; do
not optimize a suite after seeing results without recording the change.

