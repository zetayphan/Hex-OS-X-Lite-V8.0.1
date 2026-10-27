import pathlib,subprocess,sys,time,json,urllib.request,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class ReleaseSmoke(unittest.TestCase):
 def test_files_and_brand(self):
  self.assertEqual((ROOT/'VERSION').read_text().strip(),'8.0.1')
  self.assertIn('HEX OS X LITE 8.0 FINAL',(ROOT/'web/index.html').read_text())
  core=(ROOT/'system/core.py').read_text()
  for name in ('nexus','research','studio','terminal','omniverse'):
   self.assertIn(repr(name)+':',core)
 def test_http(self):
  import socket
  with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
  p=subprocess.Popen([sys.executable,str(ROOT/'launch.py'),'web','--port',str(port)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
  try:
   for _ in range(35):
    try:
     with urllib.request.urlopen(f'http://127.0.0.1:{port}/api/health',timeout=1) as r:data=json.load(r)
     break
    except Exception:time.sleep(.15)
   else:self.fail('Server did not start: '+p.stderr.read().decode()[:500])
   self.assertTrue(data['ok']);self.assertEqual(data['version'],'8.0.1');self.assertEqual(data['modules'],5)
   with urllib.request.urlopen(f'http://127.0.0.1:{port}/',timeout=3) as r:self.assertIn(b'HEX OS X LITE 8.0 FINAL',r.read())
  finally:
   p.terminate()
   try:p.wait(timeout=3)
   except subprocess.TimeoutExpired:p.kill()
if __name__=='__main__':unittest.main()
