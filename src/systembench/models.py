"""Stable data contracts shared by runners, adapters, evaluators, and reporters."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from .integrity import finite_number, positive_int


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class Scenario:
    id: str
    description: str
    input: dict[str, Any]
    expected: dict[str, Any] = field(default_factory=dict)
    constraints: dict[str, Any] = field(default_factory=dict)
    tags: tuple[str, ...] = ()
    failure_injection: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Suite:
    name: str
    version: str
    scenarios: tuple[Scenario, ...]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TraceEvent:
    name: str
    timestamp: str = field(default_factory=utc_now)
    component: str = "system"
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemResult:
    output: Any = None
    events: list[TraceEvent] = field(default_factory=list)
    latency_ms: float = 0.0
    cost_usd: float = 0.0
    token_usage: dict[str, int] = field(default_factory=dict)
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Evaluation:
    metric: str
    score: float
    passed: bool
    explanation: str
    evidence: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.metric:
            raise ValueError("evaluation metric must be non-empty")
        score = finite_number(self.score, f"evaluation {self.metric} score")
        if not 0.0 <= score <= 1.0:
            raise ValueError(f"evaluation {self.metric} score must be between 0 and 1")
        if not isinstance(self.passed, bool):
            raise TypeError(f"evaluation {self.metric} passed must be boolean")


@dataclass
class TrialResult:
    scenario_id: str
    trial: int
    system_result: SystemResult
    evaluations: list[Evaluation]
    started_at: str

    def __post_init__(self) -> None:
        positive_int(self.trial, "trial")

    @property
    def passed(self) -> bool:
        return self.system_result.error is None and all(item.passed for item in self.evaluations)

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["passed"] = self.passed
        return value
