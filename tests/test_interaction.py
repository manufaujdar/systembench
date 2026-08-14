from copy import deepcopy

import pytest

from systembench.interaction import (
    TARGET_TYPES,
    analyze_design,
    catalog,
    observe_session,
    start_session,
)


def _payload(target_type: str = "system", methods: list[str] | None = None) -> dict:
    return {
        "target_type": target_type,
        "name": "candidate-v2",
        "description": "A complete support workflow using retrieval, tools, and human approval.",
        "decision": "Decide whether to begin a supervised pilot.",
        "users": "Customers and support reviewers",
        "environment": "Multi-turn chat with a state-changing refund tool",
        "methods": methods or [],
    }


def test_catalog_covers_all_supported_evaluation_targets() -> None:
    targets = {item["id"] for item in catalog()["target_types"]}
    assert targets == set(TARGET_TYPES)
    assert all(item["constructs"] for item in catalog()["target_types"])


def test_analysis_rewards_evidence_without_calling_it_target_quality() -> None:
    weak = analyze_design(_payload(methods=["single_turn"]))
    strong = analyze_design(
        _payload(
            methods=[
                "repeated_trials",
                "human_review",
                "failure_injection",
                "budget_matching",
                "trace_capture",
                "recovery_testing",
                "long_horizon",
                "privacy_testing",
                "slice_analysis",
            ]
        )
    )
    assert weak["realism_score"] < strong["realism_score"]
    assert weak["gaps"]
    assert strong["gaps"] == []
    assert "not target quality" in strong["claim_boundary"]
    assert strong["protocol_fingerprint"].startswith("sha256:")


@pytest.mark.parametrize("target_type", TARGET_TYPES)
def test_each_target_has_distinct_observable_probes(target_type: str) -> None:
    analysis = analyze_design(_payload(target_type))
    assert len(analysis["recommended_probes"]) == 3
    assert all(probe["observable_success"] for probe in analysis["recommended_probes"])
    assert all(probe["evidence"] for probe in analysis["recommended_probes"])


def test_failed_observation_triggers_diagnostic_replay() -> None:
    session = start_session(_payload("agent"))
    adapted = observe_session(
        {
            "session": session,
            "observation": {
                "outcome": "failed",
                "human_effort": 5,
                "confidence": 0.9,
                "notes": "The tool action occurred without approval.",
            },
        }
    )
    assert adapted["current_probe"]["id"].endswith("-diagnostic")
    assert adapted["metrics"]["task_success"] == 0.0
    assert adapted["metrics"]["mean_calibration_gap"] == 0.9
    assert "diagnostic" in adapted["last_adaptation"]


def test_partial_observation_triggers_human_repair_probe() -> None:
    session = start_session(_payload("llm"))
    adapted = observe_session(
        {
            "session": session,
            "observation": {
                "outcome": "partial",
                "human_effort": 3,
                "confidence": 0.5,
                "notes": "The system missed one stated constraint.",
            },
        }
    )
    assert adapted["current_probe"]["id"].endswith("-repair")
    assert adapted["metrics"]["task_success"] == 0.5


def test_session_mutation_fails_closed() -> None:
    session = start_session(_payload())
    tampered = deepcopy(session)
    tampered["target"]["name"] = "different"
    with pytest.raises(ValueError, match="fingerprint"):
        observe_session(
            {
                "session": tampered,
                "observation": {
                    "outcome": "passed",
                    "human_effort": 1,
                    "confidence": 1.0,
                    "notes": "",
                },
            }
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [("target_type", "unknown"), ("name", ""), ("methods", ["invented"])],
)
def test_analysis_rejects_invalid_protocol_input(field: str, value: object) -> None:
    payload = _payload()
    payload[field] = value
    with pytest.raises((TypeError, ValueError)):
        analyze_design(payload)
