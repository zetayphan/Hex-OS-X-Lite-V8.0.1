"""HEX OS X V34 subsystem adapter: tasks."""
def run(ctx):
 import json
 p=ctx['work']/'subsystem_tasks.json';items=json.loads(p.read_text()) if p.exists() else []
 data=ctx['data'];action=data.get('action','list')
 if action=='add':
  title=str(data.get('title','')).strip()[:200];assert title,'missing title';items.append({'id':max([x['id'] for x in items],default=0)+1,'title':title,'done':False})
 elif action=='toggle':
  for x in items:
   if x['id']==data.get('id'):x['done']=not x['done']
 elif action!='list':raise ValueError('unsupported action')
 if action!='list':p.write_text(json.dumps(items))
 return {'tasks':items[-200:]}
