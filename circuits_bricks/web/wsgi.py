"""
..
   This file is part of the circuits bricks component library.
   Copyright (C) 2012-2015 Michael N. Lipp

.. moduleauthor:: mnl
"""
from circuits.web.events import request
from circuits.core.handlers import handler
from threading import Semaphore
from circuits.web.wsgi import Application
from circuits.web.http import HTTP

class WSGIApplication(Application):

    class Result(object):
        pass

    channel = "web"

    def __init__(self, channel="web"):
        self.channel = channel
        super(WSGIApplication, self).__init__()
        
    def init(self):
        HTTP(self, channel=self.channel).register(self)

    def __call__(self, environ, start_response, exc_info=None):
        req, res = self.getRequestResponse(environ)
        evt = request(req, res)
        sync = res.sync = self.Result() 
        sync.semaphore = Semaphore(0)
        self.fire(evt)
        sync.semaphore.acquire()

        status, headers, body = sync.result
        start_response(str(status), headers, exc_info)
        return body

    @handler("response", priority=1)
    def _on_response(self, event, response):
        if not hasattr(response, "sync"):
            pass
        
        response.prepare()
        headers = [(k, v if isinstance(v, str) else str(v)) \
                    for k, v in response.headers.items()]
#         if response.status == 302:
#             response.body = ""
        response.sync.result = (response.status, headers, response.body)
        response.sync.semaphore.release()
        event.stop()

