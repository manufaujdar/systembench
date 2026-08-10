from systembench.adapters import FunctionAdapter
from systembench.evaluators import ContainsEvaluator
from systembench.models import Scenario, Suite, SystemResult
from systembench.runner import BenchmarkRunner


def test_runner_reports_deterministic_cluster_bootstrap_intervals() -> None:
    scenarios = (
        Scenario("pass", "passes", {}, {"contains": ["ok"]}),
        Scenario("fail", "fails", {}, {"contains": ["ok"]}),
    )

    def execute(scenario, _context):
        return SystemResult(output="ok" if scenario.id == "pass" else "no", latency_ms=1)

    runner = BenchmarkRunner(FunctionAdapter(execute), [ContainsEvaluator()])
    first = runner.run(
        Suite("suite", "1", scenarios),
        trials=2,
        bootstrap_samples=100,
        bootstrap_seed=17,
    )
    second = runner.run(
        Suite("suite", "1", scenarios),
        trials=2,
        bootstrap_samples=100,
        bootstrap_seed=17,
    )

    first_intervals = first["summary"]["confidence_intervals"]
    assert first_intervals == second["summary"]["confidence_intervals"]
    assert first_intervals["method"] == "scenario_cluster_percentile_bootstrap"
    assert first_intervals["seed"] == 17
    assert first_intervals["metrics"]["pass_rate"] == {"lower": 0.0, "upper": 1.0}
    assert first["configuration"]["bootstrap_samples"] == 100
    assert len(first["results"]) == 4


def test_report_preserves_scenario_protocol_for_matched_comparisons() -> None:
    scenario = Scenario(
        "one",
        "protocol evidence",
        {"question": "test"},
        {"contains": ["ok"]},
        constraints={"max_latency_ms": 10},
        tags=("smoke",),
        failure_injection={"dependency_unavailable": True},
    )
    report = BenchmarkRunner(
        FunctionAdapter(lambda _scenario, _context: SystemResult(output="ok", latency_ms=1)),
        [ContainsEvaluator()],
    ).run(Suite("suite", "1", (scenario,)), bootstrap_samples=100)

    assert report["suite"]["scenarios"][0]["constraints"] == {"max_latency_ms": 10}
    assert report["suite"]["scenarios"][0]["failure_injection"] == {
        "dependency_unavailable": True
    }
    assert report["summary"]["confidence_intervals"]["support"]["warnings"]
    assert report["report_fingerprint"].startswith("sha256:")
