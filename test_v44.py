import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from system.core import v44_publish,v44_events
e=v44_publish({'topic':'test.ping','source':'test','payload':{'ok':True}})
assert any(x['id']==e['id'] for x in v44_events())
print('PASS V44 durable event fabric')
