from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from uuid import uuid4

from candidate_core.mutation import MutationGuard


@dataclass
class CommandContext:
    command: str
    run_id: str = field(default_factory=lambda: str(uuid4()))
    contract_path: Path | None = None
    contract: dict[str, Any] | None = None
    evidence_root: Path | None = None
    payload_root: Path | None = None
    search_path: str | None = None
    target_platform: str | None = None
    python_series: str | None = None
    prefix: Path | None = None
    python_executable: str | None = None
    fail_stage: str | None = None
    data_root_override: str | None = None
    mutation: MutationGuard = field(default_factory=MutationGuard)
    stages: list[dict[str, Any]] = field(default_factory=list)
    observations: dict[str, Any] = field(default_factory=dict)
    evidence: list[dict[str, str]] = field(default_factory=list)

    def add_stage(self, payload: dict[str, Any]) -> None:
        self.stages.append(payload)

    def add_observation(self, key: str, value: Any) -> None:
        self.observations[key] = value

    def add_evidence(self, kind: str, path: str, sha256: str | None = None) -> dict[str, str]:
        item: dict[str, str] = {"kind": kind, "path": path}
        if sha256:
            item["sha256"] = sha256
        self.evidence.append(item)
        return item
