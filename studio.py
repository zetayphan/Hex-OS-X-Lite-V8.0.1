"""HEX OS X V34 subsystem adapter: studio."""
def run(ctx):
 return ctx['engine']({'module':'studio','action':'project','name':ctx['data'].get('name','studio_project.txt'),'content':ctx['data'].get('content','')})
