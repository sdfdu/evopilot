"""Deterministic, privacy-preserving classification of Codex tool events."""
from __future__ import annotations

import re
from typing import Any

READ_VERBS = {"read", "get", "list", "search", "find", "view", "open", "inspect", "status", "weather", "time", "finance"}
WRITE_VERBS = {"create", "update", "delete", "remove", "send", "publish", "post", "put", "share", "install", "uninstall", "archive", "pin", "rename", "move", "handoff"}

SHELL_RULES = [
    ("publish_external", re.compile(r"\b(git\s+push|npm\s+publish|gh\s+release|docker\s+push|twine\s+upload)\b", re.I), "high"),
    ("delete", re.compile(r"(?:^|[;&|]\s*|\s)(rm|remove-item|del|rmdir)\s+", re.I), "high"),
    ("network_write", re.compile(r"\b(curl|wget|invoke-restmethod|invoke-webrequest)\b[^\r\n]*(?:-x\s*(?:post|put|patch|delete)|--request\s+(?:post|put|patch|delete)|-method\s+(?:post|put|patch|delete))", re.I), "high"),
    ("install_system", re.compile(r"\b(apt(?:-get)?|dnf|yum|brew|winget|choco)\s+(?:install|remove|uninstall|upgrade)\b", re.I), "high"),
    ("credentials", re.compile(r"\b(login|credential|private[_ -]?key|api[_ -]?key|access[_ -]?token|password)\b", re.I), "high"),
    ("test", re.compile(r"\b(pytest|unittest|cargo\s+test|go\s+test|npm\s+(?:run\s+)?test|pnpm\s+test|yarn\s+test)\b", re.I), "low"),
    ("build", re.compile(r"\b(npm|pnpm|yarn|cargo|go|dotnet|gradle|mvn)\s+(?:run\s+)?(?:build|check|lint)\b", re.I), "low"),
    ("git_read", re.compile(r"\bgit\s+(?:status|diff|log|show|branch)\b", re.I), "low"),
    ("git_write", re.compile(r"\bgit\s+(?:add|commit|merge|rebase|cherry-pick)\b", re.I), "low"),
    ("inspect", re.compile(r"\b(rg|grep|findstr|get-content|ls|dir|type|head|tail)\b", re.I), "low"),
]


def _command(tool_input: Any) -> str:
    if not isinstance(tool_input, dict):
        return ""
    value = tool_input.get("command", tool_input.get("cmd", ""))
    return value if isinstance(value, str) else ""


def _mcp_verb(tool_name: str) -> str:
    leaf = tool_name.rsplit("__", 1)[-1].lower()
    parts = [part for part in re.split(r"[_-]+", leaf) if part]
    return next((part for part in parts if part in READ_VERBS | WRITE_VERBS), parts[0] if parts else "unknown")


def classify_tool(tool_name: str, tool_input: Any = None) -> dict[str, str]:
    if tool_name == "Bash":
        command = _command(tool_input)
        for action, pattern, risk in SHELL_RULES:
            if pattern.search(command):
                return {"app": "terminal", "action": action, "risk": risk, "reason": f"Shell command classified as {action}."}
        return {"app": "terminal", "action": "shell", "risk": "low", "reason": "No high-risk shell pattern matched."}
    if tool_name == "apply_patch":
        return {"app": "workspace", "action": "edit", "risk": "low", "reason": "Workspace patch; normal filesystem boundaries still apply."}
    if tool_name.startswith("mcp__"):
        parts = tool_name.split("__")
        app = parts[1] if len(parts) > 2 else "mcp"
        if "evopilot" in app or "evopilot" in tool_name:
            return {"app": "evopilot", "action": "internal", "risk": "low", "reason": "EvoPilot's own local control tool."}
        verb = _mcp_verb(tool_name)
        if verb in READ_VERBS:
            return {"app": app, "action": f"mcp_{verb}", "risk": "low", "reason": "Read-only MCP verb."}
        if verb in WRITE_VERBS:
            return {"app": app, "action": f"mcp_{verb}", "risk": "high", "reason": "External or persistent MCP mutation requires confirmation."}
        return {"app": app, "action": "mcp_unknown", "risk": "unknown", "reason": "Unknown MCP behavior fails closed."}
    return {"app": "workspace", "action": tool_name.lower()[:80] or "unknown", "risk": "low", "reason": "Ungated local function; Codex permissions still apply."}
