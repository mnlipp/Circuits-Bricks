"""
..
   This file is part of the circuits bricks component library.
   Copyright (C) 2012 Michael N. Lipp

.. moduleauthor:: mnl
"""
from circuits_bricks.core.timers import Timer
from circuits.core.events import Event
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from errno import ETIMEDOUT
from collections import deque


from circuits.web.headers import Headers
from circuits.core import handler, BaseComponent
from circuits.net.sockets import TCPClient, write, close, connect, SocketError

from circuits.protocols.http import HTTP
from circuits.web.client import parse_url, NotConnected


class request(Event):
    """Request Event

    This Event is used to initiate a new request.

    :param method: HTTP Method (PUT, GET, POST, DELETE)
    :type  method: str

    :param path: Path to resource
    :type  path: str
    """

    def __init__(self, method, path, body=None, headers={}, timeout=None):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(request, self).__init__(method, path, body, headers, timeout)

class Client(BaseComponent):
    """
    This is a variation of the Client class from circuits that
    fixes a problem with channel names and provides a slightly
    simplified interface that doesn't need explicit connect events.
    """

    channel = "web"

    def __init__(self, url, channel=channel, timeout=-1):
        super(Client, self).__init__(channel=channel)
        self._host, self._port, self._resource, self._secure = parse_url(url)

        self._response = None
        self._transport = None
        self._outstanding = 0
        self._pending = deque()
        self._timeout = None
        self._timer = None

    @handler("request")
    def request(self, event, method, url, body=None, headers={}, timeout=None):
        timeout = timeout or self._timeout
        if self._transport == None or not self._transport.connected:
            self._transport = TCPClient(channel=self.channel).register(self)
            HTTP(channel=self.channel).register(self._transport)
            self.fire(connect(self._host, self._port, self._secure),
                      self._transport)
            self._pending.append((method, url, body, headers, timeout))
        else:
            self._send_request(method, url, body, headers, timeout)

    @handler("connected")
    def _on_connected(self, host, port):
        if len(self._pending) > 0:
            args = self._pending.popleft()
            self._send_request(*args)

    @handler("disconnected")
    def _on_disconnected(self):
        if len(self._pending) > 0:
            self.fire(connect(self._host, self._port, self._secure),
                      self._transport)

    def _send_request(self, method, url, body=None, headers=None, timeout=None):
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
        if headers is None:
            headers = Headers([])
        else:
            headers = Headers([(k, v) for k, v in headers.items()])
        # Clients MUST include Host header in HTTP/1.1 requests (RFC 2616)
        if not headers.has_key("Host"):
            headers["Host"] = self._host \
                + (":" + str(self._port)) if self._port else ""
        command = "%s %s HTTP/1.1" % (method, resource)
        if body is not None:
            headers["Content-Length"] = len(body)
        message = "%s\r\n%s" % (command, headers)
        self._outstanding += 1
        if timeout is not None:
            self._timer = Timer(timeout, SocketError(ETIMEDOUT), self.channel) \
                .register(self)
        self.fire(write(message.encode('utf-8')), self._transport)
        if body is not None:
            self.fire(write(body), self._transport)

    def _clear_timer(self):
        if self._timer is not None:
            self._timer.unregister()
            self._timer = None

    @handler("response")
    def _on_response(self, response):
        self._response = response
        self._outstanding -= 1
        self._clear_timer()
        if response.headers.get("Connection") == "Close":
            self.fire(close(), self._transport)

    @handler("close")
    def close(self):
        self._clear_timer()
        if self._transport.connected:
            self.fire(close(), self._transport)

    @property
    def connected(self):
        return getattr(self._transport, "connected", False) \
            if hasattr(self, "_transport") else False

    @property
    def response(self):
        return getattr(self, "_response", None)
