"""
..
   This file is part of the circuits bricks component library.
   Copyright (C) 2012 Michael N. Lipp

.. moduleauthor:: mnl
"""
from circuits.six import text_type
from circuits import Event
from circuits.web.dispatchers.dispatcher import Dispatcher, find_handlers
from circuits.core.handlers import handler
from circuits.web.controllers import BaseController
from circuits.web.utils import parse_qs
from circuits.web.processors import process

class ScopedChannel(object):
    """
    This class provides a combination of a request scope and
    a path for sending web requests to channels.
    
    The default request handling used in circuits matches the
    path of a request against a list of paths assembled from the
    :class:`circuits.web.controllers.BaseController`'s channels.
    This class allows you to specify an additional criterion for matching,
    the scope. The value of the scope must match the channel used by the
    server that received the request.
    
    Note that scoped channels only work in combination with
    :class:`circuits_bricks.web.ScopeDispatcher`.
    """
    
    def __init__(self, scope="web", path="/"):
        """
        :param scope: The scope of the scoped channel
        :param path: The path associated with the channel
        """
        self._scope = scope
        self._path = path
    
    def __eq__(self, other):
        if isinstance(other, ScopedChannel):
            return self._scope == other._scope and self._path == other._path
        return NotImplemented
    
    def __hash__(self):
        return self._scope.__hash__() ^ self._path.__hash__()
    
    def __repr__(self):
        return "ScopedChannel(\"" + self._scope + "\", \"" + self._path + "\")"

    @property
    def scope(self):
        return self._scope
    
    @property
    def path(self):
        return self._path


class ScopeDispatcher(Dispatcher):
    """
    This component provides a dispatcher for requests that are received on
    a specific channel.
    
    The dispatcher forwards requests only to controllers with a 
    :class:`circuits_bricks.web.ScopedChannel` as channel. The scoped
    channel's :attr:`scope` property must match the channel assigned to the
    ``ScopeDispatcher``.
    
    In contrast to the standard :class:`circuits.web.Dispatcher`
    a class doesn't necessarily have to inherit from
    :class:`circuits.web.controllers.BaseController`.
    It may also expose request handling methods using the
    ``@expose`` annotation with keyword parameter `channel` set
    to a scoped channel. Of course, you cannot use the prepared
    response methods that you usually inherit from ``BaseController``
    if you use that mechanism.     
    
    The scope dispatcher does not override the behavior of a standard
    dispatcher, it complements it. If a standard dispatcher component
    is registered in your component hierarchy, it will still grab and
    register the controller components.
    """

    channel = "web"

    def __init__(self, **kwargs):
        """
        The constructor creates a new dispatcher using the given
        parameters. The keyword parameter "channel" should be
        provided.
        """
        super(ScopeDispatcher, self).__init__(**kwargs)

    @handler("registered", channel="*", override=True)
    def _on_registered(self, c, m):
        if not isinstance(c, BaseController):
            return
        for hs in c._handlers.values():
            for h in hs:
                scoped_channel = h.channel or c.channel
                if scoped_channel and isinstance(scoped_channel, ScopedChannel)\
                    and scoped_channel.scope == self.channel:
                    self.paths[scoped_channel.path] = c

    @handler("unregistered", channel="*", override=True)
    def _on_unregistered(self, c, m):
        if not isinstance(c, BaseController):
            return
        for hs in c._handlers.values():
            for h in hs:
                scoped_channel = h.channel or c.channel
                if scoped_channel and isinstance(scoped_channel, ScopedChannel)\
                    and scoped_channel.scope == self.channel:
                    del self.paths[scoped_channel.path]

    @handler("request", priority=0.1, override=True)
    def _on_request(self, event, req, res, peer_cert=None):
        if peer_cert:
            event.peer_cert = peer_cert

        handlers, name, channel, vpath = find_handlers(req, self.paths)
        if isinstance(channel, str) or isinstance(channel, unicode):
            channel = ScopedChannel(self.channel, channel)

        if name is not None and channel is not None:
            event.kwargs = parse_qs(req.qs)
            process(req, event.kwargs)

            if vpath:
                event.args += tuple(vpath)

            if isinstance(name, text_type):
                name = str(name)

            return self.fire(
                Event.create(
                    name, *event.args, **event.kwargs
                ),
                channel
            )
