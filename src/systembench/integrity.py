"""Strict JSON serialization and integrity fingerprints for benchmark artifacts."""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping
from typing import Any


def _reject_constant(value: str) -> None:
    raise ValueError(f"invalid JSON numeric constant: {value}")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object member: {key}")
        result[key] = value
    return result


def strict_json_loads(value: str) -> Any:
    """Parse RFC-compatible JSON, rejecting non-finite constants and duplicate keys."""

    return json.loads(
        value,
        parse_constant=_reject_constant,
        object_pairs_hook=_unique_object,
    )


def strict_json_dumps(value: Any, *, indent: int | None = None) -> str:
    """Serialize JSON without JavaScript-only NaN or Infinity extensions."""

    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        indent=indent,
        separators=(",", ":") if indent is None else None,
        sort_keys=True,
    )


def json_snapshot(value: Any) -> Any:
    """Return a detached, strictly JSON-compatible snapshot."""

    return strict_json_loads(strict_json_dumps(value))


def fingerprint(value: Any) -> str:
    payload = strict_json_dumps(value).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def finite_number(value: Any, name: str, *, minimum: float | None = None) -> float:
    """Validate a real finite JSON number, excluding booleans."""

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a finite number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    if minimum is not None and result < minimum:
        raise ValueError(f"{name} must be at least {minimum:g}")
    return result


def positive_int(value: Any, name: str, *, minimum: int = 1) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer of at least {minimum}")
    return value


def manifest(declared: Mapping[str, Any], *, completeness: str = "declared") -> dict[str, Any]:
    snapshot = json_snapshot(dict(declared))
    if not isinstance(snapshot, dict):  # pragma: no cover - Mapping guarantees this
        raise TypeError("manifest declaration must be a JSON object")
    identity = {"schema_version": "1.0", "completeness": completeness, "declared": snapshot}
    return {**identity, "fingerprint": fingerprint(identity)}


def validate_manifest(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError(f"{name} manifest must be an object")
    identity = {
        "schema_version": value.get("schema_version"),
        "completeness": value.get("completeness"),
        "declared": value.get("declared"),
    }
    if identity["schema_version"] != "1.0":
        raise ValueError(f"{name} manifest has an unsupported schema version")
    if not isinstance(identity["completeness"], str) or not identity["completeness"]:
        raise ValueError(f"{name} manifest completeness must be a non-empty string")
    if not isinstance(identity["declared"], dict):
        raise TypeError(f"{name} manifest declared value must be an object")
    expected = fingerprint(identity)
    if value.get("fingerprint") != expected:
        raise ValueError(f"{name} manifest fingerprint does not match its declared content")
    return value


def artifact_fingerprint(value: Mapping[str, Any], field: str) -> str:
    return fingerprint({key: item for key, item in value.items() if key != field})


def validate_artifact_fingerprint(value: Mapping[str, Any], field: str, name: str) -> None:
    if value.get(field) != artifact_fingerprint(value, field):
        raise ValueError(f"{name} fingerprint does not match artifact content")
