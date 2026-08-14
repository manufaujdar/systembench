# Benchmark validation protocol

This is a protocol scaffold, not evidence that SystemBench or a suite built with
it is valid. Freeze the protocol before using it to compare candidate systems.

## 1. Construct and intended decision

- State the real decision the benchmark will inform.
- Define each measured construct operationally and list important properties the
  suite does not measure.
- Identify target users, deployment conditions, failure severity, and the minimum
  practically meaningful difference.

## 2. Scenario corpus

- Record provenance, transformation, license, author, domain, difficulty, risk,
  language, and review status for every scenario.
- Separate development, calibration, and held-out test material; assess whether
  models or system developers may have seen equivalent examples.
- Sample from realistic workflows and report missing populations or conditions.
- Freeze the suite version and fingerprint before candidate results are examined.

## 3. Evaluators and human labels

- Prefer deterministic checks tied to observable outcomes.
- Blind reviewers to system identity where practical; publish reviewer training,
  adjudication rules, disagreement, and inter-rater agreement.
- Calibrate any model judge against representative human labels and test position,
  verbosity, style, self-preference, and demographic or language bias.
- Pin judge model, prompt, sampling parameters, code, and provider version. A judge
  change creates a new accounting protocol.

## 4. Trial and resource protocol

- Predeclare trials, seeds, state reset, concurrency, timeout, retries, budgets,
  rate limits, and measurement sources.
- Compare releases on the same scenario × trial grid and under matched budgets.
- Preserve errors, traces, evaluator evidence, latency, cost, and usage at trial
  level; do not silently exclude failures.

## 5. Analysis

- Report counts, distributions, scenario-cluster confidence intervals,
  Reliability@N, worst relevant slices, and failure categories.
- Predeclare regression tolerances and multiple-comparison handling.
- Treat small suites, wide intervals, weak slice support, and evaluator disagreement
  as limitations—not as permission to collapse results into a confident ranking.

## 6. Robustness and external validation

- Repeat runs across time, providers, regions, hardware, and realistic dependency
  failures where relevant.
- Use negative controls, adversarial tests, evaluator unit tests, and an independent
  validity audit.
- Confirm important conclusions on a separately governed external suite before a
  consequential claim or deployment gate.

## 7. Release record

Archive the suite, manifests, code revision, environment, raw trial evidence,
analysis, deviations, exclusions, limitations, reviewer sign-off, and rollback
criteria. Publish only data and artifacts that are safe and licensed to disclose.
