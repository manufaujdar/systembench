import pytest

from systembench.adapters import FunctionAdapter
from systembench.evaluators import ContainsEvaluator, LatencySLOEvaluator
from systembench.models import Scenario, Suite, SystemResult
from systembench.runner import BenchmarkRunner


def test_runner_repeats_and_aggregates_trials() -> None:
    scenario = Scenario(
        id="one",
        description="test",
        input={},
        expected={"contains": ["ok"]},
        constraints={"max_latency_ms": 100},
    )
    adapter = FunctionAdapter(lambda scenario, context: SystemResult(output="ok", latency_ms=2))
    report = BenchmarkRunner(adapter, [ContainsEvaluator(), LatencySLOEvaluator()]).run(
        Suite("suite", "1", (scenario,)), trials=3
    )
    assert report["summary"]["trial_count"] == 3
    assert report["summary"]["pass_rate"] == 1.0


def test_runner_isolates_adapter_errors() -> None:
    def fail(scenario, context):
        raise RuntimeError("service unavailable")

    scenario = Scenario("failure", "test failure", {}, {"contains": ["ok"]})
    report = BenchmarkRunner(FunctionAdapter(fail), [ContainsEvaluator()]).run(
        Suite("suite", "1", (scenario,))
    )
    assert report["summary"]["error_rate"] == 1.0
    assert "service unavailable" in report["results"][0]["system_result"]["error"]


def test_runner_reports_latency_percentiles_and_reliability() -> None:
    scenario = Scenario(
        id="one",
        description="test",
        input={},
        expected={"contains": ["ok"]},
        tags=("smoke",),
    )

    def execute(_scenario, context):
        latency = {1: 3.0, 2: 8.0, 3: 20.0}[context["trial"]]
        return SystemResult(output="ok", latency_ms=latency)

    report = BenchmarkRunner(FunctionAdapter(execute), [ContainsEvaluator()]).run(
        Suite("suite", "1", (scenario,)), trials=3
    )

    summary = report["summary"]
    assert summary["latency_percentiles_ms"] == {"p50": 8.0, "p95": 20.0, "p99": 20.0}
    assert summary["reliability_at_n"] == 1.0
    assert summary["scenario_count"] == 1


def test_runner_reports_tag_slices() -> None:
    scenarios = (
        Scenario("safe", "safe", {}, {"contains": ["ok"]}, tags=("safety",)),
        Scenario("resilient", "resilient", {}, {"contains": ["ok"]}, tags=("resilience",)),
    )
    adapter = FunctionAdapter(lambda _scenario, _context: SystemResult(output="ok", latency_ms=1))
    report = BenchmarkRunner(adapter, [ContainsEvaluator()]).run(Suite("suite", "1", scenarios))

    assert report["summary"]["slices"] == {
        "resilience": {"trial_count": 1, "scenario_count": 1, "pass_rate": 1.0, "reliability_at_n": 1.0},
        "safety": {"trial_count": 1, "scenario_count": 1, "pass_rate": 1.0, "reliability_at_n": 1.0},
    }


@pytest.mark.parametrize(
    "result",
    [
        SystemResult(output="ok", latency_ms=float("nan")),
        SystemResult(output="ok", latency_ms=1, cost_usd=float("inf")),
        SystemResult(output="ok", latency_ms=-1),
        SystemResult(output="ok", latency_ms=1, token_usage={"input": -1}),
    ],
)
def test_runner_rejects_invalid_resource_measurements(result) -> None:
    scenario = Scenario("one", "test", {}, {"contains": ["ok"]})
    runner = BenchmarkRunner(FunctionAdapter(lambda _scenario, _context: result), [ContainsEvaluator()])

    with pytest.raises(ValueError):
        runner.run(Suite("suite", "1", (scenario,)), bootstrap_samples=100)


def test_runner_records_declared_manifest_fingerprints() -> None:
    scenario = Scenario("one", "test", {}, {"contains": ["ok"]})
    report = BenchmarkRunner(
        FunctionAdapter(lambda _scenario, _context: SystemResult(output="ok", latency_ms=1)),
        [ContainsEvaluator()],
    ).run(
        Suite("suite", "1", (scenario,)),
        bootstrap_samples=100,
        system_manifest={"release": "candidate-v2", "prompt_sha256": "abc"},
        budget_manifest={"max_requests": 1},
        accounting_manifest={"pricing_table_sha256": "def"},
    )

    assert report["manifests"]["system"]["completeness"] == "declared"
    assert report["manifests"]["system"]["declared"]["configuration"]["release"] == "candidate-v2"
    assert report["fingerprints"]["budget"] == report["manifests"]["budget"]["fingerprint"]
