"""Offline reference system used to verify the harness itself."""

from __future__ import annotations

import re
from typing import ClassVar

from .adapters import SystemAdapter
from .models import Scenario, SystemResult, TraceEvent


class DemoSystem(SystemAdapter):
    name = "offline-demo-system"
    system_manifest: ClassVar[dict[str, object]] = {
        "implementation": "systembench.demo.DemoSystem",
        "release": "0.1.0",
        "network_access": False,
    }

    def execute(self, scenario: Scenario, context: dict[str, object]) -> SystemResult:
        question = str(scenario.input.get("question", ""))
        events = [TraceEvent("request.received", component="gateway")]
        if scenario.failure_injection.get("retrieval_unavailable"):
            events.append(TraceEvent("retrieval.failed", component="retriever"))
            events.append(TraceEvent("fallback.used", component="orchestrator"))
        else:
            events.append(TraceEvent("retrieval.completed", component="retriever"))
        numbers = [int(value) for value in re.findall(r"-?\d+", question)]
        output = str(sum(numbers)) if "sum" in question.lower() and numbers else "unable to answer"
        events.append(TraceEvent("response.returned", component="gateway"))
        return SystemResult(output=output, events=events, cost_usd=0.0)
