"""
.. codeauthor: mnl
"""
import unittest

from circuits.web import Controller
from circuits.web import BaseServer

from circuits.core.handlers import handler
from circuits.core.components import BaseComponent
from circuits.core.manager import Manager
from urllib2 import urlopen
from circuits.core.debugger import Debugger
from circuits.web.dispatchers.dispatcher import Dispatcher
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

class PrefixingDispatcher(BaseComponent):
    """Forward to another Dispatcher based on the channel."""

    def __init__(self, channel):
        super(PrefixingDispatcher, self).__init__(channel=channel)

    @handler("request", filter=True, priority=1.0)
    def _on_request(self, event, request, response):
        path = request.path.strip("/")

        path = urljoin("/%s/" % self.channel, path)
        request.path = path

class DummyRoot(Controller):
    
    channel = "/"

    def index(self):
        return "Not used"

class Root1(Controller):

    channel = "/site1"

    def index(self):
        return "Hello from site 1!"

class Root2(Controller):

    channel = "/site2"

    def index(self):
        return "Hello from site 2!"


class Test(unittest.TestCase):


    def testDisps(self):
        manager = Manager()
        Debugger().register(manager)
    
        server1 = BaseServer(("localhost", 8000), channel="site1") 
        server1.register(manager);
        PrefixingDispatcher(channel="site1").register(server1)
        Dispatcher(channel="site1").register(server1)
        Root1().register(manager)
    
        server2 = BaseServer(("localhost", 8001), channel="site2") 
        server2.register(manager);
        PrefixingDispatcher(channel="site2").register(server2)
        Dispatcher(channel="site2").register(server2)
        Root2().register(manager)
   
        DummyRoot().register(manager)
        manager.start()

        f = urlopen(server1.base)
        s = f.read()
        self.assertEqual(s, b"Hello from site 1!")

        f = urlopen(server2.base)
        s = f.read()
        self.assertEqual(s, b"Hello from site 2!")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()