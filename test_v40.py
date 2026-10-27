import sys, pathlib
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from system import v40_services as s
assert s.snapshot()['service_count']==5
assert s.resources()['disk']['total']>0
assert s.permissions()['mode']=='local-only'
assert isinstance(s.events()['events'],list)
print('V40 service smoke tests passed')
