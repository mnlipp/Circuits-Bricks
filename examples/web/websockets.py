#!/usr/bin/env python

from circuits import Component
from circuits_bricks.web.dispatchers import WebSockets
from circuits.web import Server, Controller, Logger
from circuits.net.sockets import write
from circuits.core.debugger import Debugger


class Echo(Component):

    channel = "ws"

    def read(self, sock, data):
        self.fireEvent(write(sock, "Received: " + data))


class Root(Controller):

    def index(self):
        return "Hello World!"

(Server(("0.0.0.0", 8000))
        + Echo()
        + Root()
        + Logger()
        + WebSockets("/websocket")
        + Debugger()
).run()
