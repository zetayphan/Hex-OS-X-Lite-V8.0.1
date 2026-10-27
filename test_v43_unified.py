"""V43 unified local HTTP integration checks. Run: python tests/test_v43_unified.py"""
import json,subprocess,sys,time,urllib.request,urllib.error,socket
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
with socket.socket() as s:
 s.bind(('127.0.0.1',0)); port=s.getsockname()[1]
proc=subprocess.Popen([sys.executable,str(ROOT/'system/core.py'),str(port)],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
base=f'http://127.0.0.1:{port}'
def req(path,payload=None):
 data=None if payload is None else json.dumps(payload).encode()
 request=urllib.request.Request(base+path,data=data,headers={'Content-Type':'application/json'} if data else {})
 try:
  with urllib.request.urlopen(request,timeout=4) as r:return r.status,r.read(),dict(r.headers)
 except urllib.error.HTTPError as e:return e.code,e.read(),dict(e.headers)
checks=[]
def check(name,ok):
 checks.append((name,bool(ok)));print(('PASS' if ok else 'FAIL')+' '+name)
try:
 for _ in range(50):
  if proc.poll() is not None:raise RuntimeError('server exited')
  try:req('/api/health');break
  except Exception:time.sleep(.1)
 status,body,h=req('/');check('desktop root serves HTML',status==200 and b'<html' in body.lower())
 status,body,h=req('/web/');check('desktop web route',status==200 and b'<html' in body.lower())
 status,body,h=req('/api/version');check('V43 version',status==200 and json.loads(body)['version']=='43.0')
 status,body,h=req('/api/modules');check('five registered modules',status==200 and len(json.loads(body)['modules'])==5)
 status,body,h=req('/system/core.py');check('private source denied',status in (403,404))
 status,body,h=req('/api/engine',{'module':'nexus','action':'v38_execute','source':'2+3'});check('Nexus engine',status==200)
 status,body,h=req('/api/engine',{'module':'research','action':'statistics','values':[1,2,3]});check('Research statistics',status==200 and json.loads(body)['result']['mean']==2)
 status,body,h=req('/api/engine',{'module':'studio','action':'project','name':'v43_test.hex','content':'hello'});check('Studio save',status==200)
 status,body,h=req('/api/engine',{'module':'studio','action':'read','name':'v43_test.hex'});check('Studio read',status==200 and json.loads(body)['content']=='hello')
 status,body,h=req('/api/engine',{'module':'terminal','action':'v38_script','source':'x = 2 + 3'});check('Terminal engine',status==200)
 status,body,h=req('/api/engine',{'module':'omniverse','action':'v38_simulate','steps':1});check('Omniverse engine',status==200)
 finally_path=ROOT/'workspace/v43_test.hex'
 if finally_path.exists():finally_path.unlink()
finally:
 proc.terminate()
 try:proc.communicate(timeout=3)
 except subprocess.TimeoutExpired:proc.kill();proc.communicate()
print(f'{sum(ok for _,ok in checks)}/{len(checks)} passed')
sys.exit(0 if all(ok for _,ok in checks) else 1)
