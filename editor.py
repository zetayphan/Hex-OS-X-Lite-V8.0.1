"""HEX OS X V34 subsystem adapter: editor."""
def run(ctx):
 action=ctx['data'].get('action','read')
 return ctx['dispatch']('file_write' if action=='save' else 'file_read',ctx['data'])
