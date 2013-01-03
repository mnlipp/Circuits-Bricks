"""
.. codeauthor: mnl
"""
import unittest
from circuits.core.components import Component
from circuits.net.sockets import Write
from circuits.web.controllers import Controller
from circuits.web.servers import Server
from circuits_bricks.web.dispatchers.websockets import WebSockets
from circuits.core.manager import Manager
from circuits_bricks.web.websocket import WebSocketClient
import time
from circuits.core.debugger import Debugger
from circuits.web.client import Connect

class Echo(Component):

    channel = "ws"

    def read(self, sock, data):
        self.fireEvent(Write(sock, "Received: " + data))

class Root(Controller):

    def index(self):
        return "Hello World!"

class WSClient(Component):
    
    response = None
    
    def read(self, data):
        self.response = data

class Test(unittest.TestCase):

    def setUp(self):
        self.manager = Manager()
        # Debugger().register(self.manager)
    
        self.server = Server(("localhost", 8123)).register(self.manager) 
        Echo().register(self.server)
        Root().register(self.server)
        WebSockets("/websocket").register(self.server)
        self.manager.start()

    def tearDown(self):
        self.manager.stop()

    def testEcho(self):
        app = WebSocketClient("ws://localhost:8123/websocket")
        wsclient = WSClient().register(app)
        app.start()
        app.fire(Connect())
        app.fire(Write("Hello!"), "ws")
        for i in range(100):
            if wsclient.response is not None:
                break
            time.sleep(0.010)
        assert wsclient.response is not None
        app.stop()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()