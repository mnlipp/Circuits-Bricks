"""
..
   This file is part of the circuits bricks component library.
   Copyright (C) 2012 Michael N. Lipp
   
   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.
   
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.

.. moduleauthor:: mnl
"""
from circuits.core.debugger import Debugger
from circuits.core.components import Component
import sys
from circuits.web.servers import BaseServer
import os
from circuits_bricks.mipypo import Portal
from circuits_bricks.application import Application
from circuits_bricks.mipypo.portlets.helloworld import HelloWorldPortlet

CONFIG = {
    "logging": {
        "type": "TimedRotatingFile",
        "file": os.path.join("%(log_dir)s", "application.log"),
        "when": "midnight",
        "backupCount": 7,
        "level": "DEBUG",
    },
    "ui": {
        "port": "8123",
    },
}

class ErrorHandler(Component):
    def exception(self, error_type, value, traceback, handler=None):
        sys.exit();

if __name__ == '__main__':

    application = Application("TestPortal", CONFIG)
    Debugger().register(application)
    ErrorHandler().register(application)
    # Build a web (HTTP) server for handling user interface requests.
    port = int(application.config.get("ui", "port", 0))
    portal_server = BaseServer(("", port), channel="ui").register(application)
    Portal(portal_server).register(application)
    HelloWorldPortlet().register(application)
    
    from circuits.tools import graph
    print graph(application)
    application.run()
