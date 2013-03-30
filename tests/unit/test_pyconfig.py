'''
Created on Nov 30, 2011

@author: ppa
'''
import unittest
from ultrafinance.ufConfig.pyConfig import PyConfig

class testPyConfig(unittest.TestCase):
    def setUp(self):
        self.config = PyConfig()
        self.config.setSource("test.ini")

    def tearDown(self):
        pass

    def testGetSession(self):
        keyValues = self.config.getSection("app_main")
        self.assertNotEqual(0, len(keyValues))

    def testGetOption(self):
        option = self.config.getOption("log", "file")
        self.assertEqual("test.log", option)
