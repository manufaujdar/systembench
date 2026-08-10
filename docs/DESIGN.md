# SystemBench design and methodology

## 1. Evaluation target

The unit under test is a versioned **system release**: model(s), prompts, retrieval indexes,
tool implementations, routing, memory, policies, retries, infrastructure, and configuration.
A report should be reproducible from a system version, suite version, runner version, seed,
and sanitized environment snapshot.

Avoid a single leaderboard number. Publish a scorecard and the underlying distributions so
teams can see trade-offs and failure modes.

## 2. Scenario contract

Every scenario should state:

- a realistic user goal and initial state;
- the observable outcome that counts as success;
- allowed and forbidden actions;
- latency, cost, privacy, and safety constraints;
- required trace evidence;
- optional perturbations or component failures;
- provenance, domain, difficulty, and review status.

Keep hidden test data separate from development data. Version scenarios immutably after they
are used for a public comparison, and track contamination risk.

## 3. Measurement layers

1. **Outcome:** completion, factual accuracy, groundedness, safety, and human usefulness.
2. **Process:** tool choice, arguments, citations, policy decisions, retries, and recovery.
3. **Operations:** availability, tail latency, cost, rate limits, resource use, and observability.
4. **Reliability:** variance across trials, worst-group performance, and behavior under faults.

Each evaluator returns a normalized score, pass/fail decision, explanation, and machine-readable
evidence. Deterministic evaluators should be preferred. Model judges require calibration against
human labels, blinded pairwise testing where possible, judge-version recording, and periodic
bias/drift audits.

## 4. Core metrics

- **Pass@1:** successful trials / all trials.
- **Reliability@N:** scenarios for which every one of N trials passes / all scenarios.
- **Pass under fault:** pass rate for scenarios with failure injection.
- **Worst-slice pass rate:** minimum pass rate across declared domains or risk groups.
- **Error rate:** unhandled system errors / trials.
- **Latency:** p50, p95, p99 end-to-end wall time, plus component spans.
- **Cost per successful task:** total measured cost / successful trials.
- **Calibration:** whether confidence predicts empirical correctness.
- **Recovery rate:** injected failures followed by a valid recovery / injected failures.

The runner calculates pass rate, error rate, mean latency/cost, p50/p95/p99 latency, Reliability@N,
tag-slice metrics, and mean evaluator scores. It reports deterministic percentile-bootstrap
confidence intervals for pass rate, error rate, mean latency/cost, Reliability@N, and mean
evaluator scores. The bootstrap resamples scenarios as clusters and retains every repeated trial
within a selected scenario, so repeated trials are not treated as independent task samples. The
report records the bootstrap sample count, confidence level, and seed.

### 4.1 Baseline comparison and CI gates

Baseline comparisons are paired by scenario ID and trial number. SystemBench refuses a comparison
unless both reports have identical report schema versions, full suite/scenario protocols, trial
counts, run seeds, and scenario/trial identities. This keeps scenario constraints, expected
outcomes, failure injections, and budgets matched. The comparison artifact records candidate-minus-
baseline deltas for each paired trial and uses a deterministic paired scenario-cluster bootstrap.

Regression policies declare practical tolerances before comparison. A lower-is-worse metric fails
only when the confidence interval's upper bound is below the allowed decrease; a higher-is-worse
metric fails only when the lower bound is above the allowed increase. Pass-rate decrease and
error-rate increase gates are enabled by default with zero tolerance. Mean latency and mean cost
gates are opt-in because their practical tolerances depend on deployment SLOs and budgets. A passed
gate means this protocol did not detect a regression beyond its threshold; it is not evidence that
the systems are equivalent, especially for small or unrepresentative suites.

## 5. Trace schema direction

Use OpenTelemetry-compatible spans in production. At minimum capture event name, timestamp,
component, duration, status, retry count, sanitized inputs/outputs or hashes, dependency version,
token usage, and cost. Never place secrets or raw sensitive user data in benchmark artifacts.

## 6. Recommended suite families

- golden-path product tasks;
- ambiguous requests and clarification behavior;
- adversarial safety and prompt-injection attempts;
- retrieval conflicts, stale documents, and missing evidence;
- invalid tool output, timeouts, partial outages, and retry storms;
- multi-turn state and memory isolation;
- multilingual and accessibility cases;
- long-context and load/concurrency cases;
- privacy, authorization, and tenant-boundary tests;
- operator diagnostics and incident recovery.

## 7. Validity safeguards

- Sample tasks from real workflows using privacy-safe transformation.
- Have domain experts define success independently of system outputs.
- Measure inter-rater agreement and adjudicate disagreement.
- Include negative controls and evaluator unit tests.
- Report sample sizes and confidence intervals; do not rank statistically tied systems.
- Slice results by domain, risk, difficulty, language, and failure type.
- Detect regressions against a pinned baseline and declare practical significance thresholds.
- Maintain an evaluation threat model: leakage, gaming, judge bias, flaky dependencies,
  nondeterminism, and selective reporting.

## 8. Development roadmap

### Phase 1 — foundation

- Add JSON Schema validation and suite linting.
- Add plugin registries for adapters and evaluators.
- Add p50/p95/p99, bootstrap confidence intervals, Reliability@N, and slice reports. (Implemented.)
- Add subprocess/HTTP adapters with timeouts and secret-safe configuration.

### Phase 2 — realistic systems

- Add sandboxed tool environments and state reset hooks.
- Add fault injection proxies for latency, errors, malformed data, and rate limits.
- Add OpenTelemetry import/export and redaction policies.
- Add human-review queues and calibrated rubric/model judges.

### Phase 3 — governance and scale

- Add distributed execution, concurrency/load tests, and artifact storage.
- Add signed suite manifests, provenance, access control, and audit logs.
- Extend baseline comparison and regression gates with critical-slice policies and richer CI
  integrations. (Matched offline report comparison and process exit gates are implemented.)
- Create private challenge sets and a documented benchmark release process.

## 9. Definition of a trustworthy result

A result is decision-ready only when the suite represents the intended deployment population,
the scoring process is validated, system and suite versions are pinned, repeated-trial uncertainty
is reported, critical slices meet minimum thresholds, failures are inspectable, and another team
can reproduce the run without privileged oral knowledge.

## 10. Public claims and governance

SystemBench results are scoped engineering evidence, not certifications. A public result should
link an immutable system revision, suite version and fingerprint, budget/accounting manifests,
benchmark card, system/model card, scenario dataset card, validation record, and complete safe-to-
share report artifact. State sample counts, uncertainty, weak slices, deviations, and failed trials
beside any headline result.

Do not use a benchmark score alone to claim safety, fairness, compliance, human equivalence, or
fitness for consequential deployment. Follow [VALIDATION_PROTOCOL.md](../VALIDATION_PROTOCOL.md)
and [DEPLOYMENT_BOUNDARIES.md](../DEPLOYMENT_BOUNDARIES.md); record methodology changes under the
change-control rules in [GOVERNANCE.md](../GOVERNANCE.md).
