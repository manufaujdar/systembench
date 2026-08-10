"""Deterministic repository audit and supervised external-agent brief generator."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

DEFAULT_ROOT = Path(__file__).resolve().parents[2]
REQUIRED_FILES = (
    "README.md",
    "LICENSE",
    "NOTICE",
    "CITATION.cff",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    "GOVERNANCE.md",
    "DEPLOYMENT_BOUNDARIES.md",
    "VALIDATION_PROTOCOL.md",
    "BENCHMARK_CARD_TEMPLATE.md",
    "MODEL_CARD_TEMPLATE.md",
    "DATASET_CARD_TEMPLATE.md",
    "PROVENANCE.md",
)
SUSPICIOUS_TRACKED_PATTERNS = (
    re.compile(r"(^|/)(\.env|id_rsa|credentials?|secrets?)(\.|/|$)", re.IGNORECASE),
    re.compile(
        r"(^|/)(private|production)[-_ ]?(prompts?|traces?|evals?)(\.|/|$)",
        re.IGNORECASE,
    ),
    re.compile(r"\.(pem|key|p12|pfx)$", re.IGNORECASE),
)


@dataclass(frozen=True)
class Finding:
    severity: str
    area: str
    title: str
    detail: str
    next_action: str


@dataclass(frozen=True)
class AgentProfile:
    name: str
    executable: str
    strengths: tuple[str, ...]
    tradeoffs: tuple[str, ...]
    source: str


AGENTS = (
    AgentProfile(
        "Codex",
        "codex",
        ("repository-aware edits", "test and command loop", "project instructions"),
        ("provider-managed", "external data terms require review"),
        "https://developers.openai.com/codex/",
    ),
    AgentProfile(
        "Claude Code",
        "claude",
        ("multi-file work", "terminal workflow", "repository context"),
        ("provider-managed", "separate account and data terms"),
        "https://code.claude.com/docs/en/overview",
    ),
    AgentProfile(
        "Gemini CLI",
        "gemini",
        ("open-source harness", "terminal workflow", "repository exploration"),
        ("model/API terms are separate", "review configuration is user-owned"),
        "https://github.com/google-gemini/gemini-cli",
    ),
    AgentProfile(
        "OpenHands",
        "openhands",
        ("composable agent framework", "provider flexibility", "self-hosting options"),
        ("higher setup cost", "sandbox and tool policy require design"),
        "https://docs.openhands.dev/",
    ),
)


def _read(root: Path, relative: str) -> str:
    path = root / relative
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _tracked_files(root: Path) -> list[str]:
    try:
        process = subprocess.run(
            ["git", "ls-files"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return []
    return sorted(line for line in process.stdout.splitlines() if line)


def _extract(pattern: str, text: str) -> str | None:
    match = re.search(pattern, text, flags=re.MULTILINE)
    return match.group(1).strip() if match else None


def audit_repository(root: Path = DEFAULT_ROOT) -> dict[str, Any]:
    findings: list[Finding] = []
    missing = [relative for relative in REQUIRED_FILES if not (root / relative).is_file()]
    if missing:
        findings.append(
            Finding(
                "high",
                "governance",
                "Public-project records are incomplete",
                "Missing: " + ", ".join(missing),
                "Add and review each required record before a public release.",
            )
        )

    pyproject = _read(root, "pyproject.toml")
    package_init = _read(root, "src/systembench/__init__.py")
    citation = _read(root, "CITATION.cff")
    versions = {
        "pyproject": _extract(r'^version\s*=\s*"([^"]+)"', pyproject),
        "package": _extract(r'^__version__\s*=\s*"([^"]+)"', package_init),
        "citation": _extract(r"^version:\s*([^\s#]+)", citation),
    }
    declared_versions = {value for value in versions.values() if value}
    if len(declared_versions) != 1 or None in versions.values():
        findings.append(
            Finding(
                "high",
                "release",
                "Version declarations do not align",
                json.dumps(versions, sort_keys=True),
                "Use one reviewed version in package metadata, code, and citation metadata.",
            )
        )

    license_text = _read(root, "LICENSE")
    if "Apache License" not in license_text or 'license = {text = "Apache-2.0"}' not in pyproject:
        findings.append(
            Finding(
                "high",
                "licensing",
                "Apache-2.0 declarations are incomplete",
                "The package declaration and full license text must agree.",
                "Reconcile LICENSE, NOTICE, CITATION.cff, and pyproject.toml.",
            )
        )

    workflow = _read(root, ".github/workflows/ci.yml")
    if "permissions:\n  contents: read" not in workflow:
        findings.append(
            Finding(
                "high",
                "security",
                "CI permissions are not explicitly read-only",
                "The main workflow lacks an explicit top-level contents: read permission.",
                "Declare least-privilege workflow permissions.",
            )
        )

    readme_and_boundary = (_read(root, "README.md") + _read(root, "DEPLOYMENT_BOUNDARIES.md")).lower()
    for concept in ("not a certification", "high-impact", "offline", "synthetic"):
        if concept not in readme_and_boundary:
            findings.append(
                Finding(
                    "medium",
                    "truthfulness",
                    f"Missing public boundary: {concept}",
                    "A reader could overgeneralize a benchmark result or the demo environment.",
                    f"State the {concept!r} boundary in public-facing documentation.",
                )
            )

    tracked = _tracked_files(root)
    suspicious = [
        path for path in tracked if any(pattern.search(path) for pattern in SUSPICIOUS_TRACKED_PATTERNS)
    ]
    if suspicious:
        findings.append(
            Finding(
                "high",
                "data_safety",
                "Tracked filenames may contain sensitive material",
                "Review: " + ", ".join(suspicious),
                "Remove secrets/private evaluation material from history and rotate exposed credentials.",
            )
        )

    scores = {
        "governance": 10,
        "release": 10,
        "licensing": 10,
        "security": 10,
        "truthfulness": 10,
        "data_safety": 10,
    }
    deductions = {"high": 4, "medium": 2, "low": 1}
    for finding in findings:
        scores[finding.area] = max(0, scores[finding.area] - deductions[finding.severity])

    return {
        "tool": "systembench-repository-review-agent",
        "mode": "local_deterministic_audit",
        "root": str(root),
        "versions": versions,
        "tracked_file_count": len(tracked),
        "required_files_checked": list(REQUIRED_FILES),
        "scores": scores,
        "findings": [asdict(finding) for finding in findings],
        "limitations": [
            "presence and consistency checks do not establish benchmark validity",
            "filename checks do not inspect Git history or prove that content is non-sensitive",
            "legal, security, accessibility, and methodological review remain human responsibilities",
        ],
        "external_model_calls": False,
        "files_modified": False,
    }


def compare_agents() -> dict[str, Any]:
    profiles = [
        {**asdict(profile), "available_on_path": shutil.which(profile.executable) is not None}
        for profile in AGENTS
    ]
    return {
        "method": "capability matrix, not an AI performance benchmark",
        "evaluation_rubric": [
            {"criterion": "methodology preservation", "weight": 25},
            {"criterion": "evidence and test quality", "weight": 20},
            {"criterion": "privacy and security boundaries", "weight": 15},
            {"criterion": "small maintainable changes", "weight": 15},
            {"criterion": "clear non-overclaiming documentation", "weight": 15},
            {"criterion": "reproducible review trail", "weight": 10},
        ],
        "selection_rule": (
            "Use the same frozen brief and repository revision; a human reviews every proposed "
            "change before release. Do not select an agent from marketing claims or this matrix alone."
        ),
        "agents": profiles,
    }


def review_prompt(audit: dict[str, Any], comparison: dict[str, Any]) -> str:
    return f"""Review SystemBench, a provider-neutral framework for evaluating complete AI systems.

