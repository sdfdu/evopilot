#!/usr/bin/env python3
"""Dependency-free stdio MCP server exposing EvoPilot's local tools."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("PLUGIN_ROOT", Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(ROOT / "scripts"))
from core import (  # noqa: E402
    analyze_habits, analyze_sequences, authorize_once, context, correct_memory,
    draft_skill, export_data, forget, memory_history, observe, remember,
    review_action, weekly_report,
)

SERVER_VERSION = "0.2.0"
FALLBACK_PROTOCOL_VERSION = "2025-06-18"

TOOLS = [
    {"name": "evopilot_observe", "description": "Record a privacy-minimized work observation and outcome for later workflow analysis.", "inputSchema": {"type": "object", "properties": {"app": {"type": "string"}, "action": {"type": "string"}, "outcome": {"type": "string", "enum": ["unknown", "success", "failure", "abandoned"]}, "session_id": {"type": "string"}}, "required": ["app", "action"]}},
    {"name": "evopilot_remember", "description": "Store a non-sensitive explicit or inferred preference. Inferences never silently replace conflicting values.", "inputSchema": {"type": "object", "properties": {"key": {"type": "string"}, "value": {"type": "string"}, "scope": {"type": "string"}, "confidence": {"type": "number", "minimum": 0, "maximum": 1}, "source": {"type": "string", "enum": ["explicit", "inferred"]}}, "required": ["key", "value"]}},
    {"name": "evopilot_correct_memory", "description": "Explicitly correct a memory while preserving its history.", "inputSchema": {"type": "object", "properties": {"key": {"type": "string"}, "value": {"type": "string"}, "scope": {"type": "string"}}, "required": ["key", "value"]}},
    {"name": "evopilot_memory_history", "description": "Inspect memory creation, confirmation, correction, conflict, and deletion events.", "inputSchema": {"type": "object", "properties": {"key": {"type": "string"}, "limit": {"type": "integer", "minimum": 1, "maximum": 200}}}},
    {"name": "evopilot_forget", "description": "Delete one memory by exact key while retaining a deletion audit event.", "inputSchema": {"type": "object", "properties": {"key": {"type": "string"}}, "required": ["key"]}},
    {"name": "evopilot_context", "description": "Retrieve concise relevant memories and learned workflows for the current scope.", "inputSchema": {"type": "object", "properties": {"scope": {"type": "string"}}}},
    {"name": "evopilot_analyze_habits", "description": "Detect repeated individual actions without inferring a preference from one event.", "inputSchema": {"type": "object", "properties": {"min_count": {"type": "integer", "minimum": 2, "maximum": 20}}}},
    {"name": "evopilot_analyze_sequences", "description": "Detect repeated two-to-four-step workflows and measure their outcomes.", "inputSchema": {"type": "object", "properties": {"min_count": {"type": "integer", "minimum": 2, "maximum": 20}, "max_length": {"type": "integer", "minimum": 2, "maximum": 6}}}},
    {"name": "evopilot_draft_skill", "description": "Create an uninstalled Skill draft only from a workflow that passed evidence thresholds.", "inputSchema": {"type": "object", "properties": {"fingerprint": {"type": "string"}, "destination": {"type": "string"}}, "required": ["fingerprint", "destination"]}},
    {"name": "evopilot_weekly_report", "description": "Produce a concise evidence-based learning report for the last 1-90 days.", "inputSchema": {"type": "object", "properties": {"days": {"type": "integer", "minimum": 1, "maximum": 90}}}},
    {"name": "evopilot_review_action", "description": "Classify a proposed action. Unknown or dangerous actions require a person.", "inputSchema": {"type": "object", "properties": {"action": {"type": "string"}, "details": {"type": "string"}}, "required": ["action"]}},
    {"name": "evopilot_authorize_once", "description": "After explicit human confirmation, authorize the exact action ID blocked by the safety gate for one use within ten minutes.", "inputSchema": {"type": "object", "properties": {"approval_id": {"type": "string", "pattern": "^[0-9a-f]{24}$"}, "label": {"type": "string"}}, "required": ["approval_id"]}},
    {"name": "evopilot_export", "description": "Export local learning data and audit history to JSON. Stored approvals are excluded.", "inputSchema": {"type": "object", "properties": {"destination": {"type": "string"}}, "required": ["destination"]}},
]


def content(value):
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2)
    return {"content": [{"type": "text", "text": text}]}


def call(name, args):
    if name == "evopilot_observe":
        return content({"id": observe(args["app"], args["action"], args.get("outcome", "unknown"), session_id=args.get("session_id", ""))})
    if name == "evopilot_remember":
        return content(remember(args["key"], args["value"], scope=args.get("scope", "global"), confidence=float(args.get("confidence", 0.6)), source=args.get("source", "explicit")))
    if name == "evopilot_correct_memory":
        return content(correct_memory(args["key"], args["value"], scope=args.get("scope")))
    if name == "evopilot_memory_history":
        return content(memory_history(args.get("key"), int(args.get("limit", 50))))
    if name == "evopilot_forget":
        return content({"forgotten": forget(args["key"])})
    if name == "evopilot_context":
        return content(context(args.get("scope", "global")))
    if name == "evopilot_analyze_habits":
        return content(analyze_habits(int(args.get("min_count", 3))))
    if name == "evopilot_analyze_sequences":
        return content(analyze_sequences(int(args.get("min_count", 3)), int(args.get("max_length", 4))))
    if name == "evopilot_draft_skill":
        return content(draft_skill(args["fingerprint"], Path(args["destination"])))
    if name == "evopilot_weekly_report":
        return content(weekly_report(int(args.get("days", 7))))
    if name == "evopilot_review_action":
        return content(review_action(args["action"], args.get("details", "")))
    if name == "evopilot_authorize_once":
        return content(authorize_once(args["approval_id"], args.get("label", "human-confirmed action")))
    if name == "evopilot_export":
        return content({"path": str(export_data(Path(args["destination"])))})
    raise ValueError(f"Unknown tool: {name}")


def negotiated_protocol_version(message):
    requested = message.get("params", {}).get("protocolVersion")
    return requested if isinstance(requested, str) and requested else FALLBACK_PROTOCOL_VERSION


def respond(message):
    method = message.get("method")
    ident = message.get("id")
    if ident is None:
        return None
    try:
        if method == "initialize":
            result = {
                "protocolVersion": negotiated_protocol_version(message),
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "evopilot", "version": SERVER_VERSION},
                "instructions": "Use only non-sensitive, evidence-backed memory. Call evopilot_authorize_once only after explicit human confirmation of the exact blocked action.",
            }
        elif method == "tools/list":
            result = {"tools": TOOLS}
        elif method == "tools/call":
            result = call(message["params"]["name"], message["params"].get("arguments", {}))
        elif method == "ping":
            result = {}
        else:
            return {"jsonrpc": "2.0", "id": ident, "error": {"code": -32601, "message": "Method not found"}}
        return {"jsonrpc": "2.0", "id": ident, "result": result}
    except Exception as exc:
        return {"jsonrpc": "2.0", "id": ident, "error": {"code": -32000, "message": str(exc)}}


def main():
    for line in sys.stdin:
        try:
            message = json.loads(line)
            output = respond(message)
            if output:
                print(json.dumps(output, ensure_ascii=False), flush=True)
        except Exception as exc:
            print(f"EvoPilot MCP input error ({type(exc).__name__}): {exc}", file=sys.stderr, flush=True)
            print(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}), flush=True)


if __name__ == "__main__":
    main()
