"""HEX OS X V34 subsystem adapter: files."""
def run(ctx):
 return {'files':[{'name':p.name,'bytes':p.stat().st_size} for p in sorted(ctx['work'].iterdir()) if p.is_file()][:200]}
