import os, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0,str(ROOT/"plugins"/"evopilot"/"scripts"))
from core import analyze_habits, context, forget, observe, remember, review_action

class EvoPilotTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();os.environ["EVOPILOT_DATA"]=self.temp.name
 def tearDown(self):
  self.temp.cleanup();os.environ.pop("EVOPILOT_DATA",None)
 def test_memory_strengthens_with_evidence(self):
  first=remember("format","conclusion first",confidence=.6)
  second=remember("format","conclusion first",confidence=.6)
  self.assertEqual(first["evidence_count"],1);self.assertEqual(second["evidence_count"],2);self.assertGreater(second["confidence"],first["confidence"])
  self.assertIn("conclusion first",context())
 def test_secrets_are_rejected(self):
  with self.assertRaises(ValueError):remember("api_key","abc123")
 def test_habit_requires_repetition(self):
  for _ in range(2):observe("vscode","run tests","success")
  self.assertEqual(analyze_habits(3),[])
  observe("vscode","run tests","success")
  self.assertEqual(analyze_habits(3)[0]["evidence"],3)
 def test_dangerous_and_unknown_actions_require_human(self):
  self.assertEqual(review_action("publish")["decision"],"human_required")
  self.assertEqual(review_action("mystery-action")["decision"],"human_required")
  self.assertEqual(review_action("run_tests")["decision"],"allow")
 def test_forget_is_explicit(self):
  remember("tone","direct");self.assertTrue(forget("tone"));self.assertFalse(forget("tone"))

if __name__=="__main__":unittest.main()

