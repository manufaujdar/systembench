# Adaptive human–system benchmark design

## Decision supported

The workbench helps an evaluation owner decide whether a proposed protocol covers enough realistic
whole-system and human-interaction risk to be frozen for a supervised comparison. It does not score
or certify a live external target. The coverage score describes the protocol, not the AI system.

## Construct map

| Layer | Observable constructs |
|---|---|
| Human interaction | goal completion, clarification, correction, effort, handoff, recoverability |
| Model/knowledge | grounded accuracy, instruction fidelity, uncertainty, context retention |
| Agent/action | goal preservation, tool correctness, permission boundaries, safe stopping |
| Framework/harness | isolation, normalization, reproducibility, accounting, evaluator integrity |
| Feedback loop | convergence, error amplification, stop conditions, long-horizon drift |
| Operations | tail latency, partial outage behavior, retries, idempotency, observability |

System confidence is recorded only to calculate calibration against observed outcomes. It is never
used as ground truth. Hidden reasoning is neither requested nor scored.

## Scenario coverage

Every target type has three initial probe families. Together they cover common human goals,
underspecification, correction, boundary conditions, degraded dependencies, concurrency or state,
and recovery. The first release provides protocol templates rather than claiming representative
deployment samples. Evaluation owners must replace or extend them with privacy-safe scenarios
sampled from their actual workflow population.

## Adaptive policy

The policy is deterministic and visible:

- a pass advances to a different construct;
- a partial outcome repeats the construct with a human correction;
- a failure removes the injected difficulty and performs a diagnostic replay;
- completion stops the planned probe set and requires review.

This adaptation improves diagnosis inside a session. It must not be used to change the frozen
comparison corpus, thresholds, exclusions, or budgets after inspecting candidate results.

## Baseline and budgets

Compare a candidate with the current deployed workflow, including current human effort and failure
handling. Match model access, tools, retrieval, time, retries, latency, and allowed human
interventions. Each probe declares a small budget template; the evaluation owner must replace these
with predeclared deployment-relevant limits before running a comparison.

## Evaluators and evidence

Initial interaction metrics are task success, human ease, calibration gap, and repair rate. A real
suite should also preserve final state, dialogue, tool and policy events, correction scope,
side-effect ledger, trace lineage, latency, cost, and reviewer evidence. Outcome labels need a
prespecified rubric, blinded review when feasible, disagreement measurement, and adjudication.

## Statistical plan

Repeat every scenario and report failures, Reliability@N, scenario-cluster confidence intervals,
tail latency, cost, human effort, repair rate, and worst declared user/context slices. Do not treat
multiple turns or trials within one scenario as independent task samples.

## Validity threats

- template probes may not represent the deployment population;
- public scenarios can be contaminated or gamed;
- adaptive paths create unequal samples unless the policy and budgets are frozen;
- human effort scales require reviewer training and agreement checks;
- confidence may be absent or incomparable across systems;
- a deterministic checklist can reward documentation rather than true implementation;
- local synthetic operation does not reproduce provider, network, or production drift.

## Frozen fields before comparison

Freeze target releases, scenario set and sampling, adaptive policy, budgets, evaluators, pass rules,
trial count, seeds, exclusions, human-review protocol, manifests, and analysis code. Version any
change and do not reuse earlier results as if they were produced under the new protocol.
