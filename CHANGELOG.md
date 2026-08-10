# Changelog

## Unreleased

- Added a dependency-free local browser lab for the offline demo benchmark.
- Fixed optional latency and cost evaluators so an undeclared SLO emits an explicit
  finite result instead of non-standard JSON infinity.
- Reject duplicate JSON members and non-finite JSON values, policy thresholds, evaluator scores,
  and trial resource measurements.
- Validate every report against its exact declared scenario × trial grid and require explicit
  latency, cost, and token-usage fields instead of silently defaulting missing measurements.
- Add detached system, budget, and accounting manifests with SHA-256 fingerprints, whole-report
  fingerprints, and regression-policy/comparison fingerprints for mutation detection.
- Require suite, budget, and accounting identities to match while preserving and explicitly
  permitting baseline/candidate system-manifest differences.
- Require at least 100 bootstrap resamples and report warnings for weak scenario-cluster support.
- Add deterministic scenario-cluster bootstrap confidence intervals to benchmark reports.
- Add matched baseline comparison with auditable paired evidence and CI-friendly regression gates.
- Preserve the full suite/scenario protocol in reports for budget and configuration matching.
- Added tag-slice summaries alongside p50/p95/p99 latency and Reliability@N metrics.
- Added deterministic latency percentiles and Reliability@N summary metrics.
- Prepared contributor, security, and CI guidance for public review.

## 0.1.0

- Added offline suite loading, repeated trials, structured traces, evaluators,
  aggregation, JSON reports, and a runnable demonstration system.