Constraints:
- Evaluate observable system outcomes; never request or score hidden chain-of-thought.
- Do not claim a score proves safety, fairness, compliance, equivalence, or human capability.
- Preserve matched protocols, trial evidence, failures, manifests, and uncertainty.
- Do not tune scenarios, evaluators, thresholds, exclusions, or budgets after viewing results.
- Do not upload private scenarios, prompts, traces, personal data, credentials, or model artifacts.
- Keep the offline example dependency-free and provider-neutral.
- Return a proposed patch plan first; do not edit until a human approves it.

Deterministic repository audit:
{json.dumps(audit, indent=2, sort_keys=True)}

Agent capability matrix:
{json.dumps(comparison, indent=2, sort_keys=True)}

Deliver:
1. The three most important validity or reliability risks.
2. Exact evidence for each finding and a bounded remediation.
3. Tests and negative controls needed before release.
4. Any privacy, provenance, licensing, or deployment boundary affected.
5. A short patch plan naming files, with unsupported claims explicitly rejected.
"""


def _print(payload: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif isinstance(payload, dict) and "findings" in payload:
        print(f"{payload['tool']} · {payload['mode']}")
        print("Scores: " + ", ".join(f"{name}={score}/10" for name, score in payload["scores"].items()))
        for finding in payload["findings"]:
            print(f"- [{finding['severity']}] {finding['area']}: {finding['title']}")
        print("Limitations: " + "; ".join(payload["limitations"]))
    else:
        print(payload if isinstance(payload, str) else json.dumps(payload, indent=2, sort_keys=True))


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit SystemBench public-project readiness")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--json", action="store_true")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("audit", "compare", "prompt"):
        subparsers.add_parser(command).add_argument("--json", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.command == "audit":
        _print(audit_repository(args.root), args.json)
    elif args.command == "compare":
        _print(compare_agents(), args.json)
    else:
        _print(review_prompt(audit_repository(args.root), compare_agents()), False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
