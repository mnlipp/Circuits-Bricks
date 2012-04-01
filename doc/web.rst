..
   This file is part of the Circuits Bricks package.
   Copyright (C) 2012 Michael N. Lipp


Web classes
===========

.. toctree::
   :maxdepth: 1

Dispatchers
-----------

It is currently not possible to have more than one web document tree
in a single component hierarchy. The circuits' :class:`VirtualHosts` component
works around this by prefixing every request with an additional path component,
thus associating each host with its own subtree.

In some circumstances this approach is inadequate. The following 
dispatcher provides an alternative that dispatch requests received on their 
channel only to a subset of the controllers in the component hierarchy.

ScopeDispatcher
^^^^^^^^^^^^^^^

The :class:`ScopeDispatcher` dispatches only to components that
have a special kind of channel. As an additional feature, components
need not be derived from :class:`BaseComponent`.


.. autoclass:: circuits_bricks.web.ScopeDispatcher
   :members:

.. autoclass:: circuits_bricks.web.ScopedChannel
   :members:


Filters
-------

.. autoclass:: circuits_bricks.web.LanguagePreferences
   :members:

.. autoclass:: circuits_bricks.web.ThemeSelection
   :members:

   