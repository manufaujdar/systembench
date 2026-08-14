## Summary

Describe the change and the evaluation decision it supports.

## Validation

- [ ] `pytest`
- [ ] `ruff check .`
- [ ] `mypy src tests`
- [ ] `python -m compileall -q src tests tools`
- [ ] `python tools/repository_agent/repository_agent.py audit --json`
- [ ] Browser lab checked if `web.py` changed
- [ ] Documentation and changelog updated for behavior or release changes

## Methodology, safety, and provenance

- [ ] Scenario, evaluator, threshold, budget, exclusion, and trial changes were
      declared before viewing candidate results, or the post-hoc change is recorded
- [ ] Comparison protocols remain matched and trial-level failures remain visible
- [ ] No private prompts, traces, personal data, credentials, hidden sets, or model weights included
- [ ] New third-party code, models, data, services, and assets have documented terms
- [ ] Benchmark, model/system, or dataset cards are included where relevant
- [ ] No unsupported safety, fairness, equivalence, human-level, or deployment claim added
