import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'system'))
import core
class V45Tests(unittest.TestCase):
 def test_reject_unknown(self):
  with self.assertRaises(ValueError):core.v45_execute({'name':'invalid'})
 def test_execute(self):
  result=core.v45_execute({'name':'five-core'})
  self.assertEqual(len(result['steps']),5)
  self.assertTrue((core.WORK/result['saved']).exists())
  self.assertIn(result['status'],('ok','partial'))
if __name__=='__main__':unittest.main()
