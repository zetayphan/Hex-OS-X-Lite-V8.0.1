import math
#!/usr/bin/env python3
"""HEX OS shared local service: module discovery, shared workspace, static desktop."""
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from urllib.parse import urlsplit,parse_qs
from pathlib import Path
import json,os,mimetypes,socket,datetime,ast,operator,sys,importlib.util,threading,statistics,math,contextlib,io
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
WORK=ROOT/'workspace'; WORK.mkdir(exist_ok=True)
SYNC={'revision':0,'events':[]}; SYNC_LOCK=threading.RLock()
MODULES={'nexus':'HEX Nexus X','research':'Unified Research Lab','studio':'HEX Studio Pro','terminal':'HEX Terminal Pro','omniverse':'HEX Omniverse X'}

# V30: import original module implementations into the OS process (no extra servers).
_ENGINE_CACHE={}
_ENGINE_LOCK=threading.RLock()
def load_original(module,filename):
 key=(module,filename)
 if key not in _ENGINE_CACHE:
  source=ROOT/'modules'/module/filename
  if not source.is_file():
   # Materialize the bundled source fabric only when a legacy engine is requested.
   raise RuntimeError(f'Legacy {module}/{filename} engine unavailable: source fabric removed in experimental build')
  spec=importlib.util.spec_from_file_location('hex_v30_'+module+'_'+filename.replace('.','_'),source)
  obj=importlib.util.module_from_spec(spec)
  # Omniverse original code uses sibling imports; only local bundled directory is added.
  folder=str(source.parent)
  with _ENGINE_LOCK:
   sys.path.insert(0,folder)
   try:spec.loader.exec_module(obj)
   finally:sys.path.remove(folder)
  _ENGINE_CACHE[key]=obj
 return _ENGINE_CACHE[key]
def engine_call(data):
 module=data.get('module');action=data.get('action')
 if action in ('v38_execute','v38_analyze','v38_project','v38_script','v38_simulate'):
  from system.v38_features import execute
  return execute(module,action,data,WORK)
 if module=='nexus' and action=='hexlang':
  source=data.get('source','')
  if not isinstance(source,str) or len(source)>4000:raise ValueError('invalid source')
  engine=load_original('nexus','hexlang.py')
  # Source is executed by the bundled HexLang interpreter, not Python eval.
  output=io.StringIO()
  with contextlib.redirect_stdout(output): result=engine.HexLang(source).run()
  return {'module':module,'engine':'original Nexus HexLang','result':str(result)[:4000],'output':output.getvalue()[:4000]}
 if module=='research' and action=='metrics':
  values=data.get('values',[])
  if not isinstance(values,list) or len(values)>10000 or any(type(v)!=int or v<0 or v>0xffffff for v in values):raise ValueError('values must be RGB integers')
  engine=load_original('research','research_metrics.py')
  return {'module':module,'engine':'original research_metrics.summarize_state','result':engine.summarize_state({'values':values,'tick':0})}
 if module=='omniverse' and action in ('state','step','reset'):
  with _ENGINE_LOCK:
   engine=load_original('omniverse','app.py')
   if 'omniverse_kernel' not in _ENGINE_CACHE:_ENGINE_CACHE['omniverse_kernel']=engine.Kernel()
   kernel=_ENGINE_CACHE['omniverse_kernel']
   if action=='reset':kernel.reset()
   if action=='step':
    steps=data.get('steps',1)
    if type(steps)!=int or not 1<=steps<=5:raise ValueError('steps 1-5')
    for _ in range(steps):kernel.step()
   state=kernel.state()
   return {'module':module,'engine':'original Omniverse Kernel','result':state}
 if module=='studio' and action=='list':
  return {'module':module,'engine':'HEX OS native studio','projects':[{'name':p.name,'bytes':p.stat().st_size} for p in WORK.iterdir() if p.is_file() and p.suffix in ('.txt','.hex','.json','.md','.py')][:200]}
 if module=='studio' and action=='read':
  name=data.get('name','')
  if not safe(name):raise ValueError('invalid project name')
  target=WORK/name
  if not target.is_file():raise ValueError('project not found')
  if target.stat().st_size>200000:raise ValueError('project too large')
  return {'module':module,'engine':'HEX OS native studio','name':name,'content':target.read_text(encoding='utf-8')}
 if module=='research' and action=='statistics':
  values=data.get('values',[])
  if not isinstance(values,list) or len(values)>10000 or any(type(x) not in (int,float) or not math.isfinite(x) for x in values):raise ValueError('values must be finite numbers')
  return {'module':module,'engine':'HEX OS native statistics','result':{'count':len(values),'mean':statistics.mean(values) if values else None,'median':statistics.median(values) if values else None,'min':min(values) if values else None,'max':max(values) if values else None,'stdev':statistics.stdev(values) if len(values)>1 else None}}
 if module=='studio' and action=='project':
  name=data.get('name','project.txt');content=data.get('content','')
  if not safe(name) or not isinstance(content,str) or len(content)>200000:raise ValueError('invalid project')
  (WORK/name).write_text(content)
  return {'module':module,'engine':'OS Studio project workspace','saved':name}
 if module=='terminal' and action=='hexlang':
  source=data.get('source','')
  if not isinstance(source,str) or len(source)>4000:raise ValueError('invalid source')
  # Terminal's original HexLang interpreter requires a shell adapter; use its parser with restricted shell.
  engine=load_original('terminal','hexlang.py')
  class Shell:
   def safe(self,*args,**kwargs):raise ValueError('native shell API unavailable in embedded mode')
   def __getattr__(self,name):raise ValueError('native shell command unavailable: '+name)
  interpreter=engine.Interpreter(Shell())
  return {'module':module,'engine':'original Terminal HexLang','result':str(interpreter.execute(source))[:4000]}
 raise ValueError('unsupported module action')


