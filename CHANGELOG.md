# Changelog

## Unreleased

- Added a responsive adaptive human–system benchmark workbench for LLMs, agents,
  frameworks, harnesses, feedback loops, and complete systems.
- Added deterministic benchmark-design diagnosis, construct coverage, target-specific
  interaction probes, adaptive repair/diagnostic routing, integrity-sealed session state,
  and human-effort/calibration metrics.
- Split browser assets into packaged HTML, CSS, and JavaScript with a strict self-only
  content security policy and expanded the local JSON API.
- Documented the human-interaction construct map, matched baselines, budgets, evidence,
  statistical plan, system architecture, and validity threats.
- Expanded automated coverage from 41 to 56 tests.

## 0.1.1 - 2026-08-10

- Added Apache-2.0 licensing, notice, citation metadata, governance, conduct,
  provenance, deployment-boundary, and benchmark-validation records.
- Added benchmark, evaluated-system/model, and scenario-dataset card templates.
- Added public contribution templates and monthly dependency update configuration.
- Added a deterministic local repository review agent, supervised agent-selection
  matrix, bounded review prompt, and automated tests.
- Redesigned the offline browser lab with clearer method, local-only, evidence,
  uncertainty, accessibility, responsive, download, and copy-brief surfaces.
- Added syntax, typing, repository-audit, and browser-boundary checks to CI.
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
