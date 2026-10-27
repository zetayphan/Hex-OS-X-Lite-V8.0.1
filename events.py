"""HEX OS X V34 subsystem adapter: events."""
def run(ctx):
 return {'events':ctx['sync']['events'][-100:],'revision':ctx['sync']['revision']}
