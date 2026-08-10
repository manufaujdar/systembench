---
name: systembench-design-suite
description: Design representative, reproducible whole-system evaluation suites for SystemBench. Use when defining scenarios, baselines, evaluators, failure injections, trial counts, budgets, rubrics, or acceptance thresholds before comparing an AI system or changing an existing benchmark.
---

# Design a SystemBench suite

Read `AGENTS.md`, `docs/DESIGN.md`, `.ai/CONTEXT.md`, the target adapter, and the
smallest relevant existing suite before editing.

## Workflow

1. State the decision the evaluation must support, target system, users, operating
   conditions, and constructs being measured.
2. Define observable success and failure. Do not use hidden reasoning or a model's
   self-confidence as ground truth.
3. Build scenarios from real task classes, including common, boundary, adversarial,
   degraded-component, and recovery cases. Record the sampling rationale.
4. Specify matched baselines and budgets for model access, tools, retrieval, latency,
   retries, and human intervention.
5. Make every evaluator return evidence. Predefine rubrics, exclusions, aggregation,
   thresholds, trial counts, seeds where applicable, and uncertainty reporting.
6. Separate suite-design data from final comparison data. Freeze and version the
   protocol before inspecting comparative results.
7. Add the narrowest tests needed for parsing, trial preservation, evaluator output,
   and deterministic offline behavior.

## Required handoff

Report the decision, construct map, scenario coverage, baselines, budgets,
evaluators, failure injections, statistical plan, validity threats, frozen fields,
files changed, and checks run.

Stop before using private production traces, changing a frozen protocol after
seeing results, or claiming benchmark validity without representative evidence and
independent review.
