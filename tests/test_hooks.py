import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "evopilot"


class HookTests(unittest.TestCase):
    def test_observe_hook_minimizes_stored_data(self):
        with tempfile.TemporaryDirectory() as temp:
            env = {
                **os.environ,
                "EVOPILOT_DATA": temp,
                "PLUGIN_DATA": temp,
                "PLUGIN_ROOT": str(PLUGIN),
            }
            cwd = "C:/Users/example/Private Client Project"
            event = {
                "cwd": cwd,
                "session_id": "hook-test",
                "tool_name": "mcp__github__search",
                "tool_input": {"query": "private-input-marker"},
                "tool_response": {"isError": False, "text": "private-output-marker"},
            }
            subprocess.run(
                [sys.executable, str(PLUGIN / "hooks" / "observe_tool.py")],
                input=json.dumps(event),
                text=True,
                capture_output=True,
                env=env,
                check=True,
            )
            db = sqlite3.connect(Path(temp) / "evopilot.sqlite3")
            try:
                row = db.execute("SELECT app,action,outcome,metadata_json FROM observations").fetchone()
            finally:
                db.close()

            metadata = json.loads(row[3])
            expected_hash = hashlib.sha256(cwd.casefold().encode()).hexdigest()[:16]
            self.assertEqual(row[:3], ("github", "mcp__github__search", "success"))
            self.assertEqual(metadata, {"workspace_hash": expected_hash})
            serialized = json.dumps(metadata)
            self.assertNotIn(cwd, serialized)
            self.assertNotIn("private-input-marker", serialized)
            self.assertNotIn("private-output-marker", serialized)


if __name__ == "__main__":
    unittest.main()
