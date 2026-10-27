"""HEX OS X V34 subsystem adapter: workflow."""
def run(ctx):
 return ctx['workflow'](ctx['data'])
