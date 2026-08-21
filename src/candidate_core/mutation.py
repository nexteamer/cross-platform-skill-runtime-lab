from __future__ import annotations

from dataclasses import dataclass, field

from candidate_core.errors import MutationDenied


@dataclass
class MutationEvent:
    kind: str
    path: str

    def as_dict(self) -> dict[str, str]:
        return {"kind": self.kind, "path": self.path}


@dataclass
class MutationGuard:
    enabled: bool = False
    events: list[MutationEvent] = field(default_factory=list)

    def allow(self) -> None:
        self.enabled = True

    def record(self, kind: str, path: str) -> MutationEvent:
        if not self.enabled:
            raise MutationDenied(
                f"refusing {kind} at {path} before the contract is accepted"
            )
        event = MutationEvent(kind=kind, path=path)
        self.events.append(event)
        return event

    def as_dicts(self) -> list[dict[str, str]]:
        return [event.as_dict() for event in self.events]
