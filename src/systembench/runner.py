"""Trial orchestration, exception isolation, and result aggregation."""

from __future__ import annotations

import platform
import time
import uuid
from collections.abc import Mapping
from dataclasses import asdict
from math import ceil
from typing import Any

from .adapters import SystemAdapter
from .evaluators import Evaluator
from .integrity import artifact_fingerprint, fingerprint, finite_number, json_snapshot, manifest
from .models import Suite, SystemResult, TrialResult, utc_now
from .statistics import report_confidence_intervals, validate_bootstrap_config


def _nearest_rank(values: list[float], percentile: float) -> float:
    """Return a deterministic nearest-rank percentile for a non-empty sample."""

    if not values:
        return 0.0
    if not 0 <= percentile <= 100:
        raise ValueError("percentile must be between 0 and 100")
    ordered = sorted(values)
    index = max(0, ceil((percentile / 100) * len(ordered)) - 1)
    return ordered[index]


def _result_metrics(results: list[TrialResult]) -> dict[str, Any]:
    """Summarize a result subset without changing the underlying trial evidence."""

    if not results:
        return {"trial_count": 0, "scenario_count": 0, "pass_rate": 0.0, "reliability_at_n": 0.0}
    scenario_trials: dict[str, list[TrialResult]] = {}
    for result in results:
        scenario_trials.setdefault(result.scenario_id, []).append(result)
    return {
        "trial_count": len(results),
        "scenario_count": len(scenario_trials),
        "pass_rate": sum(result.passed for result in results) / len(results),
        "reliability_at_n": sum(
            all(trial.passed for trial in trials_for_scenario)
            for trials_for_scenario in scenario_trials.values()
        )
        / len(scenario_trials),
    }


def _validate_suite(suite: Suite) -> None:
    if not suite.name or not suite.version:
        raise ValueError("suite name and version must be non-empty")
    if not suite.scenarios:
        raise ValueError("suite must declare at least one scenario")
    scenario_ids = [scenario.id for scenario in suite.scenarios]
    if any(not scenario_id for scenario_id in scenario_ids):
        raise ValueError("scenario IDs must be non-empty")
    if len(set(scenario_ids)) != len(scenario_ids):
        raise ValueError("scenario IDs must be unique")
    json_snapshot(asdict(suite))


def _validate_system_result(result: SystemResult) -> None:
    result.latency_ms = finite_number(result.latency_ms, "system_result.latency_ms", minimum=0.0)
    result.cost_usd = finite_number(result.cost_usd, "system_result.cost_usd", minimum=0.0)
    if not isinstance(result.token_usage, dict):
        raise TypeError("system_result.token_usage must be an object")
    for name, value in result.token_usage.items():
        if not isinstance(name, str) or not name:
            raise ValueError("system_result.token_usage keys must be non-empty strings")
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"system_result.token_usage.{name} must be a non-negative integer")
    json_snapshot(asdict(result))


