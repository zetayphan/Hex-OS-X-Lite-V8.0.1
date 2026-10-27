import subprocess,sys,time,json,urllib.request,socket
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sock=socket.socket();sock.bind(('127.0.0.1',0));port=sock.getsockname()[1];sock.close()
proc=subprocess.Popen([sys.executable,str(root/'system/core.py'),str(port)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
base=f'http://127.0.0.1:{port}'
try:
 for _ in range(50):
  try:
   with urllib.request.urlopen(base+'/api/health',timeout=.5) as r: health=json.load(r);break
  except Exception:time.sleep(.1)
 else:raise AssertionError('server failed to start')
 assert health['ok'] and health['version']=='28.0'
 with urllib.request.urlopen(base+'/api/modules') as r:mods=json.load(r)
 assert len(mods['modules'])==5 and all(x['installed'] for x in mods['modules'])
 data=json.dumps({'message':'status'}).encode()
 req=urllib.request.Request(base+'/api/ai',data=data,headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req) as r: ai=json.load(r)
 assert ai['model_connected'] is False
 with urllib.request.urlopen(base+'/web/') as r:assert r.status==200
 print('PASS: desktop, five modules, health and offline AI')
finally:
 proc.terminate();proc.wait(timeout=5)
