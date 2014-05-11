__all__ = ['testClass', 'testFunction', 'testModule', 'testModuleClass', 'testModuleFunction']
# Don't modify the line above, or this line!
from autoxinit import autoxinit
autoxinit(__name__, __file__, globals())
del autoxinit




import unittest
from inspect import isclass, isfunction, ismodule

class MyTest(unittest.TestCase):

	def test_importedModule(self):
		self.assertTrue(ismodule(testModule))

	def test_isClassNotModule(self):
		self.assertTrue(isclass(testClass))

	def test_isFunctionNotModule(self):
		self.assertTrue(isfunction(testFunction))

#if __name__ == '__main__': unittest.main()
suite = unittest.TestLoader().loadTestsFromTestCase(MyTest)
unittest.TextTestRunner(verbosity=2).run(suite)
