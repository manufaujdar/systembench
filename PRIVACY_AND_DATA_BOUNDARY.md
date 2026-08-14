# Privacy and data boundary

Status: source distribution and offline benchmark use only. This file is a
technical privacy boundary, not a jurisdiction-specific privacy policy for a
hosted evaluation service.

## Current distribution

The bundled runner, examples, and browser lab are intended to run locally with
synthetic or approved, safely sanitized inputs. The repository does not include
accounts, advertising, a hosted data service, private evaluation sets,
production prompts, personal records, model weights, or provider traces. A
future adapter may process prompts, outputs, traces, or identifiers outside the
repository; that behavior is not covered by the source-only default.

## Deployment responsibility

Any operator who evaluates real systems or stores benchmark artifacts must
define the data owner, permitted data class, lawful basis or authorization,
access controls, provider and evaluator terms, retention/deletion, region and
transfer rules, redaction, incident response, and approval for restricted or
high-impact data. The operator must publish any user-facing privacy notice and
terms of service required by its deployment. This repository does not provide
those notices.

## Legal and integrity boundary

The Apache-2.0 `LICENSE` governs the source code. It does not grant rights to
third-party datasets, model weights, prompts, outputs, provider services, or
evaluation artifacts. See `NOTICE`, `PROVENANCE.md`, `SECURITY.md`, and
`VALIDATION_PROTOCOL.md` before adding or redistributing any component.

Reviewed: 2026-08-14.
