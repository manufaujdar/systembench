import json

import pytest

from systembench.io import load_report, load_suite, write_report


def test_duplicate_scenario_ids_are_rejected(tmp_path) -> None:
    path = tmp_path / "suite.json"
    path.write_text(json.dumps({
        "name": "x", "version": "1", "scenarios": [
            {"id": "same", "description": "a", "input": {}},
            {"id": "same", "description": "b", "input": {}}
        ]
    }))
    with pytest.raises(ValueError, match="unique"):
        load_suite(path)


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity"])
def test_strict_json_rejects_non_finite_constants(tmp_path, constant) -> None:
    path = tmp_path / "suite.json"
    path.write_text(
        '{"name":"x","version":"1","scenarios":[],"metric":' + constant + "}",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="invalid JSON numeric constant"):
        load_suite(path)


def test_strict_json_rejects_duplicate_object_members(tmp_path) -> None:
    path = tmp_path / "report.json"
    path.write_text('{"schema_version":"1.1","schema_version":"1.0"}', encoding="utf-8")

    with pytest.raises(ValueError, match="duplicate JSON object member"):
        load_report(path)


def test_report_writer_rejects_non_finite_values(tmp_path) -> None:
    with pytest.raises(ValueError, match="JSON compliant"):
        write_report({"run_id": "bad", "metric": float("nan")}, tmp_path)
