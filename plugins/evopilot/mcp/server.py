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
    analyze_sequences, authorize_once, context, correct_memory,
    compile_skill, doctor, forget,
    install_skill, observe, observe_episode, prepare_skill_install, promote_policy, remember,
    retire_policy, review_action, runtime_context, validate_skill_bundle, weekly_report,
)

SERVER_VERSION = "0.6.0"
FALLBACK_PROTOCOL_VERSION = "2025-06-18"

TOOLS = [
    {"name": "evopilot_observe", "description": "Record a privacy-minimized work observation and outcome for later workflow analysis.", "inputSchema": {"type": "object", "properties": {"app": {"type": "string"}, "action": {"type": "string"}, "outcome": {"type": "string", "enum": ["unknown", "success", "failure", "abandoned"]}, "session_id": {"type": "string"}}, "required": ["app", "action"]}},
    {"name": "evopilot_remember", "description": "Store a non-sensitive explicit or inferred preference. Inferences never silently replace conflicting values.", "inputSchema": {"type": "object", "properties": {"key": {"type": "string"}, "value": {"type": "string"}, "scope": {"type": "string"}, "confidence": {"type": "number", "minimum": 0, "maximum": 1}, "source": {"type": "string", "enum": ["explicit", "inferred"]}}, "required": ["key", "value"]}},
    {"name": "evopilot_correct_memory", "description": "Explicitly correct a memory while preserving its history.", "inputSchema": {"type": "object", "properties": {"key": {"type": "string"}, "value": {"type": "string"}, "scope": {"type": "string"}}, "required": ["key", "value"]}},
    {"name": "evopilot_forget", "description": "Delete one memory by exact key while retaining a deletion audit event.", "inputSchema": {"type": "object", "properties": {"key": {"type": "string"}}, "required": ["key"]}},
    {"name": "evopilot_context", "description": "Retrieve concise relevant memories and learned workflows for the current scope.", "inputSchema": {"type": "object", "properties": {"scope": {"type": "string"}}}},
    {"name": "evopilot_analyze_sequences", "description": "Detect repeated two-to-four-step workflows and measure their outcomes.", "inputSchema": {"type": "object", "properties": {"min_count": {"type": "integer", "minimum": 2, "maximum": 20}, "max_length": {"type": "integer", "minimum": 2, "maximum": 6}}}},
    {"name": "evopilot_observe_episode", "description": "Record one privacy-minimized behavior-cloning episode as structured steps, validation, and outcome.", "inputSchema": {"type": "object", "properties": {"task_type": {"type": "string"}, "steps": {"type": "array", "items": {"type": "string"}, "minItems": 2}, "outcome": {"type": "string", "enum": ["success", "failure", "abandoned", "corrected"]}, "validation_steps": {"type": "array", "items": {"type": "string"}}, "decision_points": {"type": "array", "items": {"type": "string"}}, "risk_level": {"type": "string", "enum": ["low", "medium", "high", "unknown"]}}, "required": ["task_type", "steps"]}},
    {"name": "evopilot_promote_policy", "description": "Promote a qualified behavior workflow into a short reviewed policy card for token-capped runtime retrieval.", "inputSchema": {"type": "object", "properties": {"fingerprint": {"type": "string"}}, "required": ["fingerprint"]}},
    {"name": "evopilot_retire_policy", "description": "Retire a behavior policy so it is no longer returned in runtime context.", "inputSchema": {"type": "object", "properties": {"fingerprint": {"type": "string"}}, "required": ["fingerprint"]}},
    {"name": "evopilot_runtime_context", "description": "Return a deterministic, token-capped behavior policy context for a task type without replaying episodes.", "inputSchema": {"type": "object", "properties": {"task_type": {"type": "string"}, "token_budget": {"type": "integer", "minimum": 40, "maximum": 1000}}, "required": ["task_type"]}},
    {"name": "evopilot_compile_skill", "description": "Compile an evidence-backed workflow into a portable Open Agent Skills bundle for validation and review.", "inputSchema": {"type": "object", "properties": {"fingerprint": {"type": "string"}, "destination": {"type": "string"}}, "required": ["fingerprint", "destination"]}},
    {"name": "evopilot_doctor", "description": "Check the local runtime, required plugin files, and database health without returning stored memory content.", "inputSchema": {"type": "object", "properties": {"plugin_root": {"type": "string"}}}},
    {"name": "evopilot_validate_skill", "description": "Structurally validate and score a compiled Skill bundle without executing or installing it.", "inputSchema": {"type": "object", "properties": {"bundle": {"type": "string"}}, "required": ["bundle"]}},
    {"name": "evopilot_prepare_skill_install", "description": "Validate a generated Skill and return its evidence plus the exact one-time approval ID required for installation.", "inputSchema": {"type": "object", "properties": {"bundle": {"type": "string"}, "destination": {"type": "string"}}, "required": ["bundle"]}},
    {"name": "evopilot_install_skill", "description": "Install one reviewed Skill bundle after explicit user confirmation and exact one-time approval.", "inputSchema": {"type": "object", "properties": {"bundle": {"type": "string"}, "approval_id": {"type": "string", "pattern": "^[0-9a-f]{24}$"}, "destination": {"type": "string"}}, "required": ["bundle", "approval_id"]}},
    {"name": "evopilot_weekly_report", "description": "Produce a concise evidence-based learning report for the last 1-90 days.", "inputSchema": {"type": "object", "properties": {"days": {"type": "integer", "minimum": 1, "maximum": 90}}}},
    {"name": "evopilot_review_action", "description": "Classify a proposed action. Unknown or dangerous actions require a person.", "inputSchema": {"type": "object", "properties": {"action": {"type": "string"}, "details": {"type": "string"}}, "required": ["action"]}},
    {"name": "evopilot_authorize_once", "description": "After explicit human confirmation, authorize the exact action ID blocked by the safety gate for one use within ten minutes.", "inputSchema": {"type": "object", "properties": {"approval_id": {"type": "string", "pattern": "^[0-9a-f]{24}$"}, "label": {"type": "string"}}, "required": ["approval_id"]}},
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
    if name == "evopilot_forget":
        return content({"forgotten": forget(args["key"])})
    if name == "evopilot_context":
        return content(context(args.get("scope", "global")))
    if name == "evopilot_analyze_sequences":
        return content(analyze_sequences(int(args.get("min_count", 3)), int(args.get("max_length", 4))))
    if name == "evopilot_observe_episode":
        return content(observe_episode(args["task_type"], list(args["steps"]), args.get("outcome", "success"), validation_steps=args.get("validation_steps", []), decision_points=args.get("decision_points", []), risk_level=args.get("risk_level", "low")))
    if name == "evopilot_promote_policy":
        return content(promote_policy(args["fingerprint"]))
    if name == "evopilot_retire_policy":
        return content(retire_policy(args["fingerprint"]))
    if name == "evopilot_runtime_context":
        return content(runtime_context(args["task_type"], int(args.get("token_budget", 250))))
    if name == "evopilot_compile_skill":
        return content(compile_skill(args["fingerprint"], Path(args["destination"])))
    if name == "evopilot_doctor":
        return content(doctor(Path(args["plugin_root"]) if args.get("plugin_root") else None))
    if name == "evopilot_validate_skill":
        return content(validate_skill_bundle(Path(args["bundle"])))
    if name == "evopilot_prepare_skill_install":
        return content(prepare_skill_install(Path(args["bundle"]), Path(args["destination"]) if args.get("destination") else None))
    if name == "evopilot_install_skill":
        return content(install_skill(Path(args["bundle"]), args["approval_id"], Path(args["destination"]) if args.get("destination") else None))
    if name == "evopilot_weekly_report":
        return content(weekly_report(int(args.get("days", 7))))
    if name == "evopilot_review_action":
        return content(review_action(args["action"], args.get("details", "")))
    if name == "evopilot_authorize_once":
        return content(authorize_once(args["approval_id"], args.get("label", "human-confirmed action")))
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
