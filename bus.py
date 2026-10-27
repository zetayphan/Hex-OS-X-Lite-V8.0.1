"""HEX OS X V34 subsystem adapter: bus."""
def run(ctx):
 return {'correlation':ctx['correlated'](),'sync':ctx['sync']}
