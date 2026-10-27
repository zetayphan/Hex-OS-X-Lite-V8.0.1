import unittest,sys,json,threading,urllib.request
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'system'))
from core import Handler,ThreadingHTTPServer
class V29(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
  threading.Thread(target=cls.server.serve_forever,daemon=True).start()
  cls.base='http://127.0.0.1:'+str(cls.server.server_port)
 @classmethod
 def tearDownClass(cls):cls.server.shutdown();cls.server.server_close()
 def get(self,path):return json.load(urllib.request.urlopen(self.base+path))
 def test_version(self):self.assertEqual(self.get('/api/version')['version'],'29.0')
 def test_modules(self):self.assertEqual(len(self.get('/api/modules')['modules']),5)
 def test_quantum(self):
  data=json.dumps({'qubits':2,'gates':[{'gate':'H','target':0},{'gate':'CNOT','target':1,'control':0}]}).encode()
  req=urllib.request.Request(self.base+'/api/quantum/experiment',data=data,headers={'Content-Type':'application/json'})
  p=json.load(urllib.request.urlopen(req))['probabilities']
  self.assertAlmostEqual(p[0],.5);self.assertAlmostEqual(p[3],.5)
if __name__=='__main__':unittest.main()
