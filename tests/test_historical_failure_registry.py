from __future__ import annotations

import json
import re
from pathlib import Path

from candidate_core.registry import high_extreme_entries, load_registry, summarize_registry

ROOT = Path(__file__).resolve().parents[1]
COVERAGE = ROOT / "docs" / "planning" / "historical-failure-command-coverage.md"
INDEX = ROOT / "tests" / "fixtures" / "historical_failures" / "index.json"


def _coverage_titles() -> list[str]:
    titles: list[str] = []
    for line in COVERAGE.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| "):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 4 or cells[0] in {"Historical failure class", "---"}:
            continue
        if cells[0].startswith("---"):
            continue
        titles.append(cells[0])
    return titles


def test_registry_matches_coverage_map_and_package_copy() -> None:
    document = load_registry()
    packaged = document["entries"]
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    assert packaged == index["entries"]
    titles = [entry["title"] for entry in packaged]
    assert titles == _coverage_titles()


def test_high_extreme_rows_have_owner_and_proof_lane() -> None:
    document = load_registry()
    rows = high_extreme_entries(document)
    assert rows
    for entry in rows:
        assert entry["owner_layer"], entry["id"]
        assert entry["proof_lane"], entry["id"]
        assert entry["stage"], entry["id"]
        if entry["product_owned"]:
            assert entry["command"]
            assert entry["fixture"]
            fixture = ROOT / entry["fixture"]
            assert fixture.is_file(), entry["id"]
            payload = json.loads(fixture.read_text(encoding="utf-8"))
            assert payload["id"] == entry["id"]
            assert payload["expected_error_category"] == entry["expected_error_category"]
        else:
            assert entry["external_entrypoint"]
            assert entry["fixture"] is None
    summary = summarize_registry(document)
    assert summary["high_extreme_count"] == len(rows)
    assert summary["entry_count"] == len(document["entries"])


def test_coverage_map_still_names_every_row() -> None:
    text = COVERAGE.read_text(encoding="utf-8")
    document = load_registry()
    for entry in document["entries"]:
        assert entry["title"] in text
        if entry["command"]:
            assert re.search(r"productctl|payload verify|runtime discover", text)
