from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    error_category TEXT,
    error_message TEXT,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS stages (
    run_id TEXT NOT NULL,
    name TEXT NOT NULL,
    status TEXT NOT NULL,
    error_category TEXT,
    PRIMARY KEY (run_id, name)
);
"""


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def upsert_run(conn: sqlite3.Connection, run_id: str, status: str, error: dict[str, str] | None = None) -> None:
    conn.execute(
        """
        INSERT INTO runs (id, status, error_category, error_message, created_at)
        VALUES (?, ?, ?, ?, datetime('now'))
        ON CONFLICT(id) DO UPDATE SET
            status=excluded.status,
            error_category=excluded.error_category,
            error_message=excluded.error_message
        """,
        (run_id, status, (error or {}).get("category"), (error or {}).get("message")),
    )
    conn.commit()


def upsert_stage(conn: sqlite3.Connection, run_id: str, name: str, status: str, error_category: str | None = None) -> None:
    conn.execute(
        """
        INSERT INTO stages (run_id, name, status, error_category)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(run_id, name) DO UPDATE SET
            status=excluded.status,
            error_category=excluded.error_category
        """,
        (run_id, name, status, error_category),
    )
    conn.commit()


def get_run(conn: sqlite3.Connection, run_id: str) -> dict[str, Any] | None:
    row = conn.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
    if row is None:
        return None
    stages = conn.execute("SELECT * FROM stages WHERE run_id=?", (run_id,)).fetchall()
    return {
        "id": row["id"],
        "status": row["status"],
        "error_category": row["error_category"],
        "error_message": row["error_message"],
        "created_at": row["created_at"],
        "stages": [dict(stage) for stage in stages],
    }
