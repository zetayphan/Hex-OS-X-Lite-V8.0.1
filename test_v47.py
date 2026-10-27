import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from system.core import v47_assist,v47_resource_snapshot,v47_workflow
class V47Tests(unittest.TestCase):
 def test_helper(self):
  self.assertFalse(v47_assist({'prompt':'How do I use workflows?'})['model_connected'])
 def test_resources(self):
  self.assertIn('pid',v47_resource_snapshot())
 def test_reject_unapproved(self):
  with self.assertRaises(ValueError):v47_workflow({'steps':[{'module':'terminal','action':'hexlang'}]})
if __name__=='__main__':unittest.main()
