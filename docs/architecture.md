# System architecture

SystemBench runs versioned scenarios against a complete system adapter and
turns observable trial behavior into evidence-backed reports.

## Component flow

Suite and protocol -> runner -> system adapter -> system under test
                              -> trace events, output, usage, errors
Evaluators -> trial scores/evidence -> aggregator/statistics -> report/comparison

## Components

- models.py: scenario, suite, trace, evaluator, report, and comparison contracts.
- io.py: JSON suite/report loading and serialization.
- adapters.py: system-under-test boundary.
- runner.py: repeat trials, failures, traces, and report creation.
- evaluators.py: composable observable-property evaluators.
- statistics.py: aggregates, percentiles, bootstrap intervals, Reliability@N, and slices.
- comparison.py: paired baseline comparison and regression gates.
- integrity.py: report/protocol integrity and fingerprinting.
- cli.py and web.py: local operator surfaces.
- examples/ and tests/: deterministic usage and regression coverage.

## Trust boundary and interpretation

The runner should receive sanitized inputs and emit evidence another team can
inspect without secrets or raw sensitive data. Suite, scenario, system, runner,
and seed versions should be pinned. A passing gate means only that this
protocol did not detect a regression above its threshold; it is not evidence of
clinical validity or external generalization.

