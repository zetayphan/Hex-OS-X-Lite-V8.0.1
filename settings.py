"""HEX OS X V34 subsystem adapter: settings."""
def run(ctx):
 import json
 p=ctx['work']/'subsystem_settings.json';settings=json.loads(p.read_text()) if p.exists() else {'theme':'dark','accent':'#4de6dc'}
 if ctx['data'].get('action')=='update':
  for k in ('theme','accent'):
   if k in ctx['data']:settings[k]=str(ctx['data'][k])[:30]
  p.write_text(json.dumps(settings))
 return {'settings':settings}
