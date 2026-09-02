#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
root=Path(os.environ.get("PLUGIN_ROOT",Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(root/"scripts"))
from core import startup_context  # noqa:E402
try:
 payload=json.load(sys.stdin);scope=Path(payload.get("cwd") or "").name or "global"
 print(json.dumps({"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":startup_context(scope)}}))
except Exception as exc:
 print(f"EvoPilot SessionStart error ({type(exc).__name__}): {exc}",file=sys.stderr,flush=True)
 print(json.dumps({"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":f"EvoPilot memory is unavailable ({type(exc).__name__}). Continue without it; do not infer missing preferences."}}))
