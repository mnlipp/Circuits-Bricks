"""
..
   This file is part of the circuits bricks component library.
   Copyright (C) 2012 Michael N. Lipp

.. moduleauthor:: mnl
"""
from circuits.core.handlers import handler
from circuits.core.components import BaseComponent
from circuits.core.events import Event
import os

try:
    from configparser import ConfigParser, SafeConfigParser
except ImportError:
    from ConfigParser import ConfigParser, SafeConfigParser


class config_value(Event):
    """
    This event informs about the change of a configuration value.
    The events are sent to channel ``configuration``, so every
    component interested in the events should have a handler that
    listens on this channel.
    """
    
    channels = ("configuration",)
    
    def __init__(self, section, option, value):
        """
        The constructor initializes a new instance with the given
        parameters
        
        :param section: the section the configuration value belongs to
        :type section: string
        :param option: the name of the configuration value that has changed
        :type option: string
        :param value: the new value
        :type value: string 
        """
        super(config_value, self).__init__(section, option, value)

class emit_config(Event):
    """
    This event causes the :class:`Configuration` to emit the configuration
    values.
    """
    channels = ("configuration",)
    """
    The event is delivered on the ``configuration`` channel.
    """
    def __init__(self, *args, **kwargs):
        super(Event, self).__init__(*args, **kwargs)


class Configuration(BaseComponent):
    """
    This component provides a repository for configuration values.
    
    The component reads the initial configuration values from an
    ini-style configuration file when created. During application bootstrap,
    it intercepts the ``started`` event with a filter with  priority 999999.
    After receiving the ``started`` event, it fires all known configuration 
    values on the ``configuration`` channel as :class:`config_value` events.
    Then, it re-fires the intercepted started event.
     
    Components that depend on configuration values define handlers
    for ``config_value`` events on the ``configuration`` channel 
    and adapt themselves to the values propagated. Note that 
    due to the intercepted ``started`` event, the initial
    configuration events are received before the ``startup`` event, so
    components' configurations can be rearranged before they actually
    start doing something.
 
    Besides initially publishing the stored configuration values,
    :class:`Configuration` listens for :class:`config_value` events
    fired by other components, merges them with the already existing 
    configuration values and saves any changes to the configuration file.

    Other components that are capable of adjusting themselves to changed
    configuration values should, of course, continue to listen for
    :class:`config_value` events and adapt their behavior to the
    changed configuration if possible.
    
    If your application requires a different startup behavior, you 
    can also fire an :class:`emit_config` event or call
    method :meth:`emit_values`. This causes the 
    :class:`Configuration` to emit the configuration values 
    immediately. If this event is received before the ``started`` event, 
    the ``started`` event will not be intercepted.    
    """
    
    channel = "configuration"
    
    def __init__(self, filename, initial_config=None, 
                 defaults=None, channel=channel):
        """
        The constructor creates a new configuration using the given
        parameters.
        
        :param filename: the name of the file that is used to store the
                         configuration. If the file does not exist
                         it will be created.
        :type filename: string
        :param initial_config: a dict of name/section pairs, each section being
                               a dict of option/value pairs that is used
                               to initialize the configuration if no existing
                               configuration file is found
        :type initial_config: dict of dicts
        :param defaults: defaults passed to to the :class:`ConfigParser`
        :param channel: the channel to be used by this :class:`Configuration`
                        (defaults to "configuration")
        """
        super(Configuration, self).__init__(channel=channel)
        self._emit_done = False

        self._filename = filename
        self._config = SafeConfigParser(defaults=defaults)
        self._config.optionxform = str
        if os.path.exists(filename):
            self._config.read(filename)
        modified = False
        for section in initial_config:
            if not self._config.has_section(section):
                self._config.add_section(section)
                for option, value in initial_config[section].items():
                    if not self._config.has_option(section, option):
                        self._config.set(section, option, str(value))
                        modified = True
        if modified:
            with open(filename, "w") as f:
                self._config.write(f)

    def emit_values(self):
        """
        Fire all known configuration values as :class:`config_value`
        events.
        """
        for section in self._config.sections():
            for option in self._config.options(section):
                self.fire(config_value
                          (section, option, self._config.get(section, option)))
        self._emit_done = True

    @handler("emit_config")
    def _on_emit_config(self):
        self.emit_values()

    @handler("started", channel="*", filter=True, priority=999999)
    def _on_started(self, event, component):
        if not self._emit_done:
            self.emit_values()
            self.fire(event, *event.channels)
            return event.value

    @handler("config_value")
    def _on_config_value(self, section, option, value):
        if self._config.has_option(section, option):
            if self._config.get(section, option) == str(value):
                return
        if not self._config.has_section(section):
            self._config.add_section(section)
        self._config.set(section, option, str(value))
        with open(self._filename, "w") as f:
            self._config.write(f)

    def options(self, section):
        return self._config.options(section)

    def get(self, section, option, default=None):
        if self._config.has_option(section, option):
            return self._config.get(section, option)
        else:
            return default
