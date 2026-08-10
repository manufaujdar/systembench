import json
from pathlib import Path

from tools.repository_agent.repository_agent import (
    audit_repository,
    compare_agents,
    review_prompt,
)

ROOT = Path(__file__).resolve().parents[1]


def test_repository_audit_is_local_deterministic_and_aligned() -> None:
    report = audit_repository(ROOT)
    assert report["mode"] == "local_deterministic_audit"
    assert report["external_model_calls"] is False
    assert report["files_modified"] is False
    assert len(set(report["versions"].values())) == 1
    assert report["findings"] == []


def test_agent_matrix_is_a_supervised_capability_comparison() -> None:
    comparison = compare_agents()
    assert "not an AI performance benchmark" in comparison["method"]
    assert sum(item["weight"] for item in comparison["evaluation_rubric"]) == 100
    assert {agent["name"] for agent in comparison["agents"]} >= {"Codex", "OpenHands"}


def test_review_prompt_preserves_validity_and_data_boundaries() -> None:
    prompt = review_prompt(audit_repository(ROOT), compare_agents())
    assert "never request or score hidden chain-of-thought" in prompt
    assert "Do not tune scenarios" in prompt
    assert "proposed patch plan first" in prompt
    json.dumps(prompt)
