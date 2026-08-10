"""JSON suite loading and report persistence."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .integrity import strict_json_dumps, strict_json_loads
from .models import Scenario, Suite


def load_json_object(path: str | Path, name: str = "JSON document") -> dict[str, Any]:
    data = strict_json_loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{name} must be a JSON object")
    return data


def load_suite(path: str | Path) -> Suite:
    data = load_json_object(path, "suite")
    scenarios = tuple(
        Scenario(
            id=item["id"],
            description=item["description"],
            input=item["input"],
            expected=item.get("expected", {}),
            constraints=item.get("constraints", {}),
            tags=tuple(item.get("tags", [])),
            failure_injection=item.get("failure_injection", {}),
        )
        for item in data["scenarios"]
    )
    if len({scenario.id for scenario in scenarios}) != len(scenarios):
        raise ValueError("scenario IDs must be unique")
    return Suite(data["name"], data["version"], scenarios, data.get("metadata", {}))


def write_report(report: dict[str, Any], output_root: str | Path = "runs") -> Path:
    rendered = strict_json_dumps(report, indent=2) + "\n"
    directory = Path(output_root) / report["run_id"]
    directory.mkdir(parents=True, exist_ok=False)
    path = directory / "report.json"
    path.write_text(rendered, encoding="utf-8")
    return path


def load_report(path: str | Path) -> dict[str, Any]:
    return load_json_object(path, "report")
