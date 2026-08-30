import os, sqlite3, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0,str(ROOT/"plugins"/"evopilot"/"scripts"))
from core import analyze_habits, analyze_sequences, compile_skill, connect, context, demo, doctor, draft_skill, forget, memories, memory_history, observe, remember, review_action, validate_skill_bundle, weekly_report

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
  with self.assertRaises(ValueError):remember("auth_header","Bearer example-value")
  with self.assertRaises(ValueError):remember("login","passcode: 123456")
 def test_habit_requires_repetition(self):
  for _ in range(2):observe("vscode","run tests","success")
  self.assertEqual(analyze_habits(3),[])
  observe("vscode","run tests","success")
  self.assertEqual(analyze_habits(3)[0]["evidence"],3)
 def test_dangerous_and_unknown_actions_require_human(self):
  self.assertEqual(review_action("publish")["decision"],"human_required")
  self.assertEqual(review_action("mystery-action")["decision"],"human_required")
  self.assertEqual(review_action("run_tests")["decision"],"allow")
  self.assertEqual(review_action("write_workspace","then publish externally")["decision"],"human_required")
  self.assertEqual(review_action("read","open the password file")["decision"],"human_required")
 def test_forget_is_explicit(self):
  remember("tone","direct");self.assertTrue(forget("tone"));self.assertFalse(forget("tone"))
  self.assertEqual(memory_history("tone")[0]["event"],"forgotten")

 def test_inference_cannot_overwrite_explicit_memory(self):
  remember("tone","direct",source="explicit")
  result=remember("tone","cheerful",source="inferred")
  self.assertFalse(result["stored_value_changed"])
  self.assertEqual(memories()[0]["value"],"direct")
  self.assertEqual(memory_history("tone")[0]["event"],"conflict")

 def test_sequence_promotion_and_skill_draft(self):
  for index in range(5):
   session=f"task-{index}"
   observe("workspace","inspect","success",session_id=session)
   observe("workspace","edit","success",session_id=session)
   observe("terminal","test","success",session_id=session)
  sequences=analyze_sequences(3,4)
  workflow=next(item for item in sequences if item["steps"]==["workspace:inspect","workspace:edit","terminal:test"])
  self.assertEqual(workflow["status"],"draft_ready")
  with tempfile.TemporaryDirectory() as drafts:
   result=draft_skill(workflow["fingerprint"],Path(drafts))
   text=Path(result["path"]).read_text(encoding="utf-8")
   evidence=Path(result["evidence_path"]).read_text(encoding="utf-8")
   self.assertFalse(result["installed"])
   self.assertEqual(result["format"],"open-agent-skills")
   self.assertTrue(result["validation"]["valid"])
   self.assertEqual(result["validation"]["score"],100)
   self.assertEqual(result["validation"]["recommendation"],"ready_for_human_review")
   self.assertIn("human approval",text)
   self.assertIn('"observations": 5',evidence)

 def test_compile_alias_demo_and_doctor(self):
  for index in range(5):
   observe("workspace","inspect","success",session_id=f"compile-{index}")
   observe("terminal","test","success",session_id=f"compile-{index}")
  workflow=analyze_sequences(3,2)[0]
  with tempfile.TemporaryDirectory() as output:
   compiled=compile_skill(workflow["fingerprint"],Path(output))
   self.assertTrue(Path(compiled["bundle"]).is_dir())
  db=connect();before=db.execute("SELECT COUNT(*) FROM observations").fetchone()[0];db.close()
  result=demo()
  db=connect();after=db.execute("SELECT COUNT(*) FROM observations").fetchone()[0];db.close()
  self.assertTrue(result["simulated"])
  self.assertFalse(result["user_data_changed"])
  self.assertEqual(before,after)
  diagnosis=doctor(ROOT/"plugins"/"evopilot")
  self.assertTrue(diagnosis["ok"])

 def test_bundle_validation_rejects_tampered_evidence(self):
  with tempfile.TemporaryDirectory() as output:
   artifact=demo(Path(output))["artifact"]
   bundle=Path(artifact["bundle"])
   self.assertEqual(validate_skill_bundle(bundle)["recommendation"],"demo_only")
   evidence_path=bundle/"evopilot.json"
   evidence=evidence_path.read_text(encoding="utf-8").replace('"successful_outcomes": 4','"successful_outcomes": 9')
   evidence_path.write_text(evidence,encoding="utf-8")
   validation=validate_skill_bundle(bundle)
   self.assertFalse(validation["valid"])
   self.assertLess(validation["score"],100)
   self.assertEqual(validation["recommendation"],"needs_revision")

 def test_skill_draft_rejects_weak_evidence(self):
  for index in range(3):
   observe("workspace","inspect","success",session_id=f"weak-{index}")
   observe("terminal","test","success",session_id=f"weak-{index}")
  workflow=analyze_sequences(3,2)[0]
  with tempfile.TemporaryDirectory() as drafts:
   with self.assertRaises(ValueError):draft_skill(workflow["fingerprint"],Path(drafts))

 def test_weekly_report_is_evidence_based(self):
  observe("terminal","test","success",session_id="report")
  observe("terminal","test","failure",session_id="report")
  report=weekly_report(7)
  self.assertIn("Observations: 2",report)
  self.assertIn("50% successful",report)

 def test_v1_database_migrates_without_data_loss(self):
  path=Path(self.temp.name)/"evopilot.sqlite3"
  db=sqlite3.connect(path)
  db.execute("CREATE TABLE memories(key TEXT PRIMARY KEY,value TEXT NOT NULL,confidence REAL NOT NULL,evidence_count INTEGER NOT NULL,scope TEXT NOT NULL,risk TEXT NOT NULL,created_at TEXT NOT NULL,updated_at TEXT NOT NULL)")
  db.execute("INSERT INTO memories VALUES('format','concise',0.7,2,'global','low','2026-01-01T00:00:00+00:00','2026-01-01T00:00:00+00:00')")
  db.commit();db.close()
  migrated=connect();migrated.close()
  item=memories()[0]
  self.assertEqual(item["value"],"concise")
  self.assertEqual(item["source"],"explicit")

if __name__=="__main__":unittest.main()
