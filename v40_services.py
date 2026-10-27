"""HEX OS V40 read-only local service layer (standard library only)."""
from pathlib import Path
import os, json, time, threading, shutil, datetime
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'workspace'
START=time.monotonic()
LOCK=threading.RLock()
LOG=WORK/'v40_events.jsonl'
REGISTRY={
 'nexus':{'name':'HEX Nexus X','status':'registered'},
 'research':{'name':'Unified Research Lab','status':'registered'},
 'studio':{'name':'HEX Studio Pro','status':'registered'},
 'terminal':{'name':'HEX Terminal Pro','status':'registered'},
 'omniverse':{'name':'HEX Omniverse X','status':'registered'},
}
def snapshot():
 return {'version':'40.0','uptime_seconds':round(time.monotonic()-START,2),'services':REGISTRY,'service_count':len(REGISTRY)}
def permissions():
 return {'mode':'local-only','bind':'127.0.0.1','capabilities':{'workspace':'read-write via validated API','host_shell':'not granted by v40 services','external_network':'not granted by v40 services'},'note':'This is an informational capability manifest, not a complete security sandbox.'}
def resources():
 usage=shutil.disk_usage(WORK)
 return {'disk':{'total':usage.total,'used':usage.used,'free':usage.free},'workspace_files':sum(1 for p in WORK.iterdir() if p.is_file()),'uptime_seconds':round(time.monotonic()-START,2)}
def record(event,details=None):
 WORK.mkdir(exist_ok=True)
 entry={'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'event':str(event)[:80],'details':details or {}}
 with LOCK:
  with LOG.open('a',encoding='utf-8') as f:f.write(json.dumps(entry)+'\n')
 return entry
def events(limit=50):
 if not LOG.exists():return {'events':[]}
 with LOCK:
  lines=LOG.read_text(encoding='utf-8').splitlines()[-limit:]
 result=[]
 for line in lines:
  try:result.append(json.loads(line))
  except json.JSONDecodeError:continue
 return {'events':result}
