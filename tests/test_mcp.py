import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class McpTests(unittest.TestCase):
 def test_initialize_and_tools(self):
  with tempfile.TemporaryDirectory() as temp:
   env={**os.environ,"EVOPILOT_DATA":temp,"PLUGIN_ROOT":str(ROOT/"plugins"/"evopilot")}
   requests='\n'.join([json.dumps({"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}),json.dumps({"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}})])+'\n'
   result=subprocess.run([sys.executable,str(ROOT/"plugins"/"evopilot"/"mcp"/"server.py")],input=requests,text=True,capture_output=True,env=env,check=True)
   lines=[json.loads(x) for x in result.stdout.splitlines()]
   self.assertEqual(lines[0]["result"]["serverInfo"]["name"],"evopilot")
   self.assertGreaterEqual(len(lines[1]["result"]["tools"]),7)

if __name__=="__main__":unittest.main()
