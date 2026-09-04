import json, os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class McpTests(unittest.TestCase):
 def test_initialize_and_tools(self):
  with tempfile.TemporaryDirectory() as temp:
   env={**os.environ,"EVOPILOT_DATA":temp,"PLUGIN_ROOT":str(ROOT/"plugins"/"evopilot")}
   requests='\n'.join([json.dumps({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2026-07-28","capabilities":{},"clientInfo":{"name":"test","version":"1"}}}),json.dumps({"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}})])+'\n'
   result=subprocess.run([sys.executable,str(ROOT/"plugins"/"evopilot"/"mcp"/"server.py")],input=requests,text=True,capture_output=True,env=env,check=True)
   lines=[json.loads(x) for x in result.stdout.splitlines()]
   self.assertEqual(lines[0]["result"]["serverInfo"]["name"],"evopilot")
   self.assertEqual(lines[0]["result"]["serverInfo"]["version"],"0.4.0")
   self.assertEqual(lines[0]["result"]["protocolVersion"],"2026-07-28")
   self.assertIn("tools",lines[0]["result"]["capabilities"])
   names={tool["name"] for tool in lines[1]["result"]["tools"]}
   self.assertEqual(len(names),21)
   self.assertIn("evopilot_analyze_sequences",names)
   self.assertIn("evopilot_weekly_report",names)
   self.assertIn("evopilot_authorize_once",names)
   self.assertIn("evopilot_compile_skill",names)
   self.assertIn("evopilot_demo",names)
   self.assertIn("evopilot_quickstart",names)
   self.assertIn("evopilot_forget_all",names)
   self.assertIn("evopilot_doctor",names)
   self.assertIn("evopilot_validate_skill",names)
   self.assertIn("evopilot_prepare_skill_install",names)
   self.assertIn("evopilot_install_skill",names)

 def test_installed_plugin_path_with_spaces_and_unicode(self):
  with tempfile.TemporaryDirectory() as temp:
   installed=Path(temp)/"外掛 With Spaces";data=Path(temp)/"資料 Memory"
   shutil.copytree(ROOT/"plugins"/"evopilot",installed)
   env={**os.environ,"EVOPILOT_DATA":str(data),"PLUGIN_DATA":str(data),"PLUGIN_ROOT":str(installed),"PYTHONUTF8":"1"}
   requests='\n'.join([json.dumps({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25"}}),json.dumps({"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}})])+'\n'
   result=subprocess.run([sys.executable,str(installed/"mcp"/"server.py")],input=requests,text=True,capture_output=True,env=env,check=True)
   lines=[json.loads(x) for x in result.stdout.splitlines()]
   self.assertEqual(lines[0]["result"]["protocolVersion"],"2025-11-25")
   self.assertEqual(len(lines[1]["result"]["tools"]),21)
   self.assertEqual(result.stderr,"")

if __name__=="__main__":unittest.main()
