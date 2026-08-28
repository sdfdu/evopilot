#!/usr/bin/env python3
"""Record classified tool signals; never persist raw inputs, outputs, or paths."""
import hashlib
import json
import os
import sys
from pathlib import Path

root = Path(os.environ.get("PLUGIN_ROOT", Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(root / "scripts"))
from core import observe  # noqa: E402
from signals import classify_tool  # noqa: E402

try:
    data = json.load(sys.stdin)
    tool = str(data.get("tool_name", "unknown"))
    signal = classify_tool(tool, data.get("tool_input"))
    response = data.get("tool_response", {})
    outcome = "failure" if isinstance(response, dict) and (response.get("isError") or response.get("exit_code", 0) not in (0, None)) else "success"
    cwd = str(data.get("cwd") or "").replace("\\", "/").rstrip("/").casefold()
    metadata = {"workspace_hash": hashlib.sha256(cwd.encode()).hexdigest()[:16], "tool_family": tool.split("__", 1)[0]} if cwd else {"tool_family": tool.split("__", 1)[0]}
    observe(signal["app"], signal["action"], outcome, session_id=str(data.get("session_id", "")), metadata=metadata)
except Exception:
    pass
