"""
..
   This file is part of the circuits bricks component library.
   Copyright (C) 2012 Michael N. Lipp

.. moduleauthor:: mnl
"""
from circuits.core.components import BaseComponent
import os
import logging
from circuits_bricks.app.logger import Logger, log
from circuits_bricks.app.config import Configuration

DEFAULT_CONFIG = {
    "logging": {
        "type": "file",
        "file": os.path.join("%(log_dir)s", "application.log"),
        "level": "DEBUG",
    }
}

class Application(BaseComponent):
    """
    The application component is intended to be used as root component
    of an application. It creates a :class:`circuits_bricks.app.Configuration`
    and a :class:`util.logger.Logger` child component.
    
    The :class``Application`` component creates an application directory 
    (as hidden directory
    in the user's home directory, using the provided application name).
    The configuration is stored as file ``config`` in that directory.
    
    The ``Logger`` is configured as specified by the configuration.
    The default configuration specifies a logger that logs to a 
    file ``application.log`` in the application directory.
    """
    
    channel="application"
    """The component's channel (defaults to ``application``)."""
    
    def __init__(self, name, initial_config=None, defaults={}):
        """
        :param initial_config: the initial configuration past on to
            the constructor of the :class:`Configuration` sub-component
        :param defaults: the defaults passed to
            the constructor of the :class:`Configuration` sub-component
        """
        super(Application, self).__init__()
        self._app_name = name
        
        self._app_dir = defaults.setdefault \
            ('app_dir', os.path.expanduser('~/.%s' % name))
        self._config_dir = defaults.setdefault ('config_dir', self._app_dir)
        self._log_dir = defaults.setdefault('log_dir', self._app_dir)

        if not initial_config:
            initial_config = DEFAULT_CONFIG

        if not os.path.exists(self._app_dir):
            os.makedirs(self._app_dir)
        if not os.path.exists(self._config_dir):
            os.makedirs(self._config_dir)
        self._config = Configuration \
            (os.path.join(self._config_dir, 'config'),
             initial_config, defaults).register(self);

        # Create Logger Component using the values from the configuration
        log_opts = dict()
        for opt in self._config.options("logging"):
            log_opts[opt] = self._config.get("logging", opt)
        logtype = log_opts.get("type", "stderr")
        loglevel = log_opts.get("level", "INFO")
        loglevel = logging.getLevelName(loglevel)
        logfile = log_opts.get("file", None)
        if logfile and not os.path.abspath(logfile):
            logfile = os.path.join(self._config_dir, logfile)
        self._log = Logger(logfile, name, logtype, loglevel,
                           handler_args=log_opts).register(self)
        self.fire(log(logging.INFO, 'Application ' + name + " started"),
                  "logger")

    @property
    def app_dir(self):
        """
        Returns the application specific directory used to store the 
        configuration. May be used by other application components 
        as a place to store additional information.
        """
        return getattr(self, "_app_dir", None)

    @property
    def config(self):
        """
        Returns the configuration sub-component created for this
        application. 
        """
        return getattr(self, "_config", None)
    