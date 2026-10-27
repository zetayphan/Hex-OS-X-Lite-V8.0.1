import sys,unittest,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'system'))
import core
class Lite6Tests(unittest.TestCase):
 def test_exchange(self):
  with tempfile.TemporaryDirectory() as d:
   old=core.LITE6_STORE;core.LITE6_STORE=Path(d)/'shared.json'
   try:
    result=core.lite6_exchange({'source':'research','target':'studio','name':'results','value':{'count':3}})
    self.assertTrue(result['ok']);self.assertEqual(core.lite6_load()['studio:results']['value']['count'],3)
    with self.assertRaises(ValueError):core.lite6_exchange({'source':'unknown','target':'studio','name':'bad','value':{}})
   finally:core.LITE6_STORE=old
if __name__=='__main__':unittest.main()
