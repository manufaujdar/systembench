import json
import math
import sys
from copy import deepcopy

import pytest

from systembench.cli import main
from systembench.comparison import RegressionPolicy, compare_reports
from systembench.integrity import artifact_fingerprint, fingerprint, manifest


def _seal(report: dict) -> dict:
    report["report_fingerprint"] = artifact_fingerprint(report, "report_fingerprint")
    return report


def _report(run_id: str, passed_by_scenario: dict[str, bool]) -> dict:
    results = []
    for scenario_id, passed in passed_by_scenario.items():
        results.append(
            {
                "scenario_id": scenario_id,
                "trial": 1,
                "passed": passed,
                "system_result": {
                    "error": None if passed else "failure",
                    "latency_ms": 10.0,
                    "cost_usd": 0.01,
                    "token_usage": {},
                },
                "evaluations": [],
            }
        )
    suite = {
        "name": "suite",
        "version": "1",
        "metadata": {},
        "scenarios": [
            {
                "id": scenario_id,
                "description": scenario_id,
                "input": {},
                "expected": {},
                "constraints": {},
                "tags": [],
                "failure_injection": {},
            }
            for scenario_id in passed_by_scenario
        ],
    }
    system_identity = manifest({"name": run_id, "configuration": {}})
    budget_identity = manifest(
        {
            "trials_per_scenario": 1,
            "scenario_constraints": {scenario_id: {} for scenario_id in passed_by_scenario},
            "additional": {},
        }
    )
    accounting_identity = manifest(
        {
            "resource_metrics": {
                "latency_ms": {"unit": "milliseconds", "source": "fixture", "required": True},
                "cost_usd": {"unit": "USD", "source": "fixture", "required": True},
                "token_usage": {"unit": "tokens", "source": "fixture", "required": True},
            },
            "trial_pass_rule": "fixture",
            "evaluators": [],
            "additional": {},
        }
    )
    return _seal({
        "schema_version": "1.1",
        "run_id": run_id,
        "system": run_id,
        "suite": suite,
        "manifests": {
            "system": system_identity,
            "budget": budget_identity,
            "accounting": accounting_identity,
        },
        "fingerprints": {
            "suite": fingerprint(suite),
            "system": system_identity["fingerprint"],
            "budget": budget_identity["fingerprint"],
            "accounting": accounting_identity["fingerprint"],
        },
        "configuration": {"trials": 1, "seed": 9},
        "results": results,
    })


def test_comparison_detects_deterministic_regression_and_preserves_pair_evidence() -> None:
    baseline = _report("baseline", {"a": True, "b": True})
    candidate = _report("candidate", {"a": False, "b": False})

    comparison = compare_reports(
        baseline,
        candidate,
        bootstrap_samples=100,
        bootstrap_seed=23,
    )

    assert comparison["passed"] is False
    assert {gate["metric"]: gate["status"] for gate in comparison["gates"]} == {
        "pass_rate": "fail",
        "error_rate": "fail",
    }
    assert comparison["metrics"]["pass_rate"]["confidence_interval"] == {
        "lower": -1.0,
        "upper": -1.0,
    }
    assert comparison["paired_trial_evidence"][0] == {
        "scenario_id": "a",
        "trial": 1,
        "deltas": {
            "pass_rate": -1.0,
            "error_rate": 1.0,
            "mean_latency_ms": 0.0,
            "mean_cost_usd": 0.0,
        },
    }


def test_practical_tolerance_can_allow_small_regression() -> None:
    baseline = _report("baseline", {"a": True, "b": True})
    candidate = _report("candidate", {"a": False, "b": True})

    comparison = compare_reports(
        baseline,
        candidate,
        policy=RegressionPolicy(max_pass_rate_drop=0.5, max_error_rate_increase=0.5),
        bootstrap_samples=100,
    )

    assert comparison["passed"] is True


