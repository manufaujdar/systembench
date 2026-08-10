# Security, privacy, and benchmark integrity

SystemBench should receive synthetic, approved, or safely sanitized inputs and
traces. Do not put credentials, private prompts, personal or patient data,
production identifiers, hidden challenge sets, proprietary outputs, or model
weights in suites, fixtures, reports, logs, or issue discussions.

Report suspected vulnerabilities or evaluation-set exposure through GitHub's
private security-advisory route when available, using a minimal synthetic
reproduction. Do not publicly disclose secrets, exploitable production details,
restricted data, or hidden scenario contents.

The local browser lab binds to loopback, has no external resources or model calls,
does not persist results, and is only a demonstration. A real adapter must define
authentication, authorization, network egress, trace redaction, retention,
deletion, secrets handling, tool-side-effect controls, tenant isolation, incident
response, and rollback before production evaluation.

Prompt injection, evaluator manipulation, scenario leakage, result tampering,
post-hoc exclusions, and judge bias are benchmark-integrity security concerns.
Artifact fingerprints detect content changes but do not verify declarations or
prevent authorized manipulation.

Benchmark output is evidence for a declared engineering protocol, not proof of
clinical, financial, employment, education, legal, or other high-impact safety.
Public source availability does not imply a security SLA or suitability for
sensitive data.
