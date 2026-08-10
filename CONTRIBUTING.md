# Contributing

SystemBench is a methodology-sensitive evaluation framework. Keep adapters,
evaluators, traces, aggregation, and reports modular, and preserve enough
evidence for another team to reproduce a result.

Before opening a pull request:

```bash
pytest
ruff check .
mypy src tests
python -m compileall -q src tests tools
python tools/repository_agent/repository_agent.py audit --json
```

Do not tune scenarios, rubrics, thresholds, budgets, trial plans, or exclusions
after observing results without recording the change and assigning a new protocol
version. Use the project design skill before methodology-sensitive changes and an
independent validity review before publishing conclusions.

Keep examples offline and synthetic. Never commit secrets, personal data,
production prompts or traces, hidden evaluation data, licensed model weights, or
proprietary system artifacts. Document the source, exact version, terms, data path,
and validation boundary of every third-party model, dataset, evaluator, service,
or library.

Contributors must have the right to submit their work under Apache-2.0. SystemBench
does not currently require a CLA or DCO, but contributors remain responsible for
their copyright, data-use, and confidentiality obligations.
