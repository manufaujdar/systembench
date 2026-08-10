---
name: systembench-audit-validity
description: Independently audit SystemBench suites, evaluator logic, reports, and comparative claims for validity and fairness. Use when reviewing benchmark design or results for leakage, unmatched budgets, post-hoc tuning, weak rubrics, missing uncertainty, evaluator bias, or unsupported conclusions.
---

# Audit SystemBench validity

Remain report-only. Do not repair the implementation being audited or certify your
own prior work.

1. Read `AGENTS.md`, `docs/DESIGN.md`, the suite, adapter configuration, evaluator
   code, trial evidence, and report metadata.
2. Reconstruct the intended decision and verify that scenarios and metrics measure
   the stated constructs rather than convenient proxies.
3. Check sampling coverage, contamination and leakage, rubric provenance, judge
   calibration, inter-rater evidence where relevant, and treatment of missing or
   failed trials.
4. Verify matched inputs, tools, retries, latency/cost accounting, human help, and
   stopping rules across compared systems.
5. Look for post-hoc exclusions, threshold changes, selective reruns, aggregation
   artifacts, hidden multiple comparisons, and conclusions that exceed the data.
6. Recompute or spot-check deterministic aggregates from trial evidence and confirm
   configuration, versions, environment, and failures remain traceable.

Return severity-ranked findings with file/evidence locations, affected claims,
required remediation, and residual validity threats. A clean audit must name what
was checked; it does not establish external validity beyond the tested population.
