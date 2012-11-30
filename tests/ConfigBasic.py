"""
.. codeauthor: mnl
"""
import unittest
from circuits_bricks.app.application import Application
from circuits.core.components import BaseComponent
from circuits.core.handlers import handler
from tests.helpers import wait_for

class ConfiguredComponent(BaseComponent):
    
    value = "No"
    
    @handler("config_value", channel="configuration")
    def _on_config_value(self, section, option, value):
        if section == "configured-component":
            if option == "value":
                self.value = value

class Test(unittest.TestCase):

    def setUp(self):
        self._application = Application("BasicConfigTest")
        self._application.config._on_config_value\
            ("configured-component", "value", "Yes")
        self._conf_comp = ConfiguredComponent().register(self._application)
        self._application.start()

    def tearDown(self):
        self._application.stop()

    def testName(self):
        wait_for(self._conf_comp, "value", "Yes")
        self.assertEqual(self._conf_comp.value, "Yes")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()