def test_comparison_rejects_unmatched_protocols() -> None:
    baseline = _report("baseline", {"a": True})
    candidate = deepcopy(baseline)
    candidate["suite"]["version"] = "2"
    candidate["fingerprints"]["suite"] = fingerprint(candidate["suite"])
    _seal(candidate)

    with pytest.raises(ValueError, match="reports are not matched: suite fingerprint"):
        compare_reports(baseline, candidate, bootstrap_samples=100)


def test_latency_gate_is_opt_in() -> None:
    baseline = _report("baseline", {"a": True})
    candidate = _report("candidate", {"a": True})
    candidate["results"][0]["system_result"]["latency_ms"] = 25.0

    _seal(candidate)
    without_latency_gate = compare_reports(baseline, candidate, bootstrap_samples=100)
    with_latency_gate = compare_reports(
        baseline,
        candidate,
        policy=RegressionPolicy(max_mean_latency_increase_ms=5.0),
        bootstrap_samples=100,
    )

    assert without_latency_gate["passed"] is True
    assert with_latency_gate["passed"] is False


def test_compare_cli_exits_nonzero_for_ci_regression(tmp_path, monkeypatch, capsys) -> None:
    baseline_path = tmp_path / "baseline.json"
    candidate_path = tmp_path / "candidate.json"
    baseline_path.write_text(json.dumps(_report("baseline", {"a": True})), encoding="utf-8")
    candidate_path.write_text(json.dumps(_report("candidate", {"a": False})), encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "systembench",
            "compare",
            str(baseline_path),
            str(candidate_path),
            "--bootstrap-samples",
            "100",
        ],
    )

    with pytest.raises(SystemExit) as error:
        main()

    assert error.value.code == 1
    assert json.loads(capsys.readouterr().out)["passed"] is False


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -1.0, True])
def test_regression_policy_rejects_invalid_tolerances(value) -> None:
    with pytest.raises((TypeError, ValueError), match="max_pass_rate_drop"):
        RegressionPolicy(max_pass_rate_drop=value)


def test_comparison_requires_exact_declared_grid() -> None:
    baseline = _report("baseline", {"a": True, "b": True})
    candidate = _report("candidate", {"a": True, "b": True})
    baseline["results"].pop()
    _seal(baseline)

    with pytest.raises(ValueError, match="scenario×trial grid"):
        compare_reports(baseline, candidate, bootstrap_samples=100)


@pytest.mark.parametrize(
    ("field", "value"),
    [("latency_ms", float("nan")), ("cost_usd", -0.01), ("latency_ms", None)],
)
def test_comparison_rejects_invalid_or_missing_resource_measurements(field, value) -> None:
    baseline = _report("baseline", {"a": True})
    candidate = _report("candidate", {"a": True})
    candidate["results"][0]["system_result"][field] = value
    if not (isinstance(value, float) and math.isnan(value)):
        _seal(candidate)

    expected_error = TypeError if value is None else ValueError
    with pytest.raises(expected_error, match=field):
        compare_reports(baseline, candidate, bootstrap_samples=100)


def test_system_manifest_may_differ_but_budget_and_accounting_must_match() -> None:
    baseline = _report("baseline", {"a": True})
    candidate = _report("candidate", {"a": True})

    comparison = compare_reports(baseline, candidate, bootstrap_samples=100)
    assert comparison["system_comparison"] == {
        "manifests_differ": True,
        "difference_permitted": True,
        "claim_scope": "Regression gates apply only to the matched declared protocol; they do not establish system equivalence or benchmark validity.",
    }

    candidate["manifests"]["budget"] = manifest({"different": True})
    candidate["fingerprints"]["budget"] = candidate["manifests"]["budget"]["fingerprint"]
    _seal(candidate)
    with pytest.raises(ValueError, match="budget fingerprint"):
        compare_reports(baseline, candidate, bootstrap_samples=100)


def test_comparison_rejects_report_whose_content_no_longer_matches_hash() -> None:
    baseline = _report("baseline", {"a": True})
    candidate = _report("candidate", {"a": True})
    candidate["results"][0]["passed"] = False

    with pytest.raises(ValueError, match="report fingerprint"):
        compare_reports(baseline, candidate, bootstrap_samples=100)
