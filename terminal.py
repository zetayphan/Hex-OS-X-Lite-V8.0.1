"""HEX OS X V34 subsystem adapter: terminal."""
def run(ctx):
 return ctx['engine']({'module':'terminal','action':'hexlang','source':ctx['data'].get('source','let x = 2 + 3')})