def full_workflow(data):
 """Coordinate original module adapters and persist a reproducible report."""
 steps=[]
 def run(label,payload):
  try:
   value=engine_call(payload)
   steps.append({'step':label,'status':'ok','data':value})
   return value
  except Exception as exc:
   steps.append({'step':label,'status':'error','error':str(exc)[:300]})
   return None
 experiment={'qubits':2,'gates':['H(0)','CNOT(0,1)'],'probabilities':[0.5,0,0,0.5]}
 run('nexus',{'module':'nexus','action':'hexlang','source':data.get('nexus_source','print(2+3)')})
 run('terminal',{'module':'terminal','action':'hexlang','source':data.get('terminal_source','let x = 2 + 3')})
 research=run('research',{'module':'research','action':'metrics','values':[round(x*0xffffff) for x in experiment['probabilities']]})
 omni=run('omniverse',{'module':'omniverse','action':'state'})
 record={'version':'46.0','workflow':'five-core','timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'quantum':experiment,'steps':steps}
 filename='five_core_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json'
 # Studio adapter writes the same record as an editable project in the shared workspace.
 run('studio',{'module':'studio','action':'project','name':filename,'content':json.dumps(record,indent=2,default=str)})
 record['steps']=steps
 with _ENGINE_LOCK:
  (WORK/filename).write_text(json.dumps(record,indent=2,default=str))
  historyfile=WORK/'workflow_history.json'
  try:history=json.loads(historyfile.read_text()) if historyfile.exists() else []
  except (ValueError,OSError):history=[]
  history.append({'id':filename,'file':filename,'workflow':'five-core','status':'ok' if all(x['status']=='ok' for x in steps) else 'partial'})
  historyfile.write_text(json.dumps(history[-100:],indent=2))
 return {'saved':filename,'status':'ok' if all(x['status']=='ok' for x in steps) else 'partial','record':record}


# V33 correlated system bus: operations share one durable activity and artifact graph.
CORRELATION_FILE=WORK/'correlation_events.jsonl'
def correlate(kind, origin, payload=None, artifact=None):
 with SYNC_LOCK:
  event={'revision':SYNC['revision']+1,'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'kind':kind,'origin':origin,'artifact':artifact,'payload':payload or {}}
  SYNC['revision']=event['revision']
  SYNC['events'].append({'revision':event['revision'],'module':'system','kind':kind,'detail':str(artifact or origin)[:200],'time':event['time']})
  SYNC['events']=SYNC['events'][-100:]
  with CORRELATION_FILE.open('a') as f:f.write(json.dumps(event,default=str)+'\n')
 return event
def correlated_state():
 events=[]
 if CORRELATION_FILE.exists():
  with CORRELATION_FILE.open() as f:
   for line in f:
    try:events.append(json.loads(line))
    except ValueError:continue
 return {'version':'46.0','revision':SYNC['revision'],'events':events[-100:],'workspace':[{'name':p.name,'bytes':p.stat().st_size} for p in WORK.iterdir() if p.is_file() and p.name!='correlation_events.jsonl'],'capabilities':{'language':'nexus + terminal interpreters','research':'metrics','project':'shared workspace','simulation':'omniverse state','synchronization':'durable correlated events'}}

# V34.112 dispatches independently testable subsystem adapters through one local API.
import time
SUBSYSTEM_STARTED=time.monotonic()
SUBSYSTEM_NAMES=sorted(p.stem for p in (ROOT/'system'/'subsystems').glob('*.py'))
def subsystem_dispatch(name,data):
 if name not in SUBSYSTEM_NAMES:raise ValueError('unknown subsystem')
 if not isinstance(data,dict):raise ValueError('invalid payload')
 spec=importlib.util.spec_from_file_location('hex_subsystem_'+name,ROOT/'system'/'subsystems'/(name+'.py'))
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 ctx={'data':data,'work':WORK,'root':ROOT,'safe':safe,'engine':engine_call,'workflow':full_workflow,'modules':MODULES,'sync':SYNC,'started':SUBSYSTEM_STARTED,'names':SUBSYSTEM_NAMES,'correlated':correlated_state,'dispatch':subsystem_dispatch}
 return module.run(ctx)

# V35.2: Fabric-independent implementations of supported engine actions.
_SIM_FILE=WORK/'omniverse_state.json'
def _load_sim():
 try:
  value=json.loads(_SIM_FILE.read_text(encoding='utf-8'))
  if isinstance(value,dict) and type(value.get('tick'))==int and isinstance(value.get('entities'),list):return value
 except (OSError,ValueError,TypeError):pass
 return {'tick':0,'entities':[]}
_NATIVE_SIM=_load_sim()
def engine_call(data):
 module=data.get('module'); action=data.get('action')
 if module in ('nexus','terminal') and action=='hexlang':
  source=data.get('source','')
  if not isinstance(source,str) or len(source)>4000:raise ValueError('invalid source')
  import re
  variables={}; outputs=[]; last=None
  def evaluate(expr):
   tree=ast.parse(expr,mode='eval')
   def walk(n):
    if isinstance(n,ast.Constant) and type(n.value) in (int,float,str,bool):return n.value
    if isinstance(n,ast.Name) and n.id in variables:return variables[n.id]
    if isinstance(n,ast.BinOp) and type(n.op) in (ast.Add,ast.Sub,ast.Mult,ast.Div,ast.FloorDiv,ast.Mod,ast.Pow):
     a,b=walk(n.left),walk(n.right)
     if type(n.op)==ast.Pow and (abs(float(b))>12 or abs(float(a))>1e6):raise ValueError('power limit exceeded')
     return {ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv,ast.FloorDiv:operator.floordiv,ast.Mod:operator.mod,ast.Pow:operator.pow}[type(n.op)](a,b)
    if isinstance(n,ast.UnaryOp) and type(n.op) in (ast.USub,ast.UAdd):return (-walk(n.operand) if isinstance(n.op,ast.USub) else +walk(n.operand))
    raise ValueError('unsupported expression')
   return walk(tree.body)
  for line in source.replace(';','\n').splitlines():
   line=line.strip()
   if not line or line.startswith(('#','//')):continue
   match=re.fullmatch(r'(?:let|var|const)\s+([a-zA-Z_]\w*)\s*=\s*(.+)',line)
   if match:
    last=evaluate(match.group(2));variables[match.group(1)]=last
   elif line.startswith('print(') and line.endswith(')'):
    last=evaluate(line[6:-1]);outputs.append(str(last))
   else:last=evaluate(line)
  return {'module':module,'engine':'HEX OS native expression interpreter','result':last,'output':'\n'.join(outputs),'variables':variables,'supported':'arithmetic, variables, print'}
 if module=='research' and action=='metrics':
  values=data.get('values',[])
  if not isinstance(values,list) or len(values)>10000 or any(type(v)!=int or not 0<=v<=0xffffff for v in values):raise ValueError('values must be RGB integers')
  channels=[[((v>>shift)&255) for v in values] for shift in (16,8,0)]
  return {'module':module,'engine':'HEX OS native RGB metrics','result':{'count':len(values),'mean_rgb':[round(statistics.mean(c),3) if c else 0 for c in channels],'min':min(values) if values else None,'max':max(values) if values else None,'unique':len(set(values))}}
 if module=='studio' and action=='list':
  return {'module':module,'engine':'HEX OS native studio','projects':[{'name':p.name,'bytes':p.stat().st_size} for p in WORK.iterdir() if p.is_file() and p.suffix in ('.txt','.hex','.json','.md','.py')][:200]}
 if module=='studio' and action=='read':
  name=data.get('name','')
  if not safe(name):raise ValueError('invalid project name')
  target=WORK/name
  if not target.is_file():raise ValueError('project not found')
  if target.stat().st_size>200000:raise ValueError('project too large')
  return {'module':module,'engine':'HEX OS native studio','name':name,'content':target.read_text(encoding='utf-8')}
 if module=='research' and action=='statistics':
  values=data.get('values',[])
  if not isinstance(values,list) or len(values)>10000 or any(type(x) not in (int,float) or not math.isfinite(x) for x in values):raise ValueError('values must be finite numbers')
  return {'module':module,'engine':'HEX OS native statistics','result':{'count':len(values),'mean':statistics.mean(values) if values else None,'median':statistics.median(values) if values else None,'min':min(values) if values else None,'max':max(values) if values else None,'stdev':statistics.stdev(values) if len(values)>1 else None}}
 if module=='studio' and action=='project':
  name=data.get('name','project.txt');content=data.get('content','')
  if not safe(name) or not isinstance(content,str) or len(content)>200000:raise ValueError('invalid project')
  (WORK/name).write_text(content,encoding='utf-8');return {'module':module,'engine':'HEX OS native studio','saved':name,'bytes':len(content.encode())}
 if module=='omniverse' and action in ('state','step','reset'):
  with _ENGINE_LOCK:
   if action=='reset':_NATIVE_SIM.update(tick=0,entities=[])
   if action=='step':
    steps=data.get('steps',1)
    if type(steps)!=int or not 1<=steps<=5:raise ValueError('steps 1-5')
    _NATIVE_SIM['tick']+=steps
   _SIM_FILE.write_text(json.dumps(_NATIVE_SIM),encoding='utf-8')
   return {'module':module,'engine':'HEX OS native simulation','result':dict(_NATIVE_SIM),'note':'Deterministic minimal simulation, not original Omniverse kernel'}
 raise ValueError('unsupported engine module/action')

# V35.8 expanded native operations; legacy calls remain supported.
_engine_v357 = engine_call
def engine_call(data):
 module=data.get('module'); action=data.get('action')
 if action in ('v38_execute','v38_analyze','v38_project','v38_script','v38_simulate'):
  from system.v38_features import execute
  return execute(module,action,data,WORK)
 if module=='research' and action=='analyze':
  values=data.get('values',[])
  if not isinstance(values,list) or len(values)>10000 or not values or any(type(v) not in (int,float) or not math.isfinite(v) for v in values):raise ValueError('provide 1-10000 finite numbers')
  ordered=sorted(values); avg=statistics.mean(values)
  return {'module':module,'engine':'HEX OS native research v35.8','result':{'count':len(values),'sum':sum(values),'mean':avg,'median':statistics.median(values),'variance':statistics.pvariance(values),'stdev':statistics.pstdev(values),'range':ordered[-1]-ordered[0],'quartiles':{'q1':ordered[(len(ordered)-1)//4],'q3':ordered[(3*(len(ordered)-1))//4]},'sorted':ordered[:100]}}
 if module=='omniverse' and action in ('spawn','remove'):
  with _ENGINE_LOCK:
   if action=='spawn':
    label=data.get('name','entity'); x=data.get('x',0); y=data.get('y',0)
    if not isinstance(label,str) or not 1<=len(label)<=50 or type(x) not in (int,float) or type(y) not in (int,float) or not math.isfinite(x) or not math.isfinite(y):raise ValueError('invalid entity')
    if len(_NATIVE_SIM['entities'])>=100:raise ValueError('entity limit reached')
    eid=max((e['id'] for e in _NATIVE_SIM['entities']),default=0)+1
    _NATIVE_SIM['entities'].append({'id':eid,'name':label,'x':x,'y':y})
   else:
    eid=data.get('id')
    if type(eid)!=int:raise ValueError('integer id required')
    _NATIVE_SIM['entities']=[e for e in _NATIVE_SIM['entities'] if e.get('id')!=eid]
   _SIM_FILE.write_text(json.dumps(_NATIVE_SIM),encoding='utf-8')
   return {'module':module,'engine':'HEX OS native simulation v35.8','result':dict(_NATIVE_SIM)}
 if module=='studio' and action=='delete':
  name=data.get('name','')
  if not safe(name):raise ValueError('invalid project name')
  target=WORK/name
  if not target.is_file() or target.suffix not in ('.txt','.hex','.md','.json','.py'):raise ValueError('project not found or protected')
  target.unlink();return {'module':module,'engine':'HEX OS native studio','deleted':name}
 return _engine_v357(data)


# V37 shared application registry and durable settings (identical across editions).
V37_STATE=WORK/'v37_state.json'
V37_LOCK=threading.RLock()
def v37_registry():
 return {'version':'46.0','edition':'shared-core','applications':[{'id':key,'name':name,'endpoint':'/api/subsystem'} for key,name in MODULES.items()],'state_endpoint':'/api/v38/state'}
def v37_read_state():
 with V37_LOCK:
  if not V37_STATE.exists():return {'version':'46.0','revision':0,'settings':{}}
  try:return json.loads(V37_STATE.read_text(encoding='utf-8'))
  except (OSError,ValueError):return {'version':'46.0','revision':0,'settings':{},'warning':'state unreadable'}
def v37_update_state(data):
 if not isinstance(data,dict):raise ValueError('expected JSON object')
 settings=data.get('settings')
 if not isinstance(settings,dict) or len(settings)>50:raise ValueError('settings must be object with <=50 keys')
 for key,value in settings.items():
  if not isinstance(key,str) or not 1<=len(key)<=64 or not isinstance(value,(str,int,float,bool,type(None))) or (isinstance(value,str) and len(value)>512):raise ValueError('invalid setting')
 with V37_LOCK:
  current=v37_read_state();merged=dict(current.get('settings',{}));merged.update(settings)
  state={'version':'46.0','revision':int(current.get('revision',0))+1,'settings':merged}
  temporary=V37_STATE.with_suffix('.tmp');temporary.write_text(json.dumps(state),encoding='utf-8');temporary.replace(V37_STATE)
  return state

from system import v40_services
from system import v41_security


# V44 local event fabric: durable, bounded events and workflow notifications.
_V44_EVENTS = ROOT / 'workspace' / 'v44_events.jsonl'
_V44_LOCK = __import__('threading').RLock()
def v44_events(limit=50):
 with _V44_LOCK:
  if not _V44_EVENTS.exists():return []
  lines=_V44_EVENTS.read_text(encoding='utf-8').splitlines()[-min(max(limit,1),100):]
  return [json.loads(line) for line in lines if line.strip()]
def v44_publish(data):
 if not isinstance(data,dict):raise ValueError('event must be an object')
 topic=data.get('topic'); source=data.get('source','desktop'); payload=data.get('payload',{})
 if not isinstance(topic,str) or not 1<=len(topic)<=80 or not all(c.isalnum() or c in '._-' for c in topic):raise ValueError('invalid topic')
 if not isinstance(source,str) or len(source)>80 or not isinstance(payload,dict):raise ValueError('invalid event fields')
 event={'id':__import__('uuid').uuid4().hex,'time':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),'topic':topic,'source':source,'payload':payload}
 with _V44_LOCK:
  _V44_EVENTS.parent.mkdir(exist_ok=True,parents=True)
  with _V44_EVENTS.open('a',encoding='utf-8') as f:f.write(json.dumps(event,separators=(',',':'))+'\n')
 return event

# V44.1: persistent local preferences, observable resource metrics, and workflow journal.
_V441_STATE=WORK/'v44_1_state.json'
_V441_LOCK=threading.RLock()
def v441_state():
 with _V441_LOCK:
  try:return json.loads(_V441_STATE.read_text(encoding='utf-8'))
  except (OSError,ValueError):return {'preferences':{},'workflows':[]}
def v441_save(data):
 if not isinstance(data,dict):raise ValueError('state must be an object')
 preferences=data.get('preferences',{})
 if not isinstance(preferences,dict) or len(json.dumps(preferences))>4096:raise ValueError('invalid preferences')
 with _V441_LOCK:
  state=v441_state();state['preferences']=preferences
  tmp=_V441_STATE.with_suffix('.tmp');tmp.write_text(json.dumps(state),encoding='utf-8');tmp.replace(_V441_STATE)
 return state
def v441_monitor():
 import time,platform
 info={'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'platform':platform.system(),'python':platform.python_version(),'pid':os.getpid(),'uptime_seconds':round(time.monotonic()-_V441_STARTED,1),'modules':list(MODULES),'event_count':0}
 if _V44_EVENTS.exists():
  with _V44_LOCK:
   with _V44_EVENTS.open(encoding='utf-8') as f:info['event_count']=sum(1 for _ in f)
 try:
  import resource
  info['max_rss_kb']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
 except ImportError:pass
 return info
_V441_STARTED=__import__('time').monotonic()
def v441_workflow(data):
 if not isinstance(data,dict):raise ValueError('expected object')
 name=data.get('name','five-app-handoff')
 if name!='five-app-handoff':raise ValueError('unknown workflow')
 run_id=__import__('uuid').uuid4().hex
 stages=['nexus','research','studio','terminal','omniverse']
 for stage in stages:v44_publish({'topic':'workflow.stage','source':stage,'payload':{'run_id':run_id,'stage':stage,'status':'notified'}})
 record={'id':run_id,'name':name,'stages':stages,'status':'notifications-sent','time':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 with _V441_LOCK:
  state=v441_state();state['workflows']=(state.get('workflows',[])+[record])[-30:]
  tmp=_V441_STATE.with_suffix('.tmp');tmp.write_text(json.dumps(state),encoding='utf-8');tmp.replace(_V441_STATE)
 return record

# V45 executes the existing five-engine workflow rather than sending notifications only.
def v45_execute(data):
 if not isinstance(data,dict):raise ValueError('expected JSON object')
 if data.get('name','five-core')!='five-core':raise ValueError('unsupported workflow')
 run_id=__import__('uuid').uuid4().hex
 v44_publish({'topic':'v45.workflow.started','source':'core','payload':{'run_id':run_id}})
 result=full_workflow({})
 status=result['status']
 record={'id':run_id,'name':'five-core','status':status,'saved':result['saved'],'steps':[{'step':x['step'],'status':x['status'],'error':x.get('error')} for x in result['record']['steps']],'time':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 with _V441_LOCK:
  state=v441_state();state['workflows']=(state.get('workflows',[])+[record])[-30:]
  tmp=_V441_STATE.with_suffix('.tmp');tmp.write_text(json.dumps(state),encoding='utf-8');tmp.replace(_V441_STATE)
 v44_publish({'topic':'v45.workflow.completed','source':'core','payload':{'run_id':run_id,'status':status,'saved':result['saved']}})
 return record

_V46_LOCK=threading.RLock()
def v46_session():
 with _V46_LOCK:
  p=WORK/'v46_session.json'
  if not p.exists():return {}
  try:return json.loads(p.read_text())
  except (ValueError,OSError):return {}

# V47: bounded local assistant, workflow orchestration and resource snapshot.
_V47_LOCK=threading.RLock()
def v47_resource_snapshot():
 import time,platform
 info={'platform':platform.system(),'python':platform.python_version(),'pid':os.getpid(),'uptime_seconds':round(time.monotonic()-_V47_STARTED,1),'applications':len(MODULES)}
 try:
  import resource
  info['peak_rss_kb']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
 except ImportError:info['peak_rss_kb']=None
 try:info['load_average']=list(os.getloadavg())
 except (OSError,AttributeError):info['load_average']=None
 return info
_V47_STARTED=__import__('time').monotonic()
def v47_assist(data):
 prompt=data.get('prompt','')
 if not isinstance(prompt,str) or not 1<=len(prompt)<=2000:raise ValueError('prompt must be 1..2000 characters')
 lower=prompt.lower()
 if any(x in lower for x in ('workflow','automate','coordinate')):
  answer='Use Run five-engine workflow to execute the existing supported application adapters. Review each stage result before using generated files.'
 elif any(x in lower for x in ('file','project','studio')):
  answer='Open Studio Pro to manage workspace projects. The V46 application registry lists the supported project actions.'
 elif any(x in lower for x in ('cpu','memory','resource','performance')):
  answer='Use Resource Snapshot for process uptime, peak memory usage where supported, and system load averages.'
 else:answer='I am the V47 offline command helper, not a generative AI model. I can guide you to workflows, Studio projects, application actions, and monitoring. External AI models are not configured.'
 return {'mode':'offline-rule-based','answer':answer,'model_connected':False}
def v47_workflow(data):
 steps=data.get('steps')
 permitted={'research':{'statistics','metrics'},'studio':{'list','read','project'},'omniverse':{'state','step','reset'}}
 if not isinstance(steps,list) or not 1<=len(steps)<=8:raise ValueError('steps must be a list of 1..8 actions')
 results=[]
 for i,step in enumerate(steps):
  if not isinstance(step,dict):raise ValueError('invalid step')
  module=step.get('module');action=step.get('action')
  if action not in permitted.get(module,set()):raise ValueError('workflow action not permitted')
  if len(json.dumps(step))>3000:raise ValueError('step too large')
  try:results.append({'index':i,'module':module,'action':action,'status':'ok','result':engine_call(step)})
  except Exception as exc:
   results.append({'index':i,'module':module,'action':action,'status':'error','error':str(exc)[:180]});break
 report={'status':'ok' if len(results)==len(steps) and all(x['status']=='ok' for x in results) else 'partial','steps':results,'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 with _V47_LOCK:
  path=WORK/'v47_workflow_history.json'
  try:history=json.loads(path.read_text()) if path.exists() else []
  except (ValueError,OSError):history=[]
  history=(history+[{'status':report['status'],'created_at':report['created_at'],'steps':[{'module':x['module'],'action':x['action'],'status':x['status']} for x in results]}])[-50:]
  tmp=WORK/'v47_workflow_history.tmp';tmp.write_text(json.dumps(history));tmp.replace(path)
 return report

# Lite 6 shared data fabric: bounded JSON artifacts, restricted to registered applications.
LITE6_APPS=('nexus','research','studio','terminal','omniverse')
LITE6_STORE=WORK/'lite6_shared.json'
def lite6_load():
 try:
  data=json.loads(LITE6_STORE.read_text())
  return data if isinstance(data,dict) else {}
 except (FileNotFoundError,ValueError,OSError):return {}
def lite6_exchange(data):
 import time
 sender=data.get('source');target=data.get('target');name=data.get('name');value=data.get('value')
 if sender not in LITE6_APPS or target not in LITE6_APPS:raise ValueError('unknown application')
 if not isinstance(name,str) or not (1<=len(name)<=64) or not all(c.isalnum() or c in '_-' for c in name):raise ValueError('invalid artifact name')
 if len(json.dumps(value))>8192:raise ValueError('artifact too large')
 items=lite6_load();key=target+':'+name
 items[key]={'source':sender,'target':target,'name':name,'value':value,'timestamp':time.time()}
 if len(items)>100:items=dict(list(items.items())[-100:])
 tmp=LITE6_STORE.with_suffix('.tmp');tmp.write_text(json.dumps(items));tmp.replace(LITE6_STORE)
 return {'ok':True,'artifact':items[key],'count':len(items)}

class Handler(SimpleHTTPRequestHandler):
 def end_headers(self):
  for key,value in v41_security.HEADERS.items():self.send_header(key,value)
  super().end_headers()
 def translate_path(self,path):
  # Serve only public desktop assets; never expose Python, state, tests or workspace.
  return str(v41_security.public_path(ROOT,path))
 def log_message(self,fmt,*args):
  return super().log_message(fmt,*args)
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
 def respond(self,obj,status=200):
  raw=json.dumps(obj).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(raw)
 def v46_body(self):
  size=int(self.headers.get('Content-Length','0'))
  if not 0<size<=16384:raise ValueError('request must be 1..16384 bytes')
  data=json.loads(self.rfile.read(size))
  if not isinstance(data,dict):raise ValueError('JSON object required')
  return data
 def do_GET(self):
  path=urlsplit(self.path).path
  if path in ('/','/web/'):
   self.path='/web/index.html'
   return super().do_GET()
  if path=='/api/lite6/manifest':
   self.respond({'version':'6.0','edition':'Unified Intelligence','applications':list(LITE6_APPS),'data_exchange':'/api/lite6/exchange','artifacts':'/api/lite6/artifacts','ai_model_connected':False});return
  if path=='/api/lite6/artifacts':
   self.respond({'artifacts':list(lite6_load().values())});return
  if path=='/api/v47/manifest':
   self.respond({'version':'47.0','edition':'Intelligent System','capabilities':['offline-command-helper','bounded-workflows','resource-monitor','session-metadata'],'ai_model_connected':False});return
  if path=='/api/v47/resources':
   self.respond(v47_resource_snapshot());return
  if path=='/api/v47/history':
   p=WORK/'v47_workflow_history.json'
   try:history=json.loads(p.read_text()) if p.exists() else []
   except (ValueError,OSError):history=[]
   self.respond({'history':history[-50:]});return
  if path=='/api/v46/manifest':
   self.respond({'version':'46.0','edition':'Unified Runtime','capabilities':['module-invoke','shared-event-bus','session-persistence','monitor','workflow-execution'],'ai':'not configured','security':'local-only'});return
  if path=='/api/v46/apps':
   self.respond({'apps':[{'id':k,'name':v,'actions':{'nexus':['hexlang'],'research':['metrics','statistics'],'studio':['list','read','project'],'terminal':['hexlang'],'omniverse':['state','step','reset']}[k]} for k,v in MODULES.items()]});return
  if path=='/api/v46/session':
   self.respond({'session':v46_session()});return
  if path=='/api/v46/monitor':
   self.respond(v441_monitor());return
  if path=='/api/v45/manifest':
   self.respond({'version':'45.0','edition':'Executable Workflow','workflow':'/api/v45/workflows/execute','history':'/api/v44.1/workflows'});return
  if path=='/api/v44.1/monitor':
   self.respond(v441_monitor());return
  if path=='/api/v44.1/state':
   self.respond(v441_state());return
  if path=='/api/v44.1/workflows':
   self.respond({'workflows':v441_state().get('workflows',[])});return
  if path=='/api/v44/manifest':
   self.respond({'version':'44.1','edition':'Unified Core Evolution','capabilities':['event-fabric','responsive-desktop','shared-workspace','five-engines'],'events':'/api/v44/events'});return
  if path=='/api/v44/events':
   self.respond({'events':v44_events()});return
  if path=='/api/v38/registry':
   self.respond(v37_registry());return
  if path=='/api/v38/state':
   self.respond(v37_read_state());return
  if path=='/api/v41/security':
   self.respond(v41_security.status());return
  if path=='/api/v40/services':
   self.respond(v40_services.snapshot());return
  if path=='/api/v40/events':
   self.respond(v40_services.events());return
  if path=='/api/v40/permissions':
   self.respond(v40_services.permissions());return
  if path=='/api/v40/resources':
   self.respond(v40_services.resources());return
  if path=='/api/diagnostics':
   self.respond({'ok':True,'version':'46.0','subsystems':SUBSYSTEM_NAMES,'workspace_exists':WORK.is_dir(),'fabric_required':False});return
  if path=='/api/subsystems':self.respond({'version':'46.0','subsystems':SUBSYSTEM_NAMES});return
  if path=='/api/correlated':self.respond(correlated_state());return
  if path=='/api/sync':
   with SYNC_LOCK:self.respond(dict(SYNC));return
  if path=='/api/workflows':
   history=WORK/'workflow_history.json'
   self.respond({'version':'46.0','workflows':['bell-research','five-core'],'history':json.loads(history.read_text()) if history.exists() else []});return
  if path=='/api/engines':
   self.respond({'version':'46.0','actions':{'nexus':['hexlang'],'research':['metrics'],'studio':['project'],'terminal':['hexlang'],'omniverse':['state','step','reset']}});return
  if path=='/api/version':
   self.respond({'version':'46.0','edition':'Unified Core','api':'v1'});return
  if path=='/api/health':
   self.respond({'ok':True,'version':'8.0.1','service':'HEX OS X Lite Stability Patch','workspace':str(WORK),'modules':len(MODULES),'legacy_engines_available':all((ROOT/'modules'/k).is_dir() for k in MODULES),'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat()});return
  if path=='/api/modules':
   self.respond({'version':'46.0','modules':[{'id':k,'name':v,'installed':(ROOT/'modules'/k).is_dir(),'native':True,'source_files':sum(1 for p in (ROOT/'modules'/k).rglob('*') if p.is_file()),'python_files':sum(1 for p in (ROOT/'modules'/k).rglob('*.py'))} for k,v in MODULES.items()]});return
  if path=='/api/jobs':
   self.respond({'jobs':[], 'note':'No background execution enabled; safe local-only service'});return
  if path=='/api/workspace':
   self.respond({'files':[{'name':p.name,'size':p.stat().st_size} for p in WORK.iterdir() if p.is_file()]});return
  if path=='/api/read':
   name=parse_qs(urlsplit(self.path).query).get('name',[''])[0]
   if not safe(name):self.respond({'error':'invalid filename'},400);return
   p=WORK/name
   if not p.is_file():self.respond({'error':'not found'},404);return
   if p.stat().st_size>1024*1024:self.respond({'error':'file too large'},413);return
   self.respond({'name':name,'content':p.read_text(errors='replace')});return
  if path.startswith('/modules/'):
   self.respond({'error':'module source files are not served directly'},403);return
  if not v41_security.allowed_static(path):
   self.respond({'error':'resource not public'},403);return
  return super().do_GET()
 def do_POST(self):
  route=urlsplit(self.path).path
  if route=='/api/lite6/exchange':
   try:self.respond(lite6_exchange(self.v46_body()))
   except (ValueError,TypeError,KeyError) as exc:self.respond({'error':str(exc)},400)
   except OSError:self.respond({'error':'storage unavailable'},500)
   return
  if route in ('/api/v47/assist','/api/v47/workflow'):
   try:
    data=self.v46_body()
    result=v47_assist(data) if route.endswith('/assist') else v47_workflow(data)
    self.respond(result)
   except (ValueError,TypeError,KeyError) as exc:self.respond({'error':str(exc)},400)
   except Exception:self.respond({'error':'V47 operation failed'},500)
   return
  if route in ('/api/v46/invoke','/api/v46/session'):
   try:
    data=self.v46_body()
    if route.endswith('/invoke'):
     module=data.get('module');action=data.get('action')
     permitted={'nexus':{'hexlang'},'research':{'metrics','statistics'},'studio':{'list','read','project'},'terminal':{'hexlang'},'omniverse':{'state','step','reset'}}
     if action not in permitted.get(module,set()):raise ValueError('unsupported application action')
     result=engine_call(data)
     v44_publish({'topic':'v46.app.invoked','source':module,'payload':{'action':action}})
     self.respond({'ok':True,'data':result})
    else:
     allowed={'active_app','theme','open_apps','window_layout'}
     if set(data)-allowed:raise ValueError('unsupported session fields')
     if len(json.dumps(data))>8000:raise ValueError('session too large')
     if 'active_app' in data and data['active_app'] not in list(MODULES)+[None]:raise ValueError('invalid active app')
     if 'open_apps' in data and (not isinstance(data['open_apps'],list) or len(data['open_apps'])>10 or any(x not in MODULES for x in data['open_apps'])):raise ValueError('invalid open apps')
     if 'theme' in data and data['theme'] not in ('dark','light'):raise ValueError('invalid theme')
     if 'window_layout' in data and not isinstance(data['window_layout'],dict):raise ValueError('invalid window layout')
     with _V46_LOCK:
      target=WORK/'v46_session.json';temp=WORK/'v46_session.tmp'
      temp.write_text(json.dumps(data));temp.replace(target)
     self.respond({'ok':True,'session':data})
   except (ValueError,TypeError,json.JSONDecodeError) as exc:self.respond({'error':str(exc)},400)
   except Exception as exc:self.respond({'error':'operation failed','detail':str(exc)[:160]},500)
   return
  if route=='/api/v45/workflows/execute':
   try:
    size=int(self.headers.get('Content-Length','0'))
    if not 0<size<=4096:raise ValueError('invalid request size')
    data=json.loads(self.rfile.read(size))
    self.respond(v45_execute(data),201)
   except (ValueError,TypeError) as exc:self.respond({'error':str(exc)},400)
   except Exception as exc:self.respond({'error':'workflow execution failed','detail':str(exc)[:200]},500)
   return
  if route in ('/api/v44.1/state','/api/v44.1/workflows'):
   try:
    size=int(self.headers.get('Content-Length','0'))
    if not 0<size<=8192:raise ValueError('invalid request size')
    data=json.loads(self.rfile.read(size))
    self.respond(v441_save(data) if route.endswith('/state') else v441_workflow(data),201)
   except (ValueError,TypeError,json.JSONDecodeError) as exc:self.respond({'error':str(exc)},400)
   return
  if route=='/api/v44/events':
   try:
    size=int(self.headers.get('Content-Length','0'))
    if not 0<size<=4096:raise ValueError('invalid request size')
    self.respond({'event':v44_publish(json.loads(self.rfile.read(size)))},201)
   except (ValueError,TypeError,json.JSONDecodeError) as exc:self.respond({'error':str(exc)},400)
   return
  if route=='/api/v38/state':
   try:
    size=int(self.headers.get('Content-Length','0'))
    if not 0<size<=8192:raise ValueError('invalid request size')
    data=json.loads(self.rfile.read(size))
    self.respond(v37_update_state(data))
   except (ValueError,TypeError,json.JSONDecodeError) as exc:self.respond({'error':str(exc)},400)
   return
  if route=='/api/sync':
   try:
    size=int(self.headers.get('Content-Length','0'))
    if not 0<size<=4096:raise ValueError('invalid event size')
    data=json.loads(self.rfile.read(size));module=data.get('module');kind=data.get('kind');detail=data.get('detail','')
    if module not in MODULES and module not in ('quantum','system'):raise ValueError('unknown module')
    if not isinstance(kind,str) or len(kind)>50 or not isinstance(detail,str) or len(detail)>500:raise ValueError('invalid event')
    with SYNC_LOCK:
     SYNC['revision']+=1;SYNC['events'].append({'revision':SYNC['revision'],'module':module,'kind':kind,'detail':detail,'time':datetime.datetime.now(datetime.timezone.utc).isoformat()});SYNC['events']=SYNC['events'][-100:];snapshot=dict(SYNC)
    return self.respond(snapshot)
   except Exception as exc:return self.respond({'error':str(exc)[:200]},400)
  if route=='/api/workflow/full':
   try:
    size=int(self.headers.get('Content-Length','0'))
    if not 0<size<=8192:raise ValueError('invalid payload size')
    data=json.loads(self.rfile.read(size))
    if not isinstance(data,dict):raise ValueError('expected object')
    for key in ('nexus_source','terminal_source'):
     if key in data and (not isinstance(data[key],str) or len(data[key])>1000):raise ValueError('invalid '+key)
    result=full_workflow(data);correlate('workflow.completed','system',{'status':result['status']},result['saved']);return self.respond(result)
   except Exception as exc:return self.respond({'error':str(exc)[:300]},400)
  if route=='/api/workflow/run':
   try:
    size=int(self.headers.get('Content-Length','0'))
    if not 0<size<=4096:raise ValueError('invalid payload size')
    data=json.loads(self.rfile.read(size))
    if data.get('workflow')!='bell-research':raise ValueError('unsupported workflow')
    # Bell-state probabilities computed with the same ideal-state mathematics as Quantum Lab.
    probabilities=[0.5,0.0,0.0,0.5]
    values=[round(v*0xffffff) for v in probabilities]
    research=engine_call({'module':'research','action':'metrics','values':values})
    record={'id':datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'),
            'workflow':'bell-research','quantum':{'qubits':2,'gates':['H(0)','CNOT(0,1)'],'probabilities':probabilities},
            'research':research['result'],'note':'Probabilities scaled to RGB integers for original research metrics; not a quantum-specific statistic.'}
    filename='workflow_'+record['id']+'.json'
    (WORK/filename).write_text(json.dumps(record,indent=2,default=str))
    historyfile=WORK/'workflow_history.json'
    with _ENGINE_LOCK:
     history=json.loads(historyfile.read_text()) if historyfile.exists() else []
     history.append({'id':record['id'],'file':filename,'workflow':record['workflow']})
     historyfile.write_text(json.dumps(history[-100:],indent=2))
    correlate('workflow.completed','research',{'workflow':record['workflow']},filename);return self.respond({'saved':filename,'record':record})
   except Exception as exc:return self.respond({'error':str(exc)[:300]},400)
  if route=='/api/subsystem':
   try:
    size=int(self.headers.get('Content-Length','0'))
    if not 0<size<=262144:raise ValueError('invalid request size')
    data=json.loads(self.rfile.read(size));result=subsystem_dispatch(data.get('subsystem',''),data.get('data',{}))
    correlate('subsystem.executed',str(data.get('subsystem')),{'status':'ok'});return self.respond({'ok':True,'result':result})
   except Exception as exc:return self.respond({'ok':False,'error':str(exc)[:300]},400)
  if route=='/api/engine':
   try:
    size=int(self.headers.get('Content-Length','0'))
    if not 0<size<=32768:return self.respond({'error':'invalid size'},413)
    data=json.loads(self.rfile.read(size))
    result=engine_call(data)
    correlate('engine.'+str(data.get('action')),str(data.get('module')),{'engine':result.get('engine','')},result.get('saved'))
    with SYNC_LOCK:
     SYNC['revision']+=1;SYNC['events'].append({'revision':SYNC['revision'],'module':data.get('module'),'kind':data.get('action'),'detail':'Engine operation completed','time':datetime.datetime.now(datetime.timezone.utc).isoformat()});SYNC['events']=SYNC['events'][-100:]
    return self.respond(result)
   except Exception as exc:return self.respond({'error':str(exc)[:300]},400)
  if route=='/api/quantum/experiment':
   try:
    size=int(self.headers.get('Content-Length','0'))
    if not 0<size<=8192:return self.respond({'error':'invalid size'},413)
    data=json.loads(self.rfile.read(size));n=data.get('qubits',2);gates=data.get('gates',[])
    if type(n)!=int or not 1<=n<=8 or not isinstance(gates,list) or len(gates)>100:raise ValueError('invalid circuit')
    import math,cmath,random
    state=[0j]*(1<<n);state[0]=1+0j
    for gate in gates:
     if not isinstance(gate,dict):raise ValueError('invalid gate')
     op=gate.get('gate');t=gate.get('target');c=gate.get('control')
     if op not in ('H','X','Z','S','T','CNOT') or type(t)!=int or not 0<=t<n:raise ValueError('invalid gate')
     if op=='CNOT':
      if type(c)!=int or not 0<=c<n or c==t:raise ValueError('invalid control')
      for i in range(len(state)):
       if not (i>>t)&1 and (i>>c)&1:state[i],state[i|(1<<t)]=state[i|(1<<t)],state[i]
     else:
      v=2**-.5;matrix={'H':(v,v,v,-v),'X':(0,1,1,0),'Z':(1,0,0,-1),'S':(1,0,0,1j),'T':(1,0,0,cmath.exp(1j*math.pi/4))}[op]
      for i in range(len(state)):
       if not i&(1<<t):
        j=i|(1<<t);a,b=state[i],state[j];state[i]=matrix[0]*a+matrix[1]*b;state[j]=matrix[2]*a+matrix[3]*b
    probs=[round(abs(v)**2,10) for v in state]
    result={'qubits':n,'gates':gates,'probabilities':probs,'basis':[format(i,f'0{n}b') for i in range(len(state))],'engine':'classical ideal statevector'}
    if data.get('save') is True:
     name='quantum_experiment.json';(WORK/name).write_text(json.dumps(result,indent=2));result['saved']=name
    return self.respond(result)
   except (ValueError,TypeError,KeyError,json.JSONDecodeError) as e:return self.respond({'error':str(e)},400)
  if route=='/api/ai':
   try:
    size=int(self.headers.get('Content-Length','0'))
    if not 0<size<=8192:return self.respond({'error':'invalid size'},413)
    msg=str(json.loads(self.rfile.read(size)).get('message',''))[:1000].strip()
    lower=msg.lower()
    if 'module' in lower or 'app' in lower:answer='Installed modules: '+', '.join(MODULES.values())+'.'
    elif 'file' in lower or 'workspace' in lower:answer=f'The shared workspace contains {len(list(WORK.iterdir()))} entries. Use Files or Studio to edit them.'
    elif 'version' in lower:answer='HEX OS X V32.0 Unified Workflows Edition.'
    elif 'quantum' in lower:answer='Open Quantum Lab to simulate ideal statevectors and gates. This is not physical quantum hardware.'
    elif 'health' in lower or 'status' in lower:answer='HEX Lite 8.0.1 is online. Legacy engines require their original module files.'
    else:answer='Offline assistant: I can report module status, workspace files, system health, and quantum features. No external LLM is connected.'
    return self.respond({'answer':answer,'mode':'offline-rules','model_connected':False})
   except (ValueError,UnicodeError,json.JSONDecodeError) as e:return self.respond({'error':str(e)},400)
  if route!='/api/write':self.respond({'error':'unknown endpoint'},404);return
  try:
   size=int(self.headers.get('Content-Length','0'))
   if size>1024*1024 or size<1:self.respond({'error':'invalid size'},413);return
   data=json.loads(self.rfile.read(size));name=data.get('name','');content=data.get('content','')
   if not safe(name) or not isinstance(content,str) or len(content.encode())>1024*1024:raise ValueError('invalid file')
   (WORK/name).write_text(content);correlate('file.saved','workspace',{'bytes':len(content)},name);self.respond({'saved':name})
  except (ValueError,UnicodeError,json.JSONDecodeError) as e:self.respond({'error':str(e)},400)
def safe(name):return isinstance(name,str) and 0<len(name)<=100 and name not in ('.','..') and all(c.isalnum() or c in '._- ' for c in name)
if __name__=='__main__':
 import sys
 port=int(sys.argv[1]) if len(sys.argv)>1 else 8080
 server=None
 for candidate in [port]:
  try:
   server=ThreadingHTTPServer(('127.0.0.1',candidate),Handler);port=candidate;break
  except OSError as exc:
   if exc.errno not in (48,98,10048):raise
 if server is None:sys.exit('Requested port is already in use; stop the old server or set PORT to another port')
 print(f'HEX Lite V8.0.1 STABILITY READY: http://127.0.0.1:{port}/',flush=True)
 try:server.serve_forever()
 except KeyboardInterrupt:print('HEX OS stopped')
 finally:server.server_close()
