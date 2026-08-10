"""Matched baseline comparison and deterministic regression gates."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .integrity import (
    artifact_fingerprint,
    fingerprint,
    finite_number,
    positive_int,
    validate_artifact_fingerprint,
    validate_manifest,
)
from .statistics import (
    bootstrap_support,
    cluster_bootstrap_interval,
    mean,
    validate_bootstrap_config,
)


@dataclass(frozen=True)
class RegressionPolicy:
    """Predeclared practical tolerances for candidate-minus-baseline deltas."""

    max_pass_rate_drop: float = 0.0
    max_error_rate_increase: float = 0.0
    max_mean_latency_increase_ms: float | None = None
    max_mean_cost_increase_usd: float | None = None

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            if value is not None:
                finite_number(value, name, minimum=0.0)


def _scenario_ids(report: dict[str, Any]) -> list[str]:
    suite = report.get("suite")
    if not isinstance(suite, dict) or not isinstance(suite.get("scenarios"), list):
        raise TypeError("report suite must declare a scenarios array")
    scenario_ids: list[str] = []
    for scenario in suite["scenarios"]:
        if not isinstance(scenario, dict):
            raise TypeError("report suite scenarios must be objects")
        scenario_id = scenario.get("id")
        if not isinstance(scenario_id, str) or not scenario_id:
            raise ValueError("report suite scenario IDs must be non-empty strings")
        scenario_ids.append(scenario_id)
    if not scenario_ids:
        raise ValueError("report suite must declare at least one scenario")
    if len(set(scenario_ids)) != len(scenario_ids):
        raise ValueError("report suite scenario IDs must be unique")
    return scenario_ids


def _validate_resource_measurements(result: dict[str, Any], identity: str) -> None:
    system_result = result.get("system_result")
    if not isinstance(system_result, dict):
        raise TypeError(f"{identity} system_result must be an object")
    finite_number(system_result.get("latency_ms"), f"{identity} latency_ms", minimum=0.0)
    finite_number(system_result.get("cost_usd"), f"{identity} cost_usd", minimum=0.0)
    token_usage = system_result.get("token_usage")
    if not isinstance(token_usage, dict):
        raise TypeError(f"{identity} token_usage must be an object")
    for name, value in token_usage.items():
        if not isinstance(name, str) or not name:
            raise ValueError(f"{identity} token_usage keys must be non-empty strings")
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{identity} token_usage.{name} must be a non-negative integer")
    if system_result.get("error") is not None and not isinstance(system_result.get("error"), str):
        raise ValueError(f"{identity} error must be null or a string")


def _validate_evaluations(result: dict[str, Any], identity: str) -> None:
    evaluations = result.get("evaluations")
    if not isinstance(evaluations, list):
        raise TypeError(f"{identity} evaluations must be an array")
    for position, evaluation in enumerate(evaluations):
        if not isinstance(evaluation, dict):
            raise TypeError(f"{identity} evaluation {position} must be an object")
        metric = evaluation.get("metric")
        if not isinstance(metric, str) or not metric:
            raise ValueError(f"{identity} evaluation {position} metric must be non-empty")
        score = finite_number(evaluation.get("score"), f"{identity} {metric} score")
        if not 0.0 <= score <= 1.0:
            raise ValueError(f"{identity} {metric} score must be between 0 and 1")
        if not isinstance(evaluation.get("passed"), bool):
            raise TypeError(f"{identity} {metric} passed must be boolean")


def _trial_index(report: dict[str, Any], label: str) -> dict[tuple[str, int], dict[str, Any]]:
    scenario_ids = _scenario_ids(report)
    configuration = report.get("configuration")
    if not isinstance(configuration, dict):
        raise TypeError(f"{label} configuration must be an object")
    trials = positive_int(configuration.get("trials"), f"{label} configuration.trials")
    seed = configuration.get("seed")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise TypeError(f"{label} configuration.seed must be an integer")
    results = report.get("results")
    if not isinstance(results, list):
        raise TypeError(f"{label} results must be an array")

    index: dict[tuple[str, int], dict[str, Any]] = {}
    for result in results:
        if not isinstance(result, dict):
            raise TypeError(f"{label} trial results must be objects")
        scenario_id = result.get("scenario_id")
        if not isinstance(scenario_id, str) or not scenario_id:
            raise ValueError(f"{label} result scenario_id must be a non-empty string")
        trial = positive_int(result.get("trial"), f"{label} {scenario_id} trial")
        key = (scenario_id, trial)
        if key in index:
            raise ValueError(f"duplicate trial identity in {label}: {scenario_id} trial {trial}")
        if not isinstance(result.get("passed"), bool):
            raise TypeError(f"{label} {scenario_id} trial {trial} passed must be boolean")
        identity = f"{label} {scenario_id} trial {trial}"
        _validate_resource_measurements(result, identity)
        _validate_evaluations(result, identity)
        index[key] = result

    expected = {(scenario_id, trial) for scenario_id in scenario_ids for trial in range(1, trials + 1)}
    actual = set(index)
    if actual != expected:
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        raise ValueError(
            f"{label} results do not match declared scenario×trial grid; "
            f"missing={missing}, unexpected={unexpected}"
        )
    return index


def _validate_report(report: dict[str, Any], label: str) -> dict[tuple[str, int], dict[str, Any]]:
    if report.get("schema_version") != "1.1":
        raise ValueError(f"{label} report schema_version must be 1.1")
    manifests = report.get("manifests")
    fingerprints = report.get("fingerprints")
    if not isinstance(manifests, dict) or not isinstance(fingerprints, dict):
        raise TypeError(f"{label} report must contain manifests and fingerprints")
    for name in ("system", "budget", "accounting"):
        item = validate_manifest(manifests.get(name), f"{label} {name}")
        if fingerprints.get(name) != item["fingerprint"]:
            raise ValueError(f"{label} {name} fingerprint index does not match its manifest")
    if fingerprints.get("suite") != fingerprint(report.get("suite")):
        raise ValueError(f"{label} suite fingerprint does not match suite content")
    trials = _trial_index(report, label)
    validate_artifact_fingerprint(report, "report_fingerprint", f"{label} report")
    return trials


def _validate_match(
    baseline: dict[str, Any], candidate: dict[str, Any]
) -> tuple[dict[tuple[str, int], dict[str, Any]], dict[tuple[str, int], dict[str, Any]]]:
    baseline_trials = _validate_report(baseline, "baseline")
    candidate_trials = _validate_report(candidate, "candidate")
    fields = (
        ("schema_version", baseline["schema_version"], candidate["schema_version"]),
        ("suite fingerprint", baseline["fingerprints"]["suite"], candidate["fingerprints"]["suite"]),
        ("budget fingerprint", baseline["fingerprints"]["budget"], candidate["fingerprints"]["budget"]),
        (
            "accounting fingerprint",
            baseline["fingerprints"]["accounting"],
            candidate["fingerprints"]["accounting"],
        ),
        (
            "configuration.trials",
            baseline["configuration"]["trials"],
            candidate["configuration"]["trials"],
        ),
        (
            "configuration.seed",
            baseline["configuration"]["seed"],
            candidate["configuration"]["seed"],
        ),
    )
    mismatches = [name for name, baseline_value, candidate_value in fields if baseline_value != candidate_value]
    if mismatches:
        raise ValueError("reports are not matched: " + ", ".join(mismatches))
    if baseline_trials.keys() != candidate_trials.keys():  # Defensive after exact-grid checks.
        raise ValueError("reports are not matched: scenario/trial identities differ")
    return baseline_trials, candidate_trials


def _trial_values(result: dict[str, Any]) -> dict[str, float]:
    system_result = result["system_result"]
    return {
        "pass_rate": float(result["passed"]),
        "error_rate": float(system_result["error"] is not None),
        "mean_latency_ms": finite_number(system_result["latency_ms"], "latency_ms", minimum=0.0),
        "mean_cost_usd": finite_number(system_result["cost_usd"], "cost_usd", minimum=0.0),
    }


def _gate(
    metric: str,
    interval: dict[str, float],
    observed_delta: float,
    allowed_change: float,
    direction: str,
) -> dict[str, Any]:
    if direction == "decrease":
        failed = interval["upper"] < -allowed_change
        boundary = -allowed_change
    else:
        failed = interval["lower"] > allowed_change
        boundary = allowed_change
    return {
        "metric": metric,
        "regression_direction": direction,
        "allowed_change": allowed_change,
        "decision_boundary": boundary,
        "observed_delta": observed_delta,
        "confidence_interval": interval,
        "status": "fail" if failed else "pass",
    }


def compare_reports(
    baseline: dict[str, Any],
    candidate: dict[str, Any],
    *,
    policy: RegressionPolicy | None = None,
    bootstrap_samples: int = 2000,
    confidence_level: float = 0.95,
    bootstrap_seed: int = 0,
) -> dict[str, Any]:
    """Compare matched trial evidence and return a machine-readable gate decision."""

    validate_bootstrap_config(bootstrap_samples, confidence_level)
    policy = policy or RegressionPolicy()
    baseline_trials, candidate_trials = _validate_match(baseline, candidate)

    differences: dict[str, dict[str, list[float]]] = {}
    paired_evidence: list[dict[str, Any]] = []
    metric_names = ("pass_rate", "error_rate", "mean_latency_ms", "mean_cost_usd")
    for key in sorted(baseline_trials):
        baseline_values = _trial_values(baseline_trials[key])
        candidate_values = _trial_values(candidate_trials[key])
        deltas = {name: candidate_values[name] - baseline_values[name] for name in metric_names}
        for name, delta in deltas.items():
            differences.setdefault(name, {}).setdefault(key[0], []).append(delta)
        paired_evidence.append({"scenario_id": key[0], "trial": key[1], "deltas": deltas})

    metric_results: dict[str, dict[str, Any]] = {}
    for name in metric_names:
        scenario_differences = differences[name]
        all_differences = [value for values in scenario_differences.values() for value in values]
        metric_results[name] = {
            "observed_delta": mean(all_differences),
            "confidence_interval": cluster_bootstrap_interval(
                scenario_differences,
                statistic=mean,
                samples=bootstrap_samples,
                confidence_level=confidence_level,
                seed=bootstrap_seed,
            ),
        }

    gate_specs = [
        ("pass_rate", policy.max_pass_rate_drop, "decrease"),
        ("error_rate", policy.max_error_rate_increase, "increase"),
        ("mean_latency_ms", policy.max_mean_latency_increase_ms, "increase"),
        ("mean_cost_usd", policy.max_mean_cost_increase_usd, "increase"),
    ]
    gates = [
        _gate(
            name,
            metric_results[name]["confidence_interval"],
            metric_results[name]["observed_delta"],
            allowed_change,
            direction,
        )
        for name, allowed_change, direction in gate_specs
        if allowed_change is not None
    ]
    policy_value = asdict(policy)
    system_differs = baseline["fingerprints"]["system"] != candidate["fingerprints"]["system"]
    comparison = {
        "schema_version": "1.1",
        "baseline": {
            "run_id": baseline.get("run_id"),
            "system": baseline.get("system"),
            "report_fingerprint": baseline["report_fingerprint"],
            "system_fingerprint": baseline["fingerprints"]["system"],
        },
        "candidate": {
            "run_id": candidate.get("run_id"),
            "system": candidate.get("system"),
            "report_fingerprint": candidate["report_fingerprint"],
            "system_fingerprint": candidate["fingerprints"]["system"],
        },
        "system_comparison": {
            "manifests_differ": system_differs,
            "difference_permitted": True,
            "claim_scope": "Regression gates apply only to the matched declared protocol; they do not establish system equivalence or benchmark validity.",
        },
        "matched_protocol": {
            "suite": baseline["suite"],
            "suite_fingerprint": baseline["fingerprints"]["suite"],
            "budget_fingerprint": baseline["fingerprints"]["budget"],
            "accounting_fingerprint": baseline["fingerprints"]["accounting"],
            "trials": baseline["configuration"]["trials"],
            "run_seed": baseline["configuration"]["seed"],
            "trial_count": len(baseline_trials),
            "scenario_ids": sorted({key[0] for key in baseline_trials}),
        },
        "bootstrap": {
            "method": "paired_scenario_cluster_percentile_bootstrap",
            "samples": bootstrap_samples,
            "confidence_level": confidence_level,
            "seed": bootstrap_seed,
            "support": bootstrap_support(
                len({key[0] for key in baseline_trials}), len(baseline_trials)
            ),
        },
        "policy": policy_value,
        "policy_fingerprint": fingerprint(policy_value),
        "metrics": metric_results,
        "gates": gates,
        "passed": all(gate["status"] == "pass" for gate in gates),
        "paired_trial_evidence": paired_evidence,
    }
    comparison["comparison_fingerprint"] = artifact_fingerprint(
        comparison, "comparison_fingerprint"
    )
    return comparison
