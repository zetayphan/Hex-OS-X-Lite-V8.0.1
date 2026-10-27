import subprocess,time,urllib.request,urllib.error,json,socket,sys,os
from pathlib import Path
root=Path(__file__).resolve().parents[1]
s=socket.socket();s.bind(('127.0.0.1',0));port=s.getsockname()[1];s.close()
p=subprocess.Popen([sys.executable,str(root/'system/core.py'),str(port)],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,env={**os.environ,'PYTHONPATH':str(root)})
try:
 base=f'http://127.0.0.1:{port}'
 for _ in range(80):
  try:urllib.request.urlopen(base+'/api/health',timeout=1);break
  except Exception:time.sleep(.1)
 else:raise AssertionError('server startup failed')
 for route in ('/api/health','/api/version','/api/diagnostics','/api/subsystems','/api/v40/services','/api/v41/security','/web/index.html','/web/app.js'):
  with urllib.request.urlopen(base+route,timeout=3) as r:
   assert r.status==200,route
   assert r.headers.get('X-Content-Type-Options')=='nosniff',route
  print('PASS',route)
 assert json.load(urllib.request.urlopen(base+'/api/version'))['version']=='43.0'
 assert json.load(urllib.request.urlopen(base+'/api/health'))['version']=='43.0'
 for route in ('/system/core.py','/workspace/state.json','/VERSION'):
  try:urllib.request.urlopen(base+route,timeout=3);raise AssertionError('exposed '+route)
  except urllib.error.HTTPError as e:assert e.code==403,(route,e.code)
 print('V43 HTTP regression checks passed')
finally:
 p.terminate();p.wait(timeout=5)
