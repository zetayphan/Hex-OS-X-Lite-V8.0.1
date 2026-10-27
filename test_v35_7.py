"""End-to-end HTTP tests of five native subsystem operations."""
import json, subprocess, sys, time, urllib.request, urllib.error, socket
from pathlib import Path
root=Path(__file__).resolve().parents[1]
s=socket.socket();s.bind(('127.0.0.1',0));port=s.getsockname()[1];s.close()
p=subprocess.Popen([sys.executable,str(root/'system/core.py'),str(port)],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
def get(path):
 with urllib.request.urlopen(f'http://127.0.0.1:{port}{path}',timeout=5) as r:return r.read()
def post(path,payload):
 req=urllib.request.Request(f'http://127.0.0.1:{port}{path}',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=8) as r:return json.load(r)
try:
 for _ in range(80):
  try:get('/api/health');break
  except Exception:time.sleep(.1)
 else:raise RuntimeError('server did not start')
 assert json.loads(get('/api/version'))['version']=='35.7'
 assert json.loads(get('/api/diagnostics'))['version']=='35.7'
 assert b'35.7' in get('/web/index.html')
 assert get('/web/app.js')
 cases=[('nexus',{'source':'print(2+3)'}),('research',{'values':[1,2,3,4]}),('studio',{'name':'v357_smoke.txt','content':'hello from test'}),('terminal',{'source':'let x = 2 + 3'}),('omniverse',{'action':'state'})]
 for module,data in cases:
  response=post('/api/subsystem',{'subsystem':module,'data':data})
  assert response.get('ok') is True,(module,response)
  assert response.get('result') is not None,(module,response)
  print('PASS:',module,'subsystem executed')
 print('PASS: HTTP version, diagnostics, desktop assets, five subsystem operations')
finally:
 p.terminate()
 try:p.wait(timeout=5)
 except subprocess.TimeoutExpired:p.kill();p.wait()
 (root/'workspace'/'v357_smoke.txt').unlink(missing_ok=True)
