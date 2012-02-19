"""
..
   This file is part of the circuits bricks component library.
   Copyright (C) 2012 Michael N. Lipp

.. moduleauthor:: mnl
"""
from circuits.web.servers import BaseServer
from circuits.web.controllers import BaseController, expose, Controller
from circuits.core.manager import Manager
from unittest import TestCase
from urllib2 import urlopen
from circuits_bricks.web.dispatchers.dispatcher import ScopedChannel,\
    ScopeDispatcher

class Root1(BaseController):

    @expose("index", channel = ScopedChannel("site1", "/"))
    def index(self):
        return "Hello from site 1!"

class Root2(Controller):

    channel = ScopedChannel("site2", "/")

    def index(self):
        return "Hello from site 2!"

class TestScopedServers(TestCase):
    
    def setUp(self):
        self.manager = Manager()
        # Debugger().register(self.manager)
    
        self.server1 = BaseServer(("localhost", 8000), channel="site1") 
        self.server1.register(self.manager);
        ScopeDispatcher(channel="site1").register(self.server1)
        Root1().register(self.manager)
    
        self.server2 = BaseServer(("localhost", 8001), channel="site2") 
        self.server2.register(self.manager);
        ScopeDispatcher(channel="site2").register(self.server2)
        Root2().register(self.manager)
    
        self.manager.start()

    def tearDown(self):
        self.manager.stop()

    def test_access(self):
        f = urlopen(self.server1.base)
        s = f.read()
        self.assertEqual(s, b"Hello from site 1!")

        f = urlopen(self.server2.base)
        s = f.read()
        self.assertEqual(s, b"Hello from site 2!")
