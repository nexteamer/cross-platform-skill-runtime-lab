from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from candidate_core.context import CommandContext
from candidate_core.contract import load_and_validate_contract
from candidate_core.envelope import build_envelope, error_payload, stage
from candidate_core.errors import ContractError
from candidate_core.jsonio import write_json
from candidate_core.payload import current_platform, verify_payload
from candidate_core.registry import load_registry, summarize_registry
from candidate_core.runtime import discover_runtimes


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

    runtime = discover_runtimes(
        contract["runtime"]["discovery"]["required_capabilities"],
        path=ctx.search_path,
    )
    selected_runtime = runtime.get("selected")
    if selected_runtime is None:
        ctx.add_stage(
            stage(
                "runtime.discover",
                "failed",
                observations=runtime,
                error=error_payload(
                    "runtime_not_found",
                    "no Python 3.11 or 3.12 candidate satisfied required capabilities",
                ),
            )
        )
        ctx.add_observation("runtime", runtime)
        return _finish(ctx, status="failed", category="runtime_not_found")

    ctx.add_stage(stage("runtime.discover", "passed", observations=runtime))
    ctx.add_observation("runtime", runtime)

    payload_root = ctx.payload_root
    if payload_root is None and ctx.contract_path is not None:
        payload_root = ctx.contract_path.parent / "payload"
        ctx.payload_root = payload_root

    python_series = selected_runtime["observations"].get("python_series")
    target_platform = ctx.target_platform or current_platform()
    payload = verify_payload(
        payload_root,
        target_platform=target_platform,
        python_series=python_series,
    )
    if payload["status"] != "selected":
        rejected = [
            candidate
            for candidate in payload["candidates"]
            if candidate["status"] == "rejected"
        ]
        first_reason = (
            rejected[0]["reasons"][0]["category"]
            if rejected and rejected[0]["reasons"]
            else "payload_rejected"
        )
        ctx.add_stage(
            stage(
                "payload.verify",
                "failed",
                observations=payload,
                error=error_payload(first_reason, "payload verification rejected one or more required files"),
            )
        )
        ctx.add_observation("payload", payload)
        return _finish(ctx, status="failed", category=first_reason)

    ctx.add_stage(stage("payload.verify", "passed", observations=payload))
    ctx.add_observation("payload", payload)
    ctx.add_observation("process_launched", False)
    ctx.add_observation("install_attempted", False)
    ctx.add_stage(
        stage(
            "acceptance.skeleton",
            "passed",
            observations={"seam": "productctl acceptance core"},
        )
    )
    return _finish(ctx, status="passed")


def _finish(ctx: CommandContext, *, status: str, category: str | None = None) -> dict[str, Any]:
    ctx.add_observation("process_launched", ctx.observations.get("process_launched", False))
    ctx.add_observation("install_attempted", ctx.observations.get("install_attempted", False))
    if ctx.evidence_root is not None:
        _write_run_evidence(ctx)
    error = None if status == "passed" else error_payload(
        category or "failed",
        next((item["error"]["message"] for item in reversed(ctx.stages) if item.get("error")), "acceptance failed"),
    )
    envelope = build_envelope(
        run_id=ctx.run_id,
        command=COMMAND,
        status=status,
        stages=ctx.stages,
        observations=ctx.observations,
        evidence=ctx.evidence,
        error=error,
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
