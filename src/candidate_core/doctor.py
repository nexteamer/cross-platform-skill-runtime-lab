from __future__ import annotations

from pathlib import Path
from typing import Any

from candidate_core.codex import resolve_codex
from candidate_core.contract import load_and_validate_contract
from candidate_core.jsonio import load_json
from candidate_core.service import status_service


def run_doctor(*, contract_path: Path, prefix: Path | None = None) -> dict[str, Any]:
    stages: list[dict[str, Any]] = []
    contract = load_and_validate_contract(contract_path)
    stages.append({"id": "contract", "status": "passed", "product_id": contract["product"]["id"]})

    receipt = None
    if prefix is not None:
        receipt_path = prefix / "install" / "receipt.json"
        if not receipt_path.is_file():
            stages.append({"id": "install", "status": "failed", "category": "install_receipt_missing"})
            return {"status": "failed", "failed_stage": "install", "stages": stages, "contract": contract["product"]}
        receipt = load_json(receipt_path)
        python = Path(receipt.get("python") or "")
        if not python.is_file():
            stages.append({"id": "install", "status": "failed", "category": "install_python_missing", "python": str(python)})
            return {"status": "failed", "failed_stage": "install", "stages": stages, "receipt": receipt}
        stages.append({"id": "install", "status": "passed", "python": str(python), "final_dir": receipt.get("final_dir")})

        data_root = Path(receipt.get("data_root") or "")
        if not data_root.exists():
            stages.append({"id": "data_root", "status": "failed", "category": "data_root_missing", "path": str(data_root)})
            return {"status": "failed", "failed_stage": "data_root", "stages": stages, "receipt": receipt}
        stages.append({"id": "data_root", "status": "passed", "path": str(data_root)})

        service = status_service(prefix)
        stages.append({"id": "service", "status": service.get("status"), "owned": service.get("owned"), "state": service.get("state")})

        db = data_root / "short-essay.sqlite"
        stages.append(
            {
                "id": "database",
                "status": "passed",
                "path": str(db),
                "present": db.is_file(),
            }
        )

    resolved = resolve_codex()
    stages.append(
        {
            "id": "codex",
            "status": "passed",
            "resolved": resolved.get("resolved"),
            "silent_fallback": resolved.get("silent_fallback"),
            "candidates": resolved.get("candidates"),
        }
    )
    failed = next((item for item in stages if item.get("status") == "failed"), None)
    return {
        "status": "failed" if failed else "passed",
        "failed_stage": failed["id"] if failed else None,
        "stages": stages,
        "receipt": receipt,
        "product_id": contract["product"]["id"],
    }
