from __future__ import annotations

from typing import Any

from candidate_core import ENVELOPE_VERSION
from candidate_core.resources import load_schema
from jsonschema import Draft202012Validator


def validate_envelope(payload: dict[str, Any]) -> None:
    schema = load_schema("control-envelope.schema.json")
    Draft202012Validator(schema).validate(payload)


def error_payload(category: str, message: str) -> dict[str, str]:
    return {"category": category, "message": message}


def stage(
    stage_id: str,
    status: str,
    observations: dict[str, Any] | None = None,
    evidence: list[dict[str, str]] | None = None,
    error: dict[str, str] | None = None,
) -> dict[str, Any]:
    return {
        "id": stage_id,
        "status": status,
        "observations": observations or {},
        "evidence": evidence or [],
        "error": error,
    }


def build_envelope(
    *,
    run_id: str,
    command: str,
    status: str,
    stages: list[dict[str, Any]],
    observations: dict[str, Any] | None = None,
    evidence: list[dict[str, str]] | None = None,
    error: dict[str, str] | None = None,
    mutations: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    payload = {
        "envelope_version": ENVELOPE_VERSION,
        "run_id": run_id,
        "command": command,
        "status": status,
        "error": error,
        "stages": stages,
        "observations": observations or {},
        "evidence": evidence or [],
        "ownership": {
            "run_id": run_id,
            "mutations": mutations or [],
        },
    }
    validate_envelope(payload)
    return payload
