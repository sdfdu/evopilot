#!/usr/bin/env python3
"""Fail-closed PreToolUse gate with exact, single-use human approvals."""
import json
import os
import sys
from pathlib import Path

root = Path(os.environ.get("PLUGIN_ROOT", Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(root / "scripts"))
from core import approval_fingerprint, audit_gate, consume_approval  # noqa: E402
from signals import classify_tool  # noqa: E402

try:
    event = json.load(sys.stdin)
    tool_name = str(event.get("tool_name", "unknown"))
    tool_input = event.get("tool_input", {})
    signal = classify_tool(tool_name, tool_input)
    if signal["risk"] in {"high", "unknown"}:
        approval_id = approval_fingerprint(tool_name, tool_input)
        if consume_approval(approval_id):
            audit_gate(f"{tool_name}:{signal['action']}", "approved_once", f"Consumed approval {approval_id}.")
        else:
            reason = (
                f"EvoPilot blocked {signal['action']}. {signal['reason']} "
                f"Ask the user to confirm this exact action. After confirmation, call "
                f"evopilot_authorize_once with approval_id {approval_id}, then retry once."
            )
            audit_gate(f"{tool_name}:{signal['action']}", "denied", reason)
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }))
except Exception as exc:
    reason = f"EvoPilot safety gate failed closed ({type(exc).__name__})."
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
