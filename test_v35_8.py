import sys,unittest,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'system'))
import core
class Features(unittest.TestCase):
 def test_research(self):
  r=core.engine_call({'module':'research','action':'analyze','values':[1,2,3]})['result'];self.assertEqual(r['mean'],2)
 def test_simulation(self):
  r=core.engine_call({'module':'omniverse','action':'spawn','name':'test'})['result'];self.assertTrue(r['entities']);core.engine_call({'module':'omniverse','action':'remove','id':r['entities'][-1]['id']})
 def test_native_baseline(self):
  self.assertEqual(core.engine_call({'module':'nexus','action':'hexlang','source':'print(2+3)'})['result'],5)
if __name__=='__main__':unittest.main()
