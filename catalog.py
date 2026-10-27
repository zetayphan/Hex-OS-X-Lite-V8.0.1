"""HEX OS X V34 subsystem adapter: catalog."""
def run(ctx):
 return {'subsystems':ctx['names'],'count':len(ctx['names'])}
