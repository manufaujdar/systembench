# SystemBench documentation

Recommended reading order:

1. [`../README.md`](../README.md) — purpose, quick start, metrics, and limits.
2. [`DESIGN.md`](DESIGN.md) — design principles, extension points, and methodology.
3. [`SYSTEM_ARCHITECTURE.md`](SYSTEM_ARCHITECTURE.md) and
   [`INTERACTION_BENCHMARK.md`](INTERACTION_BENCHMARK.md) — executable surfaces.
4. [`../VALIDATION_PROTOCOL.md`](../VALIDATION_PROTOCOL.md), benchmark/model/dataset
   cards, and [`../PROVENANCE.md`](../PROVENANCE.md) — evidence and provenance.
5. [`../PRIVACY_AND_DATA_BOUNDARY.md`](../PRIVACY_AND_DATA_BOUNDARY.md),
   [`../SECURITY.md`](../SECURITY.md), and [`../CONTRIBUTING.md`](../CONTRIBUTING.md)
   — legal, privacy, security, and contribution gates.

## Release boundary

SystemBench is a provider-neutral research framework. A passing report applies
only to its declared suite, budgets, adapters, evaluators, and evidence. It does
not certify safety, fairness, compliance, or fitness for high-impact use. Before
publication, review the Apache-2.0 license, NOTICE, dependency/SBOM inventory,
scenario rights, baseline ownership, and any external model or dataset terms.
