"""
.. codeauthor: mnl
"""
import unittest
from datetime import datetime, timedelta
from circuits.core.events import Event
from circuits.core.components import Component
from circuits_bricks.core.timers import Timer
from tests.helpers import wait_for

class Test(Event):
    """Test Event"""

class App(Component):

    flag = False

    def reset(self):
        self.flag = False

    def test(self):
        self.flag = True


class TimerTest(unittest.TestCase):

    def setUp(self):
        self.app = App()
        self.app.start()

    def tearDown(self):
        self.app.stop()

    def test_basic(self):
        timer = Timer(0.1, Test(), "timer")
        timer.register(self.app)
        wait_for(self.app, "flag")
        self.app.reset()

    def test_persistent(self):
        timer = Timer(0.1, Test(), "timer", persist=True)
        timer.register(self.app)

        for _ in range(2):
            wait_for(self.app, "flag")
            self.app.reset()

        timer.unregister()
        
    def test_datetime(self):
        now = datetime.now()
        d = now + timedelta(seconds=0.1)
        timer = Timer(d, Test(), "timer")
        timer.register(self.app)
        wait_for(self.app, "flag")
        self.app.reset()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()