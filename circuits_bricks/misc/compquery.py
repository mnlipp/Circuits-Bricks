"""
..
   This file is part of the circuits bricks component library.
   Copyright (C) 2012 Michael N. Lipp

.. moduleauthor:: mnl
"""
from circuits.core.events import Event
from circuits.core.handlers import handler

class component_query(Event):
    
    channels = ("component_query")
    
    def __init__(self, query_function, **kwargs):
        super(component_query, self).__init__()
        self._query_function = query_function

    def decide(self, component):
        try:
            if self._query_function(component):
                return component
            else:
                return None
        except:
            return None

class Queryable(object):
    
    @handler("component_query")
    def _on_component_query(self, event):
        return event.decide(self)
