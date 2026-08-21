from __future__ import annotations

from typing import Any

from candidate_core.errors import ProductctlError
from candidate_core.resources import load_registry_document

HIGH_SEVERITIES = {"high", "extreme"}


def load_registry() -> dict[str, Any]:
    document = load_registry_document()
    entries = document.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ProductctlError("historical failure registry is empty", category="registry_invalid")
    return document


def high_extreme_entries(document: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        entry
        for entry in document["entries"]
        if str(entry.get("severity", "")).lower() in HIGH_SEVERITIES
    ]


def summarize_registry(document: dict[str, Any]) -> dict[str, Any]:
    entries = high_extreme_entries(document)
    missing = [
        entry["id"]
        for entry in entries
        if not entry.get("owner_layer") or not entry.get("proof_lane")
    ]
    if missing:
        raise ProductctlError(
            "historical failure rows missing owner or proof lane: " + ", ".join(missing),
            category="registry_incomplete",
        )
    return {
        "registry_version": document.get("registry_version"),
        "entry_count": len(document["entries"]),
        "high_extreme_count": len(entries),
        "product_owned_high_extreme": sum(1 for entry in entries if entry.get("product_owned")),
        "external_high_extreme": sum(1 for entry in entries if not entry.get("product_owned")),
    }