class BenchmarkRunner:
    def __init__(self, adapter: SystemAdapter, evaluators: list[Evaluator]) -> None:
        self.adapter = adapter
        self.evaluators = evaluators

    def run(
        self,
        suite: Suite,
        trials: int = 1,
        seed: int = 0,
        *,
        bootstrap_samples: int = 2000,
        confidence_level: float = 0.95,
        bootstrap_seed: int | None = None,
        system_manifest: Mapping[str, Any] | None = None,
        budget_manifest: Mapping[str, Any] | None = None,
        accounting_manifest: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        _validate_suite(suite)
        if isinstance(trials, bool) or not isinstance(trials, int) or trials < 1:
            raise ValueError("trials must be an integer of at least 1")
        validate_bootstrap_config(bootstrap_samples, confidence_level)
        resolved_bootstrap_seed = seed if bootstrap_seed is None else bootstrap_seed
        run_id = f"{suite.name}-{uuid.uuid4().hex[:10]}"
        results: list[TrialResult] = []
        started_at = utc_now()

        for scenario in suite.scenarios:
            for trial in range(1, trials + 1):
                trial_started = utc_now()
                clock = time.perf_counter()
                try:
                    context = {"run_id": run_id, "trial": trial, "seed": seed + trial - 1}
                    system_result = self.adapter.execute(scenario, context)
                    if not isinstance(system_result, SystemResult):
                        raise TypeError("adapter must return SystemResult")
                    if not system_result.latency_ms:
                        system_result.latency_ms = (time.perf_counter() - clock) * 1000
                except Exception as exc:  # noqa: BLE001 - adapters are an isolation boundary
                    system_result = SystemResult(
                        latency_ms=(time.perf_counter() - clock) * 1000,
                        error=f"{type(exc).__name__}: {exc}",
                    )

                _validate_system_result(system_result)
                evaluations = [e.evaluate(scenario, system_result) for e in self.evaluators]
                results.append(TrialResult(scenario.id, trial, system_result, evaluations, trial_started))

        passed = sum(result.passed for result in results)
        metric_scores: dict[str, list[float]] = {}
        for result in results:
            for evaluation in result.evaluations:
                metric_scores.setdefault(evaluation.metric, []).append(evaluation.score)

        total = len(results)
        latencies = [result.system_result.latency_ms for result in results]
        scenario_trials: dict[str, list[TrialResult]] = {}
        for result in results:
            scenario_trials.setdefault(result.scenario_id, []).append(result)
        reliability_at_n = _result_metrics(results)["reliability_at_n"]
        scenario_tags = {scenario.id: set(scenario.tags) for scenario in suite.scenarios}
        tags = sorted({tag for scenario in suite.scenarios for tag in scenario.tags})
        slices = {
            tag: _result_metrics(
                [result for result in results if tag in scenario_tags[result.scenario_id]]
            )
            for tag in tags
        }
        suite_snapshot = json_snapshot(asdict(suite))
        declared_system = system_manifest
        if declared_system is None:
            declared_system = self.adapter.system_manifest
        system_identity = manifest(
            {"name": self.adapter.name, "configuration": dict(declared_system or {})},
            completeness="declared" if declared_system is not None else "name_only",
        )
        budget_identity = manifest(
            {
                "trials_per_scenario": trials,
                "scenario_constraints": {
                    scenario.id: json_snapshot(scenario.constraints) for scenario in suite.scenarios
                },
                "additional": dict(budget_manifest or {}),
            }
        )
        accounting_identity = manifest(
            {
                "resource_metrics": {
                    "latency_ms": {
                        "unit": "milliseconds",
                        "source": "adapter value, or runner end-to-end wall clock when zero",
                        "required": True,
                    },
                    "cost_usd": {"unit": "USD", "source": "adapter", "required": True},
                    "token_usage": {
                        "unit": "tokens",
                        "source": "adapter",
                        "required": True,
                    },
                },
                "trial_pass_rule": "no system error and every evaluator passes",
                "evaluators": [e.name for e in self.evaluators],
                "additional": dict(accounting_manifest or {}),
            }
        )
        report = {
            "schema_version": "1.1",
            "run_id": run_id,
            "started_at": started_at,
            "completed_at": utc_now(),
            "suite": suite_snapshot,
            "system": self.adapter.name,
            "manifests": {
                "system": system_identity,
                "budget": budget_identity,
                "accounting": accounting_identity,
            },
            "fingerprints": {
                "suite": fingerprint(suite_snapshot),
                "system": system_identity["fingerprint"],
                "budget": budget_identity["fingerprint"],
                "accounting": accounting_identity["fingerprint"],
            },
            "configuration": {
                "trials": trials,
                "seed": seed,
                "bootstrap_samples": bootstrap_samples,
                "confidence_level": confidence_level,
                "bootstrap_seed": resolved_bootstrap_seed,
            },
            "summary": {
                "trial_count": total,
                "passed_trials": passed,
                "pass_rate": passed / total if total else 0.0,
                "error_rate": sum(bool(r.system_result.error) for r in results) / total if total else 0.0,
                "mean_latency_ms": (
                    sum(r.system_result.latency_ms for r in results) / total if total else 0.0
                ),
                "latency_percentiles_ms": {
                    "p50": _nearest_rank(latencies, 50),
                    "p95": _nearest_rank(latencies, 95),
                    "p99": _nearest_rank(latencies, 99),
                },
                "total_cost_usd": sum(r.system_result.cost_usd for r in results),
                "mean_cost_usd": (
                    sum(r.system_result.cost_usd for r in results) / total if total else 0.0
                ),
                "reliability_at_n": reliability_at_n,
                "scenario_count": len(scenario_trials),
                "slices": slices,
                "mean_metric_scores": {
                    name: sum(scores) / len(scores) for name, scores in metric_scores.items()
                },
                "confidence_intervals": report_confidence_intervals(
                    results,
                    samples=bootstrap_samples,
                    confidence_level=confidence_level,
                    seed=resolved_bootstrap_seed,
                ),
            },
            "environment": {"python": platform.python_version(), "platform": platform.platform()},
            "results": [result.to_dict() for result in results],
        }
        report["report_fingerprint"] = artifact_fingerprint(report, "report_fingerprint")
        return report
