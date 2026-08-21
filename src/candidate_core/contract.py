from __future__ import annotations

from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from candidate_core.errors import IncompleteContract, InvalidContract, UnconfirmedContract
from candidate_core.jsonio import load_json
from candidate_core.resources import load_schema


def load_contract(path: Path) -> dict[str, Any]:
    try:
        payload = load_json(path)
    except FileNotFoundError as exc:
        raise IncompleteContract(f"contract file is missing: {path}") from exc
    except ValueError as exc:
        raise InvalidContract(str(exc)) from exc
    except OSError as exc:
        raise IncompleteContract(f"contract file cannot be read: {path}") from exc
    if not isinstance(payload, dict):
        raise InvalidContract("contract must be a JSON object")
    return payload


def validate_contract(payload: dict[str, Any]) -> dict[str, Any]:
    schema = load_schema("productctl.contract.schema.json")
    try:
        Draft202012Validator(schema).validate(payload)
    except ValidationError as exc:
        if exc.validator in {"required", "minItems", "minLength"}:
            raise IncompleteContract(_format_schema_error(exc)) from exc
        raise InvalidContract(_format_schema_error(exc)) from exc
    if payload.get("confirmed") is not True:
        raise UnconfirmedContract(
            "contract is a draft; confirm identity, success, ownership, cleanup, and secret semantics before acceptance"
        )
    return payload


def load_and_validate_contract(path: Path) -> dict[str, Any]:
    return validate_contract(load_contract(path))


def _format_schema_error(exc: ValidationError) -> str:
    location = ".".join(str(part) for part in exc.absolute_path) or "<root>"
    return f"{location}: {exc.message}"
