"""HEX OS X V34 subsystem adapter: nexus."""
def run(ctx):
 return ctx['engine']({'module':'nexus','action':'hexlang','source':ctx['data'].get('source','print(2+3)')})
