"""
..
   This file is part of the circuits bricks component library.
   Copyright (C) 2012-2015 Michael N. Lipp

.. moduleauthor:: mnl
"""
from circuits_bricks.web.wsgi import WSGIApplication
from circuits.core.manager import Manager
from circuits.web.dispatchers.dispatcher import Dispatcher
from threading import Thread
from circuits.core.debugger import Debugger
from circuits.web.controllers import Controller
from circuits.web.servers import Server
from circuits.web.wsgi import Gateway

class Root(Controller):

    def index(self):
        """Index Request Handler

        Controller(s) expose implicitly methods as request handlers.
        Request Handlers can still be customized by using the ``@expose``
        decorator. For example exposing as a different path.
        """
        return "Hello World! (wsgi)"

# Create singleton application
wsgi_adapter = None

if not wsgi_adapter:
    application = Manager(channel="app")
    Debugger().register(application)
    dispatcher = Dispatcher(channel="app").register(application)
    Root().register(dispatcher)
    wsgi_adapter = WSGIApplication(channel="app").register(application)
    Thread(target=application.run).start()

if __name__ == '__main__':
    server = Server(("0.0.0.0", 8888))
    Gateway({"/": wsgi_adapter}).register(server)
    server.run()
else:
    wsgi_adapter
