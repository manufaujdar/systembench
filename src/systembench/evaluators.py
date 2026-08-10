"""Evidence-producing evaluators for system-level properties."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .models import Evaluation, Scenario, SystemResult


class Evaluator(ABC):
    name: str

    @abstractmethod
    def evaluate(self, scenario: Scenario, result: SystemResult) -> Evaluation:
        pass


class ExactMatchEvaluator(Evaluator):
    name = "exact_match"

    def evaluate(self, scenario: Scenario, result: SystemResult) -> Evaluation:
        expected = scenario.expected.get("output")
        actual = result.output
        score = float(actual == expected)
        return Evaluation(
            metric=self.name,
            score=score,
            passed=bool(score),
            explanation="Output matched expected value." if score else "Output did not match.",
            evidence={"expected": expected, "actual": actual},
        )


class ContainsEvaluator(Evaluator):
    name = "contains_required_terms"

    def evaluate(self, scenario: Scenario, result: SystemResult) -> Evaluation:
        required = [str(x).lower() for x in scenario.expected.get("contains", [])]
        actual = str(result.output).lower()
        matched = [term for term in required if term in actual]
        score = len(matched) / len(required) if required else 1.0
        threshold = float(scenario.constraints.get("content_threshold", 1.0))
        return Evaluation(
            metric=self.name,
            score=score,
            passed=score >= threshold,
            explanation=f"Matched {len(matched)} of {len(required)} required terms.",
            evidence={"required": required, "matched": matched, "threshold": threshold},
        )


class LatencySLOEvaluator(Evaluator):
    name = "latency_slo"

    def evaluate(self, scenario: Scenario, result: SystemResult) -> Evaluation:
        configured_limit = scenario.constraints.get("max_latency_ms")
        if configured_limit is None:
            return Evaluation(
                metric=self.name,
                score=1.0,
                passed=True,
                explanation="No latency limit was declared.",
                evidence={"actual_ms": result.latency_ms, "limit_ms": None},
            )
        limit = float(configured_limit)
        passed = result.latency_ms <= limit
        score = 1.0 if passed else max(0.0, limit / result.latency_ms) if result.latency_ms else 0.0
        return Evaluation(
            metric=self.name,
            score=score,
            passed=passed,
            explanation=f"Latency was {result.latency_ms:.2f} ms; limit was {limit:.2f} ms.",
            evidence={"actual_ms": result.latency_ms, "limit_ms": limit},
        )


class CostSLOEvaluator(Evaluator):
    name = "cost_slo"

    def evaluate(self, scenario: Scenario, result: SystemResult) -> Evaluation:
        configured_limit = scenario.constraints.get("max_cost_usd")
        if configured_limit is None:
            return Evaluation(
                metric=self.name,
                score=1.0,
                passed=True,
                explanation="No cost limit was declared.",
                evidence={"actual_usd": result.cost_usd, "limit_usd": None},
            )
        limit = float(configured_limit)
        passed = result.cost_usd <= limit
        score = 1.0 if passed else max(0.0, limit / result.cost_usd) if result.cost_usd else 0.0
        return Evaluation(
            metric=self.name,
            score=score,
            passed=passed,
            explanation=f"Cost was ${result.cost_usd:.6f}; limit was ${limit:.6f}.",
            evidence={"actual_usd": result.cost_usd, "limit_usd": limit},
        )


class RequiredEventEvaluator(Evaluator):
    name = "required_trace_events"

    def evaluate(self, scenario: Scenario, result: SystemResult) -> Evaluation:
        required = set(scenario.expected.get("required_events", []))
        observed = {event.name for event in result.events}
        missing = sorted(required - observed)
        score = (len(required) - len(missing)) / len(required) if required else 1.0
        return Evaluation(
            metric=self.name,
            score=score,
            passed=not missing,
            explanation="All required events observed." if not missing else "Required events missing.",
            evidence={"required": sorted(required), "observed": sorted(observed), "missing": missing},
        )


def default_evaluators() -> list[Evaluator]:
    return [ContainsEvaluator(), LatencySLOEvaluator(), CostSLOEvaluator(), RequiredEventEvaluator()]
