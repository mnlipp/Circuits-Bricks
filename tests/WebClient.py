"""
.. codeauthor: mnl
"""
import unittest
from circuits_bricks.web.client import Client
from circuits.core.manager import Manager
from circuits.web.servers import BaseServer
from circuits.web.controllers import BaseController, expose
from circuits.web.dispatchers.dispatcher import Dispatcher
import time
from circuits.web.client import Request

class Root(BaseController):

    @expose("test")
    def test(self):
        return "Hello!"


class Test(unittest.TestCase):

    def setUp(self):
        self.manager = Manager()
        # Debugger().register(self.manager)
    
        self.server = BaseServer(("localhost", 8123)) 
        self.server.register(self.manager);
        Dispatcher().register(self.server)
        Root().register(self.manager)
        self.manager.start()

    def tearDown(self):
        self.manager.stop()

    def test(self):
        app = Client("http://localhost:8123/hallo", channel="TestClient")
        app.start()
        app.fire(Request("GET", "http://localhost:8123/test"))
        for i in range(100):
            if app.response:
                break
            time.sleep(0.010)
        
        response = app.response
        assert response.status == 200
        assert response.message == "OK"

        s = response.read()
        assert s == b"Hello!"

        app._response = None
        app.fire(Request("GET", "test"))
        for i in range(10000):
            if app.response:
                break
            time.sleep(0.010)
        
        response = app.response
        assert response.status == 200
        assert response.message == "OK"

        s = response.read()
        assert s == b"Hello!"

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()