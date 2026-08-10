import pytest

from systembench.demo import DemoSystem
from systembench.evaluators import default_evaluators
from systembench.models import Scenario, Suite
from systembench.runner import BenchmarkRunner
from systembench.web import CONSOLE_CSS, CONSOLE_HTML, CONSOLE_JS, api_response, run_demo


def test_web_console_runs_offline_demo() -> None:
    report = run_demo(2)
    assert report["summary"]["trial_count"] == 4
    assert report["summary"]["pass_rate"] == 1.0
    assert "No model, account, API key, or database" in CONSOLE_HTML
    assert "Benchmark behavior" in CONSOLE_HTML
    assert "Adaptive session" in CONSOLE_HTML
    assert "Measure the whole causal path" in CONSOLE_HTML
    assert "localStorage" not in CONSOLE_HTML
    assert "localStorage" not in CONSOLE_JS
    assert "@media (max-width: 720px)" in CONSOLE_CSS
    assert "innerHTML" not in CONSOLE_JS


def test_default_evaluators_emit_strict_json_without_optional_slos() -> None:
    suite = Suite(
        "no-slo",
        "1",
        (Scenario("sum", "No optional limits", {"question": "Sum 1 and 2"}, {"output": "3"}),),
    )
    report = BenchmarkRunner(DemoSystem(), default_evaluators()).run(
        suite, bootstrap_samples=100
    )
    assert report["report_fingerprint"]


@pytest.mark.parametrize("value", [True, 0, 11, 1.5])
def test_web_console_bounds_trial_count(value) -> None:
    with pytest.raises(ValueError, match="between 1 and 10"):
        run_demo(value)


def test_web_api_dispatches_design_analysis() -> None:
    result = api_response(
        "/api/analyze",
        {
            "target_type": "agent",
            "name": "candidate",
            "description": "Uses retrieval and tools to support users.",
            "decision": "Decide whether to run a supervised pilot.",
            "users": "Support users",
            "environment": "Chat and refund tool",
            "methods": ["repeated_trials", "failure_injection"],
        },
    )
    assert result["protocol"]["target"]["type"] == "agent"
    assert result["recommended_probes"][0]["dimension"] == "permission"
