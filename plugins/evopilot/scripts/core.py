"""EvoPilot's local-first memory, habit analysis, and approval policy."""
from __future__ import annotations

import json
import os
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
SENSITIVE = re.compile(r"(api[_ -]?key|token|password|secret|credential|private[_ -]?key)", re.I)
DANGEROUS = {
    "delete", "destructive", "publish", "send_external", "purchase", "payment",
    "login", "credential", "system_setting", "install_system", "enable_mcp",
    "rotate_key", "make_public", "bulk_overwrite",
}
LOW_RISK = {
    "read", "search", "summarize", "plan", "write_workspace", "edit_workspace",
    "run_tests", "run_build", "analyze", "draft_skill", "draft_mcp", "export_backup",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def data_dir() -> Path:
    root = os.environ.get("PLUGIN_DATA") or os.environ.get("EVOPILOT_DATA")
    path = Path(root) if root else Path.cwd() / ".evopilot"
    path.mkdir(parents=True, exist_ok=True)
    return path


def db_path() -> Path:
    return data_dir() / "evopilot.sqlite3"


def connect() -> sqlite3.Connection:
    db = sqlite3.connect(db_path())
    db.row_factory = sqlite3.Row
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS observations(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          created_at TEXT NOT NULL, session_id TEXT, app TEXT NOT NULL,
          action TEXT NOT NULL, outcome TEXT NOT NULL DEFAULT 'unknown',
          duration_ms INTEGER, metadata_json TEXT NOT NULL DEFAULT '{}'
        );
        CREATE TABLE IF NOT EXISTS memories(
          key TEXT PRIMARY KEY, value TEXT NOT NULL, confidence REAL NOT NULL,
          evidence_count INTEGER NOT NULL, scope TEXT NOT NULL, risk TEXT NOT NULL,
          created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS workflows(
          fingerprint TEXT PRIMARY KEY, app TEXT NOT NULL, pattern TEXT NOT NULL,
          evidence_count INTEGER NOT NULL, success_count INTEGER NOT NULL,
          status TEXT NOT NULL, definition_json TEXT NOT NULL, updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS audit(
          id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL,
          action TEXT NOT NULL, risk TEXT NOT NULL, decision TEXT NOT NULL, reason TEXT NOT NULL
        );
        """
    )
    db.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('schema_version',?)", (str(SCHEMA_VERSION),))
    db.commit()
    return db


@contextmanager
def database():
    db = connect()
    try:
        yield db
        db.commit()
    finally:
        db.close()


def safe_metadata(value: dict[str, Any] | None) -> dict[str, Any]:
    clean: dict[str, Any] = {}
    for key, item in (value or {}).items():
        if SENSITIVE.search(str(key)) or SENSITIVE.search(str(item)):
            clean[key] = "[REDACTED]"
        elif isinstance(item, (str, int, float, bool)) or item is None:
            clean[key] = item
    return clean


def observe(app: str, action: str, outcome: str = "unknown", *, session_id: str = "", duration_ms: int | None = None, metadata: dict[str, Any] | None = None) -> int:
    with database() as db:
        cur = db.execute(
            "INSERT INTO observations(created_at,session_id,app,action,outcome,duration_ms,metadata_json) VALUES(?,?,?,?,?,?,?)",
            (utc_now(), session_id, app[:80], action[:160], outcome[:32], duration_ms, json.dumps(safe_metadata(metadata), ensure_ascii=False)),
        )
        return int(cur.lastrowid)


def remember(key: str, value: str, *, confidence: float = 0.6, scope: str = "global", risk: str = "low") -> dict[str, Any]:
    if SENSITIVE.search(key) or SENSITIVE.search(value):
        raise ValueError("EvoPilot refuses to store secrets or credentials in memory.")
    confidence = max(0.0, min(1.0, confidence))
    now = utc_now()
    with database() as db:
        old = db.execute("SELECT * FROM memories WHERE key=?", (key,)).fetchone()
        if old:
            evidence = int(old["evidence_count"]) + 1
            merged_confidence = min(0.99, max(confidence, float(old["confidence"])) + 0.04)
            db.execute("UPDATE memories SET value=?,confidence=?,evidence_count=?,scope=?,risk=?,updated_at=? WHERE key=?", (value, merged_confidence, evidence, scope, risk, now, key))
        else:
            evidence, merged_confidence = 1, confidence
            db.execute("INSERT INTO memories VALUES(?,?,?,?,?,?,?,?)", (key, value, merged_confidence, evidence, scope, risk, now, now))
    return {"key": key, "value": value, "confidence": merged_confidence, "evidence_count": evidence, "scope": scope, "risk": risk}


def forget(key: str) -> bool:
    with database() as db:
        return db.execute("DELETE FROM memories WHERE key=?", (key,)).rowcount > 0


def memories(scope: str | None = None, limit: int = 30) -> list[dict[str, Any]]:
    with database() as db:
        if scope:
            rows = db.execute("SELECT * FROM memories WHERE scope IN (?, 'global') ORDER BY confidence DESC,updated_at DESC LIMIT ?", (scope, limit)).fetchall()
        else:
            rows = db.execute("SELECT * FROM memories ORDER BY confidence DESC,updated_at DESC LIMIT ?", (limit,)).fetchall()
    return [dict(row) for row in rows]


def analyze_habits(min_count: int = 3) -> list[dict[str, Any]]:
    with database() as db:
        rows = db.execute(
            "SELECT app,action,COUNT(*) evidence,SUM(CASE WHEN outcome='success' THEN 1 ELSE 0 END) successes FROM observations GROUP BY app,action HAVING COUNT(*)>=? ORDER BY evidence DESC",
            (min_count,),
        ).fetchall()
        results = []
        for row in rows:
            evidence, successes = int(row["evidence"]), int(row["successes"])
            confidence = min(0.95, 0.45 + evidence * 0.08 + successes * 0.03)
            status = "stable" if evidence >= 8 and successes >= 3 else "candidate"
            fingerprint = f"{row['app']}::{row['action']}"
            definition = {"trigger": row["action"], "app": row["app"], "success_rate": round(successes / evidence, 2)}
            db.execute(
                "INSERT INTO workflows VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(fingerprint) DO UPDATE SET evidence_count=excluded.evidence_count,success_count=excluded.success_count,status=excluded.status,definition_json=excluded.definition_json,updated_at=excluded.updated_at",
                (fingerprint, row["app"], row["action"], evidence, successes, status, json.dumps(definition), utc_now()),
            )
            results.append({"fingerprint": fingerprint, "evidence": evidence, "successes": successes, "confidence": round(confidence, 2), "status": status, **definition})
        db.commit()
    return results


def review_action(action: str, details: str = "") -> dict[str, str]:
    normalized = action.strip().lower().replace("-", "_").replace(" ", "_")
    if normalized in DANGEROUS or any(term in normalized for term in DANGEROUS):
        result = {"decision": "human_required", "risk": "high", "reason": "This action can affect external systems, permissions, money, credentials, or recoverability."}
    elif normalized in LOW_RISK:
        result = {"decision": "allow", "risk": "low", "reason": "The action is local, scoped, and recoverable."}
    else:
        result = {"decision": "human_required", "risk": "unknown", "reason": "Unknown actions fail closed until a person classifies them."}
    with database() as db:
        db.execute("INSERT INTO audit(created_at,action,risk,decision,reason) VALUES(?,?,?,?,?)", (utc_now(), f"{action}: {details}"[:500], result["risk"], result["decision"], result["reason"]))
    return result


def context(scope: str = "global") -> str:
    items = memories(scope, 12)
    habits = analyze_habits(3)[:8]
    lines = ["EvoPilot local context (explicit user instructions always win):"]
    lines += [f"- Memory [{m['scope']}, {m['confidence']:.2f}]: {m['key']} = {m['value']}" for m in items]
    lines += [f"- Habit [{h['status']}, {h['confidence']:.2f}]: in {h['app']}, {h['trigger']}" for h in habits]
    if len(lines) == 1:
        lines.append("- No learned preferences yet. Observe outcomes before inferring habits.")
    return "\n".join(lines)


def export_data(destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with database() as db:
        payload = {
            "schema_version": SCHEMA_VERSION,
            "exported_at": utc_now(),
            "memories": [dict(x) for x in db.execute("SELECT * FROM memories")],
            "workflows": [dict(x) for x in db.execute("SELECT * FROM workflows")],
            "observations": [dict(x) for x in db.execute("SELECT * FROM observations")],
        }
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return destination
