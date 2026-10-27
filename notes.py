"""HEX OS X V34 subsystem adapter: notes."""
def run(ctx):
 from datetime import datetime,timezone
 data=ctx['data'];name=data.get('name','note.txt');assert ctx['safe'](name),'invalid name'
 if 'content' in data:return ctx['dispatch']('file_write',{'name':name,'content':data['content']})
 return ctx['dispatch']('file_read',{'name':name})
