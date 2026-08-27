#!/usr/bin/env python3
"""Record tool categories only; never persist raw tool inputs or outputs."""
import json, os, sys
from pathlib import Path
root=Path(os.environ.get("PLUGIN_ROOT",Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(root/"scripts"))
from core import observe  # noqa:E402
try:
 data=json.load(sys.stdin);tool=str(data.get("tool_name","unknown"))
 app=tool.split("__")[1] if tool.startswith("mcp__") and "__" in tool else ("terminal" if tool=="Bash" else "workspace")
 response=data.get("tool_response",{})
 outcome="failure" if isinstance(response,dict) and (response.get("isError") or response.get("exit_code",0) not in (0,None)) else "success"
 observe(app,tool,outcome,session_id=str(data.get("session_id","")),metadata={"cwd":data.get("cwd","")})
except Exception:
 pass
