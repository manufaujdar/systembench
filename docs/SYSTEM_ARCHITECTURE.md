# SystemBench workbench architecture

## Product boundary

The website is a local protocol-design and interaction-recording workbench. It does not call an
external model or execute arbitrary tools. Real systems connect through `SystemAdapter` only after
their network, authentication, side-effect, data, and reset boundaries have been reviewed.

```text
Browser workbench
  ├─ design assessment ───────────────┐
  ├─ adaptive observation form ───────┤
  └─ synthetic harness smoke test ────┤
                                      v
Loopback JSON API
  ├─ /api/catalog
  ├─ /api/analyze
  ├─ /api/session/start
  ├─ /api/session/observe
  └─ /api/run
                 │
       ┌─────────┴──────────┐
       v                    v
Interaction engine      Benchmark runner
  constructs              scenarios × trials
  gap rules               adapters
  target probes           evaluators
  adaptive policy         manifests
  session integrity       uncertainty
       │                    │
       └─────────┬──────────┘
                 v
       reviewable JSON evidence
```

## Frontend

The packaged frontend is plain semantic HTML, CSS, and JavaScript. It has no CDN, framework,
analytics, external font, cookie, or browser persistence dependency. Dynamic values are inserted
with `textContent` and created DOM nodes. The primary surfaces are:

1. benchmark design assessment;
2. construct-coverage and evidence-gap scorecard;
3. expandable target-specific interaction probes;
4. outcome-driven adaptive session and human-effort/calibration metrics;
5. common benchmark failure modes and whole-system causal map;
6. the original deterministic offline runner smoke test.

## Backend and API contracts

The standard-library HTTP server binds to loopback. Requests use strict JSON, must be objects, and
are limited to 128 KiB. Responses use strict finite JSON and `no-store`, self-only Content Security
Policy, MIME-sniffing protection, no-referrer policy, and same-origin opener policy.

| Route | Method | Purpose |
|---|---|---|
| `/api/catalog` | GET | Target types, constructs, methods, and conventional benchmark problems |
| `/api/analyze` | POST | Validate a proposed protocol and return coverage, gaps, probes, and fingerprint |
| `/api/session/start` | POST | Create the first target-specific adaptive probe and sealed session state |
| `/api/session/observe` | POST | Validate state, record an outcome, update metrics, and select the next probe |
| `/api/run` | POST | Run the bundled deterministic suite with 1–10 trials per scenario |

The browser holds session state and sends it back for each observation. A fingerprint detects
accidental or casual mutation; it is not authentication or a server signature. Production use
would require server-held state or authenticated signatures, authorization, retention/deletion,
audit policy, rate limiting, and CSRF/origin controls.

## Adaptive engine

`interaction.py` contains six target profiles and observable probes:

- LLM: clarification, conflicting evidence, correction;
- agent: permission boundary, interruption, degraded tool recovery;
- framework: provider substitution, nested failure, concurrent state isolation;
- harness: replay, malformed evidence, evaluator bias control;
- loop: noisy-feedback convergence, long-horizon drift, stop conditions;
- system: uncertain handoff, messy end-to-end journey, ambiguous outage recovery.

The policy is intentionally small and deterministic. It chooses among a different construct,
human-repair probe, or simpler diagnostic replay. It does not optimize a score, use hidden model
reasoning, or rewrite frozen thresholds.

## Evaluation harness

The existing runner remains the execution boundary for real comparisons. A `SystemAdapter` wraps
the whole system and returns output, structured events, error, latency, cost, token usage, and
metadata. Evaluators return score, pass decision, explanation, and evidence. Reports retain the
full scenario × trial grid, manifests, fingerprints, slices, Reliability@N, percentiles, and
scenario-cluster bootstrap intervals.

## Human review and ground truth

The website records pass/partial/fail, human effort, expressed system confidence, and an evidence
note. These are research inputs, not validated labels. A decision-ready deployment protocol must
define reviewer training, blinding, rubric, disagreement, adjudication, accessibility, sampling,
consent/privacy, and exclusions before comparison.

## Future integration seams

1. Add a reviewed HTTP or subprocess adapter with explicit timeouts and secret-safe configuration.
2. Add a sandboxed human-task environment with state snapshots and idempotent side-effect ledgers.
3. Add authenticated, server-held study sessions and role-based review queues.
4. Export/import OpenTelemetry spans with redaction and component-version manifests.
5. Add preregistered adaptive policies and matched-path statistical analysis for comparative runs.
6. Add representative private challenge sets under separate access and contamination governance.
