"""HEX OS X V34 subsystem adapter: monitor."""
def run(ctx):
 import os,platform,time
 return {'platform':platform.platform(),'pid':os.getpid(),'uptime_seconds':round(time.monotonic()-ctx['started'],1),'workspace_files':len(list(ctx['work'].iterdir()))}
