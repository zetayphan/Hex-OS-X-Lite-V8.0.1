"""HEX OS X V34 subsystem adapter: research."""
def run(ctx):
 return ctx['engine']({'module':'research','action':'metrics','values':ctx['data'].get('values',[0,16777215])})
