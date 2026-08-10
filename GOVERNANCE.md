# Governance

SystemBench is an early-stage open-source research project for evaluating
complete AI systems.

## Maintainer responsibility

The repository maintainer reviews pull requests, releases, dependency and
provenance changes, public benchmark claims, and changes to methodology-sensitive
code. A change may be rejected when it increases privacy, security, licensing,
validity, or overclaiming risk.

## Methodology decisions

Changes to scenarios, rubrics, evaluators, exclusions, budgets, trial plans, or
acceptance thresholds must be declared before examining candidate results when
those changes could affect a comparison. Post-result changes require a dated
record, rationale, and a new suite or protocol version. The author of a benchmark
design should not be its only validity reviewer.

## Contributions

Contributions should include tests, documentation, provenance, and a clear
statement of what remains unvalidated. Private data, hidden challenge sets,
production traces, or licensed model artifacts require a separately approved
storage and access process; they do not belong in public pull requests.

## Releases

A release should update [CHANGELOG.md](CHANGELOG.md), pass the full CI workflow,
run the deterministic repository audit, reconcile package and citation versions,
and state unresolved limitations. A version tag does not validate a suite,
certify a model, establish fairness, or approve deployment.
