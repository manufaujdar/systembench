# SystemBench repository review agent

This local, deterministic agent audits public-project readiness and benchmark
truthfulness. It does not call a model, upload repository content, edit files, or
declare a benchmark valid.

```bash
python tools/repository_agent/repository_agent.py audit
python tools/repository_agent/repository_agent.py compare --json
python tools/repository_agent/repository_agent.py prompt > /tmp/systembench-review.md
```

The audit checks required governance files, package/citation version alignment,
license declarations, least-privilege CI, synthetic/offline example boundaries,
high-impact-use warnings, and suspicious tracked filenames. These are repository
signals, not substitutes for human security, legal, accessibility, or validity
review.

The agent matrix is a capability comparison, not a performance benchmark. If an
external coding or review agent is used, give every candidate the same repository
revision, bounded brief, tests, and evaluation rubric. Do not upload private
scenarios, production prompts or traces, personal data, credentials, or restricted
model artifacts.
