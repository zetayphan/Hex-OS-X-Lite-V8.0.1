import sys,unittest,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'system'))
import core
class WorkflowTests(unittest.TestCase):
 def test_version(self):
  self.assertEqual((core.ROOT/'VERSION').read_text().strip(),'31.1')
 def test_full_workflow(self):
  result=core.full_workflow({})
  self.assertIn(result['status'],('ok','partial'))
  self.assertEqual([x['step'] for x in result['record']['steps']],['nexus','terminal','research','omniverse','studio'])
  self.assertTrue((core.WORK/result['saved']).is_file())
  self.assertEqual(len(result['record']['quantum']['probabilities']),4)
if __name__=='__main__':unittest.main()
