#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
root=Path(os.environ.get("PLUGIN_ROOT",Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(root/"scripts"))
from core import context  # noqa:E402
try:
 payload=json.load(sys.stdin);scope=Path(payload.get("cwd","")).name or "global"
 print(json.dumps({"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":context(scope)}}))
except Exception:
 print(json.dumps({"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"EvoPilot memory is unavailable. Continue without it; do not infer missing preferences."}}))
