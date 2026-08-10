# Deployment and high-impact-use boundaries

SystemBench is research and engineering software. It is not a certification
service, safety case, conformity assessment, regulatory approval, or substitute
for domain-specific validation and governance.

## Current safeguards

- The default system and suite are deterministic, synthetic, local, and offline.
- Strict JSON parsing rejects duplicate members and non-finite values.
- Trial grids, resource measurements, evaluator scores, and manifests are
  validated before matched comparisons.
- Suite, system, budget, accounting, policy, report, and comparison fingerprints
  make accidental or undisclosed artifact mutation detectable.
- Repeated-trial uncertainty is clustered by scenario rather than treating
  correlated trials as independent tasks.
- Comparison rejects unmatched protocols and preserves paired trial evidence.

Fingerprints prove content identity, not truthfulness. Passing a regression gate
means only that the declared test protocol did not detect a regression beyond its
predeclared tolerance.

## Required before consequential use

1. Define the intended decision, affected people, operating context, failure
   severity, escalation path, and accountable owner.
2. Establish lawful data access, minimization, retention, deletion, security,
   incident response, and access control for prompts, traces, and human labels.
3. Validate scenario representativeness, scoring reliability, contamination risk,
   subgroup coverage, uncertainty, and external reproducibility.
4. Independently review model judges, human-review protocols, reference answers,
   thresholds, exclusions, and conflicts of interest.
5. Test prompt injection, authorization, privacy boundaries, tool side effects,
   fallback behavior, monitoring, rollback, and production drift.
6. Obtain domain, legal, privacy, security, accessibility, and regulatory review
   appropriate to the actual deployment.

Do not describe a SystemBench score as proof that an AI system is safe, unbiased,
truthful, compliant, human-equivalent, or fit for clinical, employment, credit,
education, legal, or other high-impact decisions.
