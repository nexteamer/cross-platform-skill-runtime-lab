from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from candidate_core.context import CommandContext
from candidate_core.contract import load_and_validate_contract
from candidate_core.envelope import build_envelope, error_payload, stage
from candidate_core.errors import ContractError
from candidate_core.jsonio import write_json
from candidate_core.registry import load_registry, summarize_registry


COMMAND = "acceptance.core"


def run_core(ctx: CommandContext) -> dict[str, Any]:
    if ctx.contract_path is None:
        raise ContractError("a contract path is required", category="incomplete_contract")
    try:
        contract = load_and_validate_contract(ctx.contract_path)
    except ContractError as exc:
        ctx.add_stage(
            stage(
                "contract.validate",
                "failed",
                observations={"contract_path": str(ctx.contract_path)},
                error=error_payload(exc.category, exc.message),
            )
        )
        return build_envelope(
            run_id=ctx.run_id,
            command=COMMAND,
            status="failed",
            stages=ctx.stages,
            observations={"mutation_count": 0, "process_launched": False},
            error=error_payload(exc.category, exc.message),
            mutations=[],
        )

    ctx.contract = contract
    ctx.mutation.allow()
    ctx.add_stage(
        stage(
            "contract.validate",
            "passed",
            observations={
                "contract_path": str(ctx.contract_path),
                "product_id": contract["product"]["id"],
                "confirmed": True,
            },
        )
    )
    ctx.add_observation("product_id", contract["product"]["id"])
    ctx.add_observation("contract_version", contract["contract_version"])

    registry = load_registry()
    summary = summarize_registry(registry)
    ctx.add_stage(
        stage(
            "historical_failures.map",
            "passed",
            observations=summary,
        )
    )
    ctx.add_observation("historical_failures", summary)

    evidence_refs: list[dict[str, str]] = []
    if ctx.evidence_root is not None:
        evidence_refs = _write_run_evidence(ctx)

    ctx.add_stage(
        stage(
            "acceptance.skeleton",
            "passed",
            observations={"seam": "productctl acceptance core"},
            evidence=evidence_refs,
        )
    )
    ctx.add_observation("process_launched", False)
    ctx.add_observation("install_attempted", False)

    envelope = build_envelope(
        run_id=ctx.run_id,
        command=COMMAND,
        status="passed",
        stages=ctx.stages,
        observations=ctx.observations,
        evidence=ctx.evidence,
        mutations=ctx.mutation.as_dicts(),
    )
    if ctx.evidence_root is not None:
        envelope_path = ctx.evidence_root / ctx.run_id / "envelope.json"
        ctx.mutation.record("write", str(envelope_path))
        write_json(envelope_path, envelope)
    return envelope


def _write_run_evidence(ctx: CommandContext) -> list[dict[str, str]]:
    assert ctx.evidence_root is not None
    run_dir = ctx.evidence_root / ctx.run_id
    ctx.mutation.record("mkdir", str(run_dir))
    run_dir.mkdir(parents=True, exist_ok=True)

    receipt = {
        "run_id": ctx.run_id,
        "command": COMMAND,
        "product_id": ctx.contract["product"]["id"] if ctx.contract else None,
        "contract_path": str(ctx.contract_path) if ctx.contract_path else None,
    }
    receipt_path = run_dir / "receipt.json"
    ctx.mutation.record("write", str(receipt_path))
    write_json(receipt_path, receipt)
    sha = hashlib.sha256(receipt_path.read_bytes()).hexdigest()
    ref = ctx.add_evidence("receipt", str(receipt_path), sha)
    return [ref]
