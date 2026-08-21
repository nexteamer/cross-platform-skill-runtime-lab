from __future__ import annotations

from jsonschema import Draft202012Validator

from candidate_core.envelope import build_envelope, stage
from candidate_core.resources import load_schema


def test_conformance_skeleton_accepts_versioned_envelope() -> None:
    payload = build_envelope(
        run_id="conformance-skeleton",
        command="acceptance.core",
        status="passed",
        stages=[stage("contract.validate", "passed")],
        observations={"seam": "productctl acceptance core"},
        evidence=[],
    )
    Draft202012Validator(load_schema("control-envelope.schema.json")).validate(payload)
    assert payload["envelope_version"] == "0.1.0"
