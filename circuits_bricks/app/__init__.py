"""
..
   This file is part of the circuits bricks component library.
   Copyright (C) 2012 Michael N. Lipp

.. moduleauthor:: mnl

This module provides variations of some base application components
shipped with circuits.

The new :class:`circuits_bricks.app.Logger` component provides some
additional logging types and more options for configuring the logging.
The added :class:`circuits_bricks.app.LogSupport` class supports
logging to the logger component without using the event mechanism.

The :class:`circuits_bricks.app.Configuration` component takes a
different approach to configuration. The configuration values read
initially are sent to the components on startup, and events that
signal changes to the configuration are automatically persisted.

The :class:`circuits_bricks.app.Application` component combines
the aforementioned components and their configuration for an easy
application setup including configuration and logging.

"""
from .application import *
from .config import *
from .logger import *

