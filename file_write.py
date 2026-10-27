"""HEX OS X V34 subsystem adapter: file_write."""
def run(ctx):
 name=ctx['data'].get('name','');value=ctx['data'].get('content','');assert ctx['safe'](name) and isinstance(value,str) and len(value)<200000,'invalid file';(ctx['work']/name).write_text(value,encoding='utf-8');return {'saved':name}
