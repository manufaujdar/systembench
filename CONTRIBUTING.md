# Contributing

SystemBench is a methodology-sensitive evaluation framework. Keep adapters,
evaluators, traces, aggregation, and reports modular, and preserve enough
evidence for another team to reproduce a result.

Before opening a pull request:

```bash
pytest
ruff check .
mypy src tests
```

Do not tune scenarios, rubrics, thresholds, or exclusions after observing
results without recording the change. Keep examples offline and synthetic;
never commit secrets, raw private traces, or hidden evaluation data.
