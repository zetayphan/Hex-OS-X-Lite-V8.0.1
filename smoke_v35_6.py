import json, subprocess, sys, time, urllib.request, socket
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sock=socket.socket();sock.bind(('127.0.0.1',0));port=sock.getsockname()[1];sock.close()
p=subprocess.Popen([sys.executable,str(root/'system/core.py'),str(port)],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
try:
 for _ in range(60):
  try:
   urllib.request.urlopen(f'http://127.0.0.1:{port}/api/health',timeout=1);break
  except Exception:time.sleep(.1)
 for endpoint in ('/api/health','/api/version','/api/subsystems','/api/diagnostics','/web/','/web/app.js'):
  with urllib.request.urlopen(f'http://127.0.0.1:{port}{endpoint}',timeout=4) as r:
   data=r.read();assert r.status==200 and data,endpoint
   if endpoint=='/api/diagnostics':assert json.loads(data)['version']=='35.6'
 print('PASS: 6 HTTP routes including subsystem discovery and diagnostics')
finally:
 p.terminate();p.wait(timeout=5)
