# Provenance and third-party boundaries

SystemBench's tracked source consists of original framework code, documentation,
and synthetic fixtures. The dependency-free runtime does not bundle model
weights, benchmark datasets, production traces, provider SDKs, or external judge
services.

For every new external component, record:

- exact name, version, source, checksum or immutable identifier, and retrieval date;
- code, model-weight, dataset, output, and API terms separately;
- intended use, data path, network behavior, and secrets required;
- validation evidence, known limitations, and removal or rollback procedure;
- required attribution and redistributed notices.

An open-source client library does not make a hosted model, its weights, its
training data, or its outputs open source. Public availability does not establish
permission to redistribute a dataset or include its examples in a benchmark.

The current package declares only development dependencies (`pytest`, `ruff`, and
`mypy`). GitHub Actions are pinned by major version and reviewed through
Dependabot. Record any future runtime dependency in `NOTICE` when attribution or
redistribution terms require it.
