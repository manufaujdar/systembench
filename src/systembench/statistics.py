"""Dependency-free statistical helpers for auditable benchmark reports."""

from __future__ import annotations

import random
from collections.abc import Callable, Mapping, Sequence
from math import ceil
from typing import Any

from .integrity import finite_number, positive_int

MIN_BOOTSTRAP_SAMPLES = 100


def validate_bootstrap_config(samples: int, confidence_level: float) -> None:
    positive_int(samples, "bootstrap samples", minimum=MIN_BOOTSTRAP_SAMPLES)
    level = finite_number(confidence_level, "confidence level")
    if not 0.0 < level < 1.0:
        raise ValueError("confidence level must be between 0 and 1")


def bootstrap_support(scenario_count: int, trial_count: int) -> dict[str, Any]:
    warnings: list[str] = []
    if scenario_count < 2:
        warnings.append("Fewer than two scenario clusters cannot characterize between-scenario uncertainty.")
    elif scenario_count < 10:
        warnings.append("Fewer than ten scenario clusters provide weak bootstrap interval support.")
    return {
        "scenario_clusters": scenario_count,
        "trial_count": trial_count,
        "warnings": warnings,
    }


def _quantile(values: Sequence[float], probability: float) -> float:
    """Return an observed quantile using a deterministic nearest-rank rule."""

    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, ceil(probability * len(ordered)) - 1))
    return ordered[index]


def cluster_bootstrap_interval(
    values_by_scenario: Mapping[str, Sequence[float]],
    *,
    statistic: Callable[[Sequence[float]], float],
    samples: int,
    confidence_level: float,
    seed: int,
) -> dict[str, float]:
    """Bootstrap scenarios as clusters while retaining all trials in each draw."""

    validate_bootstrap_config(samples, confidence_level)
    scenario_ids = sorted(values_by_scenario)
    if not scenario_ids:
        return {"lower": 0.0, "upper": 0.0}

    rng = random.Random(seed)
    estimates: list[float] = []
    for _ in range(samples):
        sampled_values: list[float] = []
        for _scenario in scenario_ids:
            sampled_id = scenario_ids[rng.randrange(len(scenario_ids))]
            sampled_values.extend(values_by_scenario[sampled_id])
        estimates.append(statistic(sampled_values))

    tail = (1.0 - confidence_level) / 2.0
    return {
        "lower": _quantile(estimates, tail),
        "upper": _quantile(estimates, 1.0 - tail),
    }


def mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def report_confidence_intervals(
    results: Sequence[Any],
    *,
    samples: int,
    confidence_level: float,
    seed: int,
) -> dict[str, Any]:
    """Calculate report intervals from TrialResult objects without dropping evidence."""

    validate_bootstrap_config(samples, confidence_level)
    core: dict[str, dict[str, list[float]]] = {
        "pass_rate": {},
        "error_rate": {},
        "mean_latency_ms": {},
        "mean_cost_usd": {},
        "reliability_at_n": {},
    }
    evaluator_scores: dict[str, dict[str, list[float]]] = {}

    for result in results:
        scenario_id = str(result.scenario_id)
        core["pass_rate"].setdefault(scenario_id, []).append(float(result.passed))
        core["error_rate"].setdefault(scenario_id, []).append(
            float(result.system_result.error is not None)
        )
        core["mean_latency_ms"].setdefault(scenario_id, []).append(
            float(result.system_result.latency_ms)
        )
        core["mean_cost_usd"].setdefault(scenario_id, []).append(
            float(result.system_result.cost_usd)
        )
        for evaluation in result.evaluations:
            evaluator_scores.setdefault(evaluation.metric, {}).setdefault(scenario_id, []).append(
                float(evaluation.score)
            )

    for scenario_id in {str(result.scenario_id) for result in results}:
        scenario_results = [result for result in results if result.scenario_id == scenario_id]
        core["reliability_at_n"][scenario_id] = [
            float(all(result.passed for result in scenario_results))
        ]

    metrics = {
        name: cluster_bootstrap_interval(
            values,
            statistic=mean,
            samples=samples,
            confidence_level=confidence_level,
            seed=seed,
        )
        for name, values in core.items()
    }
    metric_score_intervals = {
        name: cluster_bootstrap_interval(
            values,
            statistic=mean,
            samples=samples,
            confidence_level=confidence_level,
            seed=seed,
        )
        for name, values in sorted(evaluator_scores.items())
    }
    return {
        "method": "scenario_cluster_percentile_bootstrap",
        "confidence_level": confidence_level,
        "samples": samples,
        "seed": seed,
        "support": bootstrap_support(len({str(result.scenario_id) for result in results}), len(results)),
        "metrics": metrics,
        "mean_metric_scores": metric_score_intervals,
    }
