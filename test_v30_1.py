import unittest,sys,json,threading,urllib.request,urllib.error
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"system"))
import core
class Checks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.server=core.ThreadingHTTPServer(("127.0.0.1",0),core.Handler)
  cls.port=cls.server.server_port
  cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
 @classmethod
 def tearDownClass(cls):cls.server.shutdown();cls.server.server_close()
 def call(self,path,data=None):
  payload=None if data is None else json.dumps(data).encode()
  req=urllib.request.Request(f"http://127.0.0.1:{self.port}{path}",data=payload,headers={"Content-Type":"application/json"} if payload else {})
  with urllib.request.urlopen(req,timeout=8) as r:return json.loads(r.read())
 def test_version(self):self.assertEqual(self.call("/api/version")["version"],"30.1")
 def test_health(self):self.assertTrue(self.call("/api/health")["ok"])
 def test_modules(self):self.assertEqual(len(self.call("/api/modules")["modules"]),5)
 def test_engine_registry(self):self.assertEqual(len(self.call("/api/engines")["actions"]),5)
 def test_quantum(self):
  x=self.call("/api/quantum/experiment",{"qubits":2,"gates":[{"gate":"H","target":0},{"gate":"CNOT","control":0,"target":1}]})
  self.assertAlmostEqual(x["probabilities"][0],.5);self.assertAlmostEqual(x["probabilities"][3],.5)
 def test_studio(self):
  self.assertEqual(self.call("/api/engine",{"module":"studio","action":"project","name":"v30_test.txt","content":"ok"})["saved"],"v30_test.txt")
  (core.WORK/"v30_test.txt").unlink(missing_ok=True)
 def test_research(self):self.assertIn("result",self.call("/api/engine",{"module":"research","action":"metrics","values":[0,255,65535]}))
 def test_omniverse(self):self.assertIn("result",self.call("/api/engine",{"module":"omniverse","action":"state"}))
 def test_nexus(self):self.assertIn("module",self.call("/api/engine",{"module":"nexus","action":"hexlang","source":""}))
 def test_terminal(self):self.assertIn("module",self.call("/api/engine",{"module":"terminal","action":"hexlang","source":""}))
if __name__=="__main__":unittest.main(verbosity=2)
