"""HEX OS V38 bounded, native advanced operations (no Python eval or shell)."""
import ast,operator,statistics,json,math,datetime
from pathlib import Path
OPS={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv,ast.Mod:operator.mod,ast.Pow:operator.pow}
def arithmetic(expr,vars):
 def walk(n,depth=0):
  if depth>16:raise ValueError('expression too deep')
  if isinstance(n,ast.Constant) and type(n.value) in (int,float):return n.value
  if isinstance(n,ast.Name) and n.id in vars:return vars[n.id]
  if isinstance(n,ast.UnaryOp) and isinstance(n.op,(ast.USub,ast.UAdd)):return (-1 if isinstance(n.op,ast.USub) else 1)*walk(n.operand,depth+1)
  if isinstance(n,ast.BinOp) and type(n.op) in OPS:
   a,b=walk(n.left,depth+1),walk(n.right,depth+1)
   if isinstance(n.op,ast.Pow) and abs(b)>10:raise ValueError('exponent too large')
   value=OPS[type(n.op)](a,b)
   if not math.isfinite(value) or abs(value)>1e12:raise ValueError('result out of range')
   return value
  raise ValueError('unsupported expression')
 if not isinstance(expr,str) or len(expr)>200:raise ValueError('invalid expression')
 return walk(ast.parse(expr,mode='eval').body)
def execute(module,action,data,work):
 if module in ('nexus','terminal') and action in ('v38_execute','v38_script'):
  source=data.get('source','');variables={};outputs=[]
  if not isinstance(source,str) or len(source)>4000:raise ValueError('invalid source')
  for line in source.splitlines():
   line=line.strip()
   if not line or line.startswith('#'):continue
   if line.startswith('print '):outputs.append(str(arithmetic(line[6:],variables)))
   elif '=' in line:
    key,expr=line.split('=',1);key=key.strip()
    if not key.isidentifier() or len(key)>40 or key.startswith('_'):raise ValueError('invalid variable')
    variables[key]=arithmetic(expr.strip(),variables)
   else:outputs.append(str(arithmetic(line,variables)))
  return {'engine':'HEX V38 bounded interpreter','variables':variables,'output':'\n'.join(outputs)}
 if module=='research' and action=='v38_analyze':
  values=data.get('values',[])
  if not isinstance(values,list) or not 1<=len(values)<=10000 or any(type(v) not in (int,float) or not math.isfinite(v) for v in values):raise ValueError('invalid values')
  ordered=sorted(values);n=len(values)
  return {'engine':'HEX V38 research','count':n,'mean':statistics.mean(values),'median':statistics.median(values),'population_stdev':statistics.pstdev(values),'quartiles':{'q1':ordered[(n-1)//4],'q3':ordered[3*(n-1)//4]},'histogram':{str(x):values.count(x) for x in set(values)} if n<=100 else None}
 if module=='studio' and action=='v38_project':
  name=data.get('name','project.hex');content=data.get('content','')
  if not isinstance(name,str) or not name.endswith(('.hex','.txt','.md','.py')) or not 1<=len(name)<=80 or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-' for c in name):raise ValueError('invalid filename')
  if not isinstance(content,str) or len(content)>100000:raise ValueError('invalid content')
  target=work/name;target.write_text(content,encoding='utf-8');return {'saved':name,'bytes':target.stat().st_size}
 if module=='omniverse' and action=='v38_simulate':
  steps=data.get('steps',1);velocity=data.get('velocity',1.0)
  if type(steps)!=int or not 1<=steps<=100 or type(velocity) not in (int,float) or not math.isfinite(velocity) or abs(velocity)>100:raise ValueError('invalid simulation')
  statefile=work/'v38_simulation.json';state=json.loads(statefile.read_text()) if statefile.exists() else {'tick':0,'position':0.0}
  state['tick']+=steps;state['position']+=steps*velocity;statefile.write_text(json.dumps(state));return {'state':state}
 raise ValueError('unsupported V38 operation')
