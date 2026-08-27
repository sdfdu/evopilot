#!/usr/bin/env python3
"""Dependency-free stdio MCP server exposing EvoPilot's local tools."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("PLUGIN_ROOT", Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(ROOT / "scripts"))
from core import analyze_habits, context, export_data, forget, observe, remember, review_action  # noqa: E402

SERVER_VERSION = "0.1.2"
FALLBACK_PROTOCOL_VERSION = "2025-06-18"

TOOLS = [
    {"name": "evopilot_observe", "description": "Record a privacy-minimized work observation and outcome for later habit analysis.", "inputSchema": {"type": "object", "properties": {"app": {"type": "string"}, "action": {"type": "string"}, "outcome": {"type": "string", "enum": ["unknown", "success", "failure", "abandoned"]}}, "required": ["app", "action"]}},
    {"name": "evopilot_remember", "description": "Store a non-sensitive user preference, decision, lesson, or friction point in local memory.", "inputSchema": {"type": "object", "properties": {"key": {"type": "string"}, "value": {"type": "string"}, "scope": {"type": "string"}, "confidence": {"type": "number", "minimum": 0, "maximum": 1}}, "required": ["key", "value"]}},
    {"name": "evopilot_forget", "description": "Delete one memory by exact key.", "inputSchema": {"type": "object", "properties": {"key": {"type": "string"}}, "required": ["key"]}},
    {"name": "evopilot_context", "description": "Retrieve concise relevant memories and habits for the current scope.", "inputSchema": {"type": "object", "properties": {"scope": {"type": "string"}}}},
    {"name": "evopilot_analyze_habits", "description": "Detect repeated app and workflow patterns without inventing preferences from a single event.", "inputSchema": {"type": "object", "properties": {"min_count": {"type": "integer", "minimum": 2, "maximum": 20}}}},
    {"name": "evopilot_review_action", "description": "Apply the local HITL policy before a proposed action. Unknown or dangerous actions fail closed.", "inputSchema": {"type": "object", "properties": {"action": {"type": "string"}, "details": {"type": "string"}}, "required": ["action"]}},
    {"name": "evopilot_export", "description": "Export memories, workflows, and observations to a local JSON backup. Secrets are never intentionally stored.", "inputSchema": {"type": "object", "properties": {"destination": {"type": "string"}}, "required": ["destination"]}},
]


def content(value):
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2)
    return {"content": [{"type": "text", "text": text}]}


def call(name, args):
    if name == "evopilot_observe":
        return content({"id": observe(args["app"], args["action"], args.get("outcome", "unknown"))})
    if name == "evopilot_remember":
        return content(remember(args["key"], args["value"], scope=args.get("scope", "global"), confidence=float(args.get("confidence", 0.6))))
    if name == "evopilot_forget":
        return content({"forgotten": forget(args["key"])})
    if name == "evopilot_context":
        return content(context(args.get("scope", "global")))
    if name == "evopilot_analyze_habits":
        return content(analyze_habits(int(args.get("min_count", 3))))
    if name == "evopilot_review_action":
        return content(review_action(args["action"], args.get("details", "")))
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
                "instructions": "Use EvoPilot memory only for non-sensitive, evidence-backed preferences and habits.",
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
