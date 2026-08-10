"""Interfaces for connecting SystemBench to a system under test."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, ClassVar

from .models import Scenario, SystemResult


class SystemAdapter(ABC):
    """Wrap the whole deployed pipeline, not merely a model completion call."""

    name: str = "unnamed-system"
    system_manifest: ClassVar[dict[str, Any] | None] = None

    @abstractmethod
    def execute(self, scenario: Scenario, context: dict[str, Any]) -> SystemResult:
        """Execute one isolated trial and return output plus observability data."""


class FunctionAdapter(SystemAdapter):
    """Convenience adapter for local prototypes and test harnesses."""

    def __init__(
        self,
        function: Callable[[Scenario, dict[str, Any]], SystemResult],
        name: str = "function-adapter",
    ) -> None:
        self.function = function
        self.name = name

    def execute(self, scenario: Scenario, context: dict[str, Any]) -> SystemResult:
        return self.function(scenario, context)
