"""HEX OS X V34 subsystem adapter: file_read."""
def run(ctx):
 name=ctx['data'].get('name','');assert ctx['safe'](name),'invalid filename';p=ctx['work']/name
 return {'name':name,'content':p.read_text(encoding='utf-8')[:200000]}
