"""EvoPilot's local-first memory, workflow learning, and approval policy."""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sqlite3
import sys
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 2
SENSITIVE = re.compile(
    r"(api[_ -]?key|access[_ -]?token|refresh[_ -]?token|token|password|passcode|"
    r"secret|credential|private[_ -]?key|ssh[_ -]?key|authorization|"
    r"auth[_ -]?header|bearer(?:\s+|%20)|cookie|session[_ -]?token)",
    re.I,
)
DANGEROUS = {
    "delete", "destructive", "publish", "send_external", "purchase", "payment",
    "login", "credential", "system_setting", "install_system", "enable_mcp",
    "rotate_key", "make_public", "bulk_overwrite",
}
LOW_RISK = {
    "read", "search", "summarize", "plan", "write_workspace", "edit_workspace",
    "run_tests", "run_build", "analyze", "draft_skill", "compile_skill", "validate_skill", "draft_mcp", "export_backup",
}
MEMORY_SOURCES = {"explicit", "inferred"}
ACTIVE_MEMORY = "active"
DECAY_HALF_LIFE_DAYS = 90
APPROVAL_TTL_MINUTES = 10


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _parse_time(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return datetime.now(timezone.utc)


def data_dir() -> Path:
    root = os.environ.get("PLUGIN_DATA") or os.environ.get("EVOPILOT_DATA")
    path = Path(root) if root else Path.cwd() / ".evopilot"
    path.mkdir(parents=True, exist_ok=True)
    return path


def db_path() -> Path:
    return data_dir() / "evopilot.sqlite3"


def _columns(db: sqlite3.Connection, table: str) -> set[str]:
    return {str(row[1]) for row in db.execute(f"PRAGMA table_info({table})")}


def _add_column(db: sqlite3.Connection, table: str, name: str, declaration: str) -> None:
    if name not in _columns(db, table):
        db.execute(f"ALTER TABLE {table} ADD COLUMN {name} {declaration}")


def connect() -> sqlite3.Connection:
    db = sqlite3.connect(db_path(), timeout=5.0)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA busy_timeout=5000")
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
          created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
          source TEXT NOT NULL DEFAULT 'explicit', status TEXT NOT NULL DEFAULT 'active',
          negative_evidence INTEGER NOT NULL DEFAULT 0, last_confirmed_at TEXT
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
        CREATE TABLE IF NOT EXISTS memory_events(
          id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL,
          key TEXT NOT NULL, event TEXT NOT NULL, source TEXT NOT NULL,
          previous_value TEXT, proposed_value TEXT, scope TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS approvals(
          approval_id TEXT PRIMARY KEY, created_at TEXT NOT NULL, expires_at TEXT NOT NULL,
          consumed_at TEXT, label TEXT NOT NULL
        );
        """
    )
    _add_column(db, "memories", "source", "TEXT NOT NULL DEFAULT 'explicit'")
    _add_column(db, "memories", "status", "TEXT NOT NULL DEFAULT 'active'")
    _add_column(db, "memories", "negative_evidence", "INTEGER NOT NULL DEFAULT 0")
    _add_column(db, "memories", "last_confirmed_at", "TEXT")
    db.execute("UPDATE memories SET last_confirmed_at=updated_at WHERE last_confirmed_at IS NULL")
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


def _memory_event(db: sqlite3.Connection, key: str, event: str, source: str, previous: str | None, proposed: str | None, scope: str) -> None:
    db.execute(
        "INSERT INTO memory_events(created_at,key,event,source,previous_value,proposed_value,scope) VALUES(?,?,?,?,?,?,?)",
        (utc_now(), key, event, source, previous, proposed, scope),
    )


def remember(key: str, value: str, *, confidence: float = 0.6, scope: str = "global", risk: str = "low", source: str = "explicit") -> dict[str, Any]:
    if SENSITIVE.search(key) or SENSITIVE.search(value):
        raise ValueError("EvoPilot refuses to store secrets or credentials in memory.")
    if source not in MEMORY_SOURCES:
        raise ValueError("Memory source must be 'explicit' or 'inferred'.")
    confidence = max(0.0, min(1.0, confidence))
    now = utc_now()
    with database() as db:
        old = db.execute("SELECT * FROM memories WHERE key=?", (key,)).fetchone()
        if not old:
            evidence, merged_confidence = 1, confidence
            db.execute(
                "INSERT INTO memories(key,value,confidence,evidence_count,scope,risk,created_at,updated_at,source,status,negative_evidence,last_confirmed_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                (key, value, merged_confidence, evidence, scope, risk, now, now, source, ACTIVE_MEMORY, 0, now),
            )
            _memory_event(db, key, "created", source, None, value, scope)
            status = ACTIVE_MEMORY
        elif old["value"] == value:
            evidence = int(old["evidence_count"]) + 1
            merged_confidence = min(0.99, max(confidence, float(old["confidence"])) + 0.04)
            effective_source = "explicit" if source == "explicit" else str(old["source"])
            db.execute(
                "UPDATE memories SET confidence=?,evidence_count=?,scope=?,risk=?,source=?,status='active',updated_at=?,last_confirmed_at=? WHERE key=?",
                (merged_confidence, evidence, scope, risk, effective_source, now, now, key),
            )
            _memory_event(db, key, "confirmed", source, value, value, scope)
            status = ACTIVE_MEMORY
            source = effective_source
        elif source == "explicit":
            evidence = int(old["evidence_count"]) + 1
            merged_confidence = max(confidence, 0.8)
            db.execute(
                "UPDATE memories SET value=?,confidence=?,evidence_count=?,scope=?,risk=?,source='explicit',status='active',negative_evidence=negative_evidence+1,updated_at=?,last_confirmed_at=? WHERE key=?",
                (value, merged_confidence, evidence, scope, risk, now, now, key),
            )
            _memory_event(db, key, "corrected", source, str(old["value"]), value, scope)
            status = ACTIVE_MEMORY
        else:
            evidence = int(old["evidence_count"])
            merged_confidence = float(old["confidence"])
            new_status = "conflict" if old["source"] == "inferred" else ACTIVE_MEMORY
            db.execute(
                "UPDATE memories SET status=?,negative_evidence=negative_evidence+1,updated_at=? WHERE key=?",
                (new_status, now, key),
            )
            _memory_event(db, key, "conflict", source, str(old["value"]), value, scope)
            return {
                "key": key, "value": old["value"], "proposed_value": value,
                "confidence": merged_confidence, "evidence_count": evidence,
                "scope": old["scope"], "risk": old["risk"], "source": old["source"],
                "status": "conflict", "stored_value_changed": False,
            }
    return {
        "key": key, "value": value, "confidence": merged_confidence,
        "evidence_count": evidence, "scope": scope, "risk": risk,
        "source": source, "status": status, "stored_value_changed": True,
    }


def correct_memory(key: str, value: str, *, scope: str | None = None) -> dict[str, Any]:
    with database() as db:
        old = db.execute("SELECT scope,risk FROM memories WHERE key=?", (key,)).fetchone()
    return remember(key, value, confidence=0.9, scope=scope or (old["scope"] if old else "global"), risk=(old["risk"] if old else "low"), source="explicit")


def forget(key: str) -> bool:
    with database() as db:
        old = db.execute("SELECT value,scope,source FROM memories WHERE key=?", (key,)).fetchone()
        if not old:
            return False
        _memory_event(db, key, "forgotten", str(old["source"]), str(old["value"]), None, str(old["scope"]))
        return db.execute("DELETE FROM memories WHERE key=?", (key,)).rowcount > 0


def _effective_confidence(row: sqlite3.Row) -> float:
    confidence = float(row["confidence"])
    if row["source"] == "explicit":
        return confidence
    age = max(0.0, (datetime.now(timezone.utc) - _parse_time(row["last_confirmed_at"] or row["updated_at"])).total_seconds() / 86400)
    return max(0.05, confidence * math.pow(0.5, age / DECAY_HALF_LIFE_DAYS))


def memories(scope: str | None = None, limit: int = 30) -> list[dict[str, Any]]:
    with database() as db:
        if scope:
            rows = db.execute("SELECT * FROM memories WHERE status='active' AND scope IN (?, 'global')", (scope,)).fetchall()
        else:
            rows = db.execute("SELECT * FROM memories WHERE status='active'").fetchall()
    items = [{**dict(row), "effective_confidence": round(_effective_confidence(row), 3)} for row in rows]
    return sorted(items, key=lambda item: (item["effective_confidence"], item["updated_at"]), reverse=True)[:limit]


def memory_history(key: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
    with database() as db:
        if key:
            rows = db.execute("SELECT * FROM memory_events WHERE key=? ORDER BY id DESC LIMIT ?", (key, limit)).fetchall()
        else:
            rows = db.execute("SELECT * FROM memory_events ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [dict(row) for row in rows]


def _workflow_status(evidence: int, successes: int) -> str:
    if evidence >= 8 and successes >= 3:
        return "stable"
    if evidence >= 5 and successes >= 3:
        return "draft_ready"
    return "candidate"


def _upsert_workflow(db: sqlite3.Connection, fingerprint: str, app: str, pattern: str, evidence: int, successes: int, definition: dict[str, Any]) -> dict[str, Any]:
    status = _workflow_status(evidence, successes)
    db.execute(
        "INSERT INTO workflows VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(fingerprint) DO UPDATE SET evidence_count=excluded.evidence_count,success_count=excluded.success_count,status=excluded.status,definition_json=excluded.definition_json,updated_at=excluded.updated_at",
        (fingerprint, app, pattern, evidence, successes, status, json.dumps(definition, ensure_ascii=False), utc_now()),
    )
    confidence = min(0.97, 0.35 + evidence * 0.07 + successes * 0.04)
    return {"fingerprint": fingerprint, "evidence": evidence, "successes": successes, "confidence": round(confidence, 2), "status": status, **definition}


def analyze_habits(min_count: int = 3) -> list[dict[str, Any]]:
    with database() as db:
        rows = db.execute(
            "SELECT app,action,COUNT(*) evidence,SUM(CASE WHEN outcome='success' THEN 1 ELSE 0 END) successes FROM observations GROUP BY app,action HAVING COUNT(*)>=? ORDER BY evidence DESC",
            (min_count,),
        ).fetchall()
        results = []
        for row in rows:
            evidence, successes = int(row["evidence"]), int(row["successes"])
            fingerprint = f"habit::{row['app']}::{row['action']}"
            definition = {"kind": "habit", "trigger": row["action"], "app": row["app"], "steps": [row["action"]], "success_rate": round(successes / evidence, 2)}
            results.append(_upsert_workflow(db, fingerprint, row["app"], row["action"], evidence, successes, definition))
    return results


def analyze_sequences(min_count: int = 3, max_length: int = 4) -> list[dict[str, Any]]:
    max_length = max(2, min(6, max_length))
    counts: Counter[tuple[str, ...]] = Counter()
    successes: Counter[tuple[str, ...]] = Counter()
    with database() as db:
        sessions = db.execute("SELECT DISTINCT session_id FROM observations WHERE session_id IS NOT NULL AND session_id<>''").fetchall()
        for session in sessions:
            rows = db.execute("SELECT app,action,outcome FROM observations WHERE session_id=? ORDER BY id", (session[0],)).fetchall()
            events = [(f"{row['app']}:{row['action']}", str(row["outcome"])) for row in rows]
            for size in range(2, max_length + 1):
                for start in range(0, len(events) - size + 1):
                    window = events[start:start + size]
                    pattern = tuple(item[0] for item in window)
                    if len(set(pattern)) < 2:
                        continue
                    counts[pattern] += 1
                    if window[-1][1] == "success" and all(item[1] not in {"failure", "abandoned"} for item in window):
                        successes[pattern] += 1
        results = []
        for pattern, evidence in counts.most_common():
            if evidence < min_count:
                continue
            success_count = successes[pattern]
            fingerprint = "sequence::" + hashlib.sha256("\n".join(pattern).encode()).hexdigest()[:16]
            app = pattern[0].split(":", 1)[0]
            definition = {"kind": "sequence", "trigger": pattern[0], "app": app, "steps": list(pattern), "success_rate": round(success_count / evidence, 2)}
            results.append(_upsert_workflow(db, fingerprint, app, " -> ".join(pattern), evidence, success_count, definition))
    return results


def review_action(action: str, details: str = "") -> dict[str, str]:
    normalized = action.strip().lower().replace("-", "_").replace(" ", "_")
    normalized_details = details.strip().lower().replace("-", "_").replace(" ", "_")
    risk_text = f"{normalized} {normalized_details}"
    if any(term in risk_text for term in DANGEROUS) or SENSITIVE.search(details):
        result = {"decision": "human_required", "risk": "high", "reason": "This action can affect external systems, permissions, money, credentials, or recoverability."}
    elif normalized in LOW_RISK:
        result = {"decision": "allow", "risk": "low", "reason": "The action is local, scoped, and recoverable."}
    else:
        result = {"decision": "human_required", "risk": "unknown", "reason": "Unknown actions fail closed until a person classifies them."}
    with database() as db:
        db.execute("INSERT INTO audit(created_at,action,risk,decision,reason) VALUES(?,?,?,?,?)", (utc_now(), f"{action}: {details}"[:500], result["risk"], result["decision"], result["reason"]))
    return result


def approval_fingerprint(tool_name: str, tool_input: Any) -> str:
    canonical = json.dumps(tool_input, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(f"{tool_name}\n{canonical}".encode()).hexdigest()[:24]


def authorize_once(approval_id: str, label: str = "human-confirmed action") -> dict[str, Any]:
    if not re.fullmatch(r"[0-9a-f]{24}", approval_id):
        raise ValueError("approval_id must be the 24-character ID shown by the EvoPilot safety gate.")
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=APPROVAL_TTL_MINUTES)
    with database() as db:
        db.execute(
            "INSERT OR REPLACE INTO approvals(approval_id,created_at,expires_at,consumed_at,label) VALUES(?,?,?,?,?)",
            (approval_id, now.isoformat(timespec="seconds"), expires.isoformat(timespec="seconds"), None, label[:120]),
        )
        db.execute("INSERT INTO audit(created_at,action,risk,decision,reason) VALUES(?,?,?,?,?)", (utc_now(), f"approval:{approval_id}", "high", "allow_once", label[:500]))
    return {"approval_id": approval_id, "authorized": True, "expires_at": expires.isoformat(timespec="seconds"), "uses": 1}


def consume_approval(approval_id: str) -> bool:
    now = datetime.now(timezone.utc)
    with database() as db:
        row = db.execute("SELECT expires_at,consumed_at FROM approvals WHERE approval_id=?", (approval_id,)).fetchone()
        if not row or row["consumed_at"] or _parse_time(row["expires_at"]) < now:
            return False
        return db.execute("UPDATE approvals SET consumed_at=? WHERE approval_id=? AND consumed_at IS NULL", (now.isoformat(timespec="seconds"), approval_id)).rowcount == 1


def audit_gate(action: str, decision: str, reason: str) -> None:
    with database() as db:
        db.execute("INSERT INTO audit(created_at,action,risk,decision,reason) VALUES(?,?,?,?,?)", (utc_now(), action[:500], "high", decision, reason[:500]))


def context(scope: str = "global") -> str:
    items = memories(scope, 12)
    sequences = analyze_sequences(3, 4)[:5]
    habits = analyze_habits(3)[:5]
    lines = ["EvoPilot local context (explicit user instructions always win):"]
    lines += [f"- Memory [{m['scope']}, {m['source']}, {m['effective_confidence']:.2f}]: {m['key']} = {m['value']}" for m in items]
    lines += [f"- Workflow [{w['status']}, {w['confidence']:.2f}]: {' -> '.join(w['steps'])}" for w in sequences]
    lines += [f"- Habit [{h['status']}, {h['confidence']:.2f}]: in {h['app']}, {h['trigger']}" for h in habits]
    if len(lines) == 1:
        lines.append("- No learned preferences yet. Observe outcomes before inferring habits.")
    return "\n".join(lines)


def weekly_report(days: int = 7) -> str:
    days = max(1, min(90, days))
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat(timespec="seconds")
    with database() as db:
        rows = db.execute("SELECT action,outcome,duration_ms FROM observations WHERE created_at>=?", (since,)).fetchall()
        corrections = db.execute("SELECT COUNT(*) FROM memory_events WHERE created_at>=? AND event='corrected'", (since,)).fetchone()[0]
        conflicts = db.execute("SELECT COUNT(*) FROM memory_events WHERE created_at>=? AND event='conflict'", (since,)).fetchone()[0]
    total = len(rows)
    outcomes = Counter(str(row["outcome"]) for row in rows)
    actions = Counter(str(row["action"]) for row in rows)
    completed = outcomes["success"] + outcomes["failure"]
    success_rate = (outcomes["success"] / completed * 100) if completed else 0.0
    durations = [int(row["duration_ms"]) for row in rows if row["duration_ms"] is not None]
    sequences = analyze_sequences(3, 4)
    ready = [item for item in sequences if item["status"] in {"draft_ready", "stable"}]
    lines = [
        f"# EvoPilot learning report ({days} days)", "",
        f"- Observations: {total}",
        f"- Completed outcomes: {completed} ({success_rate:.0f}% successful)",
        f"- Failures / abandoned: {outcomes['failure']} / {outcomes['abandoned']}",
        f"- Memory corrections / conflicts: {corrections} / {conflicts}",
    ]
    if durations:
        lines.append(f"- Average measured duration: {sum(durations) / len(durations):.0f} ms")
    lines += ["", "## Most-used actions"]
    lines += [f"- {action}: {count}" for action, count in actions.most_common(5)] or ["- Not enough observations yet."]
    lines += ["", "## Workflow candidates"]
    lines += [f"- {item['status']}: {' -> '.join(item['steps'])} ({item['evidence']} runs, {item['success_rate']:.0%} success)" for item in sequences[:5]] or ["- No repeated multi-step sequence has reached three observations yet."]
    lines += ["", "## Recommended next step"]
    if ready:
        lines.append(f"- Review and compile the strongest proven sequence: {' -> '.join(ready[0]['steps'])}.")
    elif outcomes["failure"] or outcomes["abandoned"]:
        lines.append("- Inspect the most frequent failed action before automating more work.")
    else:
        lines.append("- Keep collecting privacy-minimized outcomes; no workflow is ready for promotion yet.")
    return "\n".join(lines)


def _skill_name(pattern: str) -> str:
    name = re.sub(r"[^a-z0-9]+", "-", pattern.lower()).strip("-")[:48]
    return name or "evopilot-workflow"


def validate_skill_bundle(bundle: Path) -> dict[str, Any]:
    """Structurally validate and score a compiled Skill bundle without executing it."""
    bundle = Path(bundle).resolve()
    skill_file = bundle / "SKILL.md"
    evidence_file = bundle / "evopilot.json"
    checks: list[dict[str, Any]] = []

    def add(name: str, weight: int, passed: bool, detail: str) -> None:
        checks.append({"name": name, "weight": weight, "passed": bool(passed), "detail": detail})

    files_ok = bundle.is_dir() and skill_file.is_file() and evidence_file.is_file()
    add("required_files", 10, files_ok, "SKILL.md and evopilot.json are present" if files_ok else "bundle must contain SKILL.md and evopilot.json")

    skill_text = skill_file.read_text(encoding="utf-8") if skill_file.is_file() else ""
    frontmatter: dict[str, str] = {}
    if skill_text.startswith("---\n"):
        closing = skill_text.find("\n---\n", 4)
        if closing != -1:
            for line in skill_text[4:closing].splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    frontmatter[key.strip()] = value.strip()
    name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")
    frontmatter_ok = bool(re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", name)) and 1 <= len(description) <= 1024
    add("frontmatter", 10, frontmatter_ok, "valid name and description" if frontmatter_ok else "frontmatter needs a valid lowercase name and non-empty description")
    name_ok = bool(name) and name == bundle.name
    add("name_matches_directory", 5, name_ok, "Skill name matches its directory" if name_ok else "frontmatter name must match the bundle directory")

    manifest: dict[str, Any] = {}
    manifest_error = ""
    if evidence_file.is_file():
        try:
            loaded = json.loads(evidence_file.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                manifest = loaded
            else:
                manifest_error = "manifest root must be an object"
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            manifest_error = f"{type(exc).__name__}: {exc}"
    else:
        manifest_error = "evopilot.json is missing"
    generator = manifest.get("generator", {}) if isinstance(manifest.get("generator"), dict) else {}
    manifest_ok = bool(manifest) and manifest.get("schema_version") == 1 and generator.get("name") == "EvoPilot"
    add("manifest", 10, manifest_ok, "recognized EvoPilot evidence manifest" if manifest_ok else manifest_error or "unrecognized evidence manifest")

    workflow = manifest.get("workflow", {}) if isinstance(manifest.get("workflow"), dict) else {}
    steps = workflow.get("steps", [])
    workflow_ok = isinstance(steps, list) and len(steps) >= 2 and all(isinstance(step, str) and step.strip() for step in steps)
    add("workflow", 10, workflow_ok, f"{len(steps)} ordered steps" if workflow_ok else "workflow needs at least two non-empty ordered steps")

    evidence = manifest.get("evidence", {}) if isinstance(manifest.get("evidence"), dict) else {}
    observations = evidence.get("observations")
    successes = evidence.get("successful_outcomes")
    success_rate = evidence.get("success_rate")
    numbers_ok = (
        isinstance(observations, int) and not isinstance(observations, bool)
        and isinstance(successes, int) and not isinstance(successes, bool)
        and isinstance(success_rate, (int, float)) and not isinstance(success_rate, bool)
        and observations >= successes >= 0
    )
    expected_rate = successes / observations if numbers_ok and observations else 0.0
    evidence_ok = numbers_ok and abs(float(success_rate) - expected_rate) <= 0.001
    add("evidence_consistency", 10, evidence_ok, "counts and success rate agree" if evidence_ok else "observation count, success count, and success rate are inconsistent")

    status = workflow.get("status")
    threshold_ok = evidence_ok and (
        (status == "draft_ready" and observations >= 5 and successes >= 3)
        or (status == "stable" and observations >= 8 and successes >= 3)
    )
    add("promotion_threshold", 15, threshold_ok, f"{status} threshold is satisfied" if threshold_ok else "workflow does not satisfy its declared promotion threshold")

    normalized_skill = skill_text.casefold()
    safety_ok = all(fragment in normalized_skill for fragment in ("explicit user instructions", "human approval", "stop and ask"))
    add("safety_boundaries", 15, safety_ok, "instruction priority, approval, and stop conditions are present" if safety_ok else "Skill is missing one or more required safety boundaries")

    review = manifest.get("review", {}) if isinstance(manifest.get("review"), dict) else {}
    review_ok = review.get("state") == "pending_human_review" and review.get("installed") is False
    add("human_review", 10, review_ok, "bundle remains uninstalled and pending review" if review_ok else "bundle must remain uninstalled and pending human review")
    portability_ok = manifest.get("format") == "open-agent-skills" and manifest.get("portable") is True
    add("portability", 5, portability_ok, "Open Agent Skills format declared" if portability_ok else "portable Open Agent Skills format is not declared")

    score = sum(item["weight"] for item in checks if item["passed"])
    valid = all(item["passed"] for item in checks)
    simulated = manifest.get("simulated") is True
    recommendation = "demo_only" if simulated and valid else "ready_for_human_review" if valid else "needs_revision"
    return {
        "valid": valid,
        "score": score,
        "recommendation": recommendation,
        "simulated": simulated,
        "checks": checks,
        "limitations": [
            "Structural validation does not execute the workflow.",
            "A passing score does not prove compatibility with every agent client.",
        ],
    }


def _write_skill_bundle(
    *,
    fingerprint: str,
    pattern: str,
    definition: dict[str, Any],
    evidence_count: int,
    success_count: int,
    status: str,
    destination: Path,
    simulated: bool = False,
) -> dict[str, Any]:
    name = _skill_name(pattern)
    skill_dir = Path(destination).resolve() / name
    skill_file = skill_dir / "SKILL.md"
    evidence_file = skill_dir / "evopilot.json"
    if skill_dir.exists():
        raise FileExistsError(f"Bundle already exists: {skill_dir}")
    skill_dir.mkdir(parents=True, exist_ok=False)
    steps = "\n".join(f"{index}. {step}" for index, step in enumerate(definition.get("steps", []), 1))
    completed = max(0, int(evidence_count))
    successful = max(0, min(int(success_count), completed))
    success_rate = successful / completed if completed else 0.0
    demo_note = " This evidence is simulated for demonstration only." if simulated else ""
    body = f"""---
name: {name}
description: Run a locally learned workflow only when the user's task matches its trigger and the required tools are already authorized.
---

# {name.replace('-', ' ').title()}

This is an EvoPilot-generated portable Skill bundle. A person must review and validate it before installation.{demo_note}

## Evidence

- Fingerprint: `{fingerprint}`
- Observations: {completed}
- Successful outcomes: {successful}
- Success rate: {success_rate:.0%}
- Status: {status}

## Workflow

{steps}

## Safety

- Keep explicit user instructions above learned behavior.
- Do not expand permissions, publish, delete material data, or use credentials without human approval.
- Stop and ask when the current task does not match this learned sequence.
"""
    evidence = {
        "schema_version": 1,
        "generated_at": utc_now(),
        "generator": {"name": "EvoPilot", "version": "0.3.1"},
        "format": "open-agent-skills",
        "portable": True,
        "simulated": simulated,
        "workflow": {
            "fingerprint": fingerprint,
            "pattern": pattern,
            "steps": definition.get("steps", []),
            "status": status,
        },
        "evidence": {
            "observations": completed,
            "successful_outcomes": successful,
            "success_rate": success_rate,
        },
        "review": {"state": "pending_human_review", "installed": False},
    }
    skill_file.write_text(body, encoding="utf-8")
    evidence_file.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    result = {
        "path": str(skill_file),
        "bundle": str(skill_dir),
        "evidence_path": str(evidence_file),
        "name": name,
        "status": "compiled",
        "format": "open-agent-skills",
        "installed": False,
        "requires_human_review": True,
        "simulated": simulated,
    }
    result["validation"] = validate_skill_bundle(skill_dir)
    return result


def compile_skill(fingerprint: str, destination: Path) -> dict[str, Any]:
    with database() as db:
        row = db.execute("SELECT * FROM workflows WHERE fingerprint=?", (fingerprint,)).fetchone()
    if not row:
        raise ValueError("Unknown workflow fingerprint. Run sequence analysis first.")
    if row["status"] not in {"draft_ready", "stable"}:
        raise ValueError("Workflow needs at least five observations and three successful outcomes before compilation.")
    definition = json.loads(row["definition_json"])
    return _write_skill_bundle(
        fingerprint=fingerprint,
        pattern=str(row["pattern"]),
        definition=definition,
        evidence_count=int(row["evidence_count"]),
        success_count=int(row["success_count"]),
        status=str(row["status"]),
        destination=destination,
    )


def draft_skill(fingerprint: str, destination: Path) -> dict[str, Any]:
    """Backward-compatible alias for compile_skill."""
    return compile_skill(fingerprint, destination)


def demo(destination: Path | None = None) -> dict[str, Any]:
    """Return an honest, deterministic workflow-compiler demo without touching user data."""
    steps = ["workspace:inspect", "workspace:apply_patch", "terminal:test"]
    pattern = " -> ".join(steps)
    fingerprint = hashlib.sha256(pattern.encode("utf-8")).hexdigest()[:16]
    result: dict[str, Any] = {
        "simulated": True,
        "headline": "Repeated work becomes a reviewable, portable Agent Skill.",
        "workflow": {"fingerprint": fingerprint, "steps": steps, "status": "draft_ready"},
        "evidence": {"observations": 5, "successful_outcomes": 4, "success_rate": 0.8},
        "stages": ["observe outcomes", "detect a repeated sequence", "compile a Skill bundle", "validate structure and evidence", "human review before installation"],
        "user_data_changed": False,
    }
    if destination is not None:
        result["artifact"] = _write_skill_bundle(
            fingerprint=fingerprint,
            pattern=pattern,
            definition={"steps": steps},
            evidence_count=5,
            success_count=4,
            status="draft_ready",
            destination=destination,
            simulated=True,
        )
    return result


def doctor(plugin_root: Path | None = None) -> dict[str, Any]:
    """Check the local runtime, plugin files, and database without exposing stored content."""
    root = Path(plugin_root or os.environ.get("PLUGIN_ROOT") or Path(__file__).resolve().parents[1]).resolve()
    checks: list[dict[str, Any]] = []

    def add(name: str, ok: bool, detail: str, severity: str = "error") -> None:
        checks.append({"name": name, "status": "ok" if ok else severity, "detail": detail})

    version_ok = sys.version_info >= (3, 10)
    add("python", version_ok, f"Python {sys.version.split()[0]} (3.10+ required)")
    required = [root / ".mcp.json", root / "hooks" / "hooks.json", root / "mcp" / "server.py"]
    missing = [path.relative_to(root).as_posix() for path in required if not path.is_file()]
    add("plugin_files", not missing, "required files present" if not missing else f"missing: {', '.join(missing)}")
    try:
        with database() as db:
            schema = int(db.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()[0])
            observations = int(db.execute("SELECT COUNT(*) FROM observations").fetchone()[0])
            active_memories = int(db.execute("SELECT COUNT(*) FROM memories WHERE status='active'").fetchone()[0])
        add("database", schema == SCHEMA_VERSION, f"schema {schema}; {observations} observations; {active_memories} active memories")
    except Exception as exc:
        add("database", False, f"{type(exc).__name__}: {exc}")
    ok = all(item["status"] == "ok" for item in checks)
    return {
        "ok": ok,
        "version": "0.3.1",
        "checks": checks,
        "next_step": "Run `evopilot demo --destination <folder>` to see the workflow compiler." if ok else "Fix the failing checks, then run doctor again.",
    }


def export_data(destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with database() as db:
        payload = {
            "schema_version": SCHEMA_VERSION,
            "exported_at": utc_now(),
            "memories": [dict(x) for x in db.execute("SELECT * FROM memories")],
            "memory_events": [dict(x) for x in db.execute("SELECT * FROM memory_events")],
            "workflows": [dict(x) for x in db.execute("SELECT * FROM workflows")],
            "observations": [dict(x) for x in db.execute("SELECT * FROM observations")],
            "audit": [dict(x) for x in db.execute("SELECT * FROM audit")],
        }
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return destination
