import unittest
from system.core import v46_session, MODULES
class V46Tests(unittest.TestCase):
 def test_modules(self):self.assertEqual(len(MODULES),5)
 def test_session(self):self.assertIsInstance(v46_session(),dict)
if __name__=='__main__':unittest.main()
