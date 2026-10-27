import subprocess,time,urllib.request,urllib.error,json,socket,sys,os
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sock=socket.socket();sock.bind(('127.0.0.1',0));port=sock.getsockname()[1];sock.close()
p=subprocess.Popen([sys.executable,str(root/'system/core.py'),str(port)],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,env={**os.environ,"PYTHONPATH":str(root)})
try:
 base=f'http://127.0.0.1:{port}'
 for _ in range(60):
  try:urllib.request.urlopen(base+'/api/health',timeout=1);break
  except Exception:time.sleep(.1)
 else:raise AssertionError('server did not start')
 for route in ('/api/health','/api/version','/api/v40/services','/api/v41/security','/web/index.html'):
  start=time.perf_counter()
  with urllib.request.urlopen(base+route,timeout=3) as r:
   assert r.status==200,(route,r.status)
   assert r.headers.get('X-Content-Type-Options')=='nosniff'
  print(route,round((time.perf_counter()-start)*1000,2),'ms')
 for route in ('/system/core.py','/workspace/state.json','/tests/test_v41.py','/VERSION'):
  try:urllib.request.urlopen(base+route,timeout=3);raise AssertionError('exposed '+route)
  except urllib.error.HTTPError as e:assert e.code==403,(route,e.code)
 assert json.load(urllib.request.urlopen(base+'/api/version'))['version']=='41.0'
 print('V41 security and HTTP smoke tests passed')
finally:p.terminate();p.wait(timeout=5)
