import sys,tempfile,pathlib
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from system.v38_features import execute
with tempfile.TemporaryDirectory() as d:
 p=pathlib.Path(d)
 assert execute('nexus','v38_execute',{'source':'x=3\nprint x*4'},p)['output']=='12'
 assert execute('terminal','v38_script',{'source':'print 2+2'},p)['output']=='4'
 assert execute('research','v38_analyze',{'values':[1,2,3]},p)['mean']==2
 assert execute('studio','v38_project',{'name':'demo.hex','content':'print 1'},p)['saved']=='demo.hex'
 assert execute('omniverse','v38_simulate',{'steps':2},p)['state']['tick']==2
print('V38: five native operations passed')
