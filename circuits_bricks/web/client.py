"""
..
   This file is part of the circuits bricks component library.
   Copyright (C) 2012 Michael N. Lipp

.. moduleauthor:: mnl
"""
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from socket import error as SocketError
from errno import ECONNRESET


from circuits.web.headers import Headers
from circuits.core import handler, BaseComponent
from circuits.net.sockets import TCPClient, Write, Close, Connect

from circuits.net.protocols.http import HTTP
from circuits.web.client import parse_url, NotConnected


class Client(BaseComponent):
    """
    This is a variation of the Client class from circuits that
    fixes a problem with channel names and provides a slightly
    simplified interface that doesn't need explicit connect events.
    """

    channel = "web"

    def __init__(self, url, channel=channel):
        super(Client, self).__init__(channel=channel)
        self._host, self._port, self._resource, self._secure = parse_url(url)

        self._response = None
        self._transport = None
        self._pending = 0

    @handler("request")
    def request(self, method, url, body=None, headers={}):
        if self._transport == None or not self._transport.connected:
            self._transport = TCPClient(channel=self.channel).register(self)
            HTTP(channel=self.channel).register(self._transport)
            self.fire(Connect(self._host, self._port, self._secure),
                      self._transport)
        p = urlparse(url)
        if p.hostname and p.hostname != self._host \
            or p.scheme == "http" and self._secure \
            or p.scheme == "https" and not self._secure \
            or p.port and p.port != self._port:
            self.fire(NotConnected())
            return

        resource = p.path
        if p.query:
            resource += "?" + p.query
        headers = Headers([(k, v) for k, v in headers.items()])
        # Clients MUST include Host header in HTTP/1.1 requests (RFC 2616)
        if not headers.has_key("Host"):
            headers["Host"] = self._host \
                + (":" + str(self._port)) if self._port else ""
        command = "%s %s HTTP/1.1" % (method, resource)
        message = "%s\r\n%s" % (command, headers)
        self._pending += 1
        self.fire(Write(message.encode('utf-8')), self._transport)
        if body:
            self.fire(Write(body), self._transport)

    @handler("response")
    def _on_response(self, response):
        self._response = response
        self._pending -= 1
        if response.headers.get("Connection") == "Close":
            self.fire(Close(), self._transport)

    @handler("error", filter=True, priority=10)
    def _on_error(self, error):
        # For HTTP 1.1 we leave the connection open. If the peer closes
        # it after some time and we have no pending request, that's OK.
        if isinstance(error, SocketError) and error.args[0] == ECONNRESET \
            and self._pending == 0:
            return True

    def close(self):
        if self._transport != None:
            self._transport.close()

    @property
    def connected(self):
        return getattr(self._transport, "connected", False) \
            if hasattr(self, "_transport") else False

    @property
    def response(self):
        return getattr(self, "_response", None)
