"""
..
   This file is part of the circuits bricks component library.
   Copyright (C) 2012 Michael N. Lipp

.. moduleauthor:: mnl
"""
from circuits.core.components import BaseComponent
from circuits.core.handlers import handler
import threading

class LanguagePreferences(BaseComponent):
    """
    Handling language preferences can be a bit tricky in a web application.
    In general, the preferred language can be derived from the 
    "Accept-Language" header
    in the HTTP request. But sometimes the user wants to override that
    information and use a session specific setting (which in turn
    might be initialized from the user's account settings, but this
    is beyond the scope of this class). So language preferences
    have to be derived from both the HTTP header and the session information.
    
    To make things worse, adding the derived language preference to the
    request isn't sufficient when you use the approach to
    internationalization that is common in Python, i.e. putting the
    text to be localized in "_()". If you want to do that in a web
    server context, the information about the preferred language must
    be available globally (not just as property of the current request
    object), so that it can be accessed by whatever
    function you bind "_" to, and it must be maintained in a thread
    specific way, because your server may handle several requests
    concurrently. 
    
    This class filters the requests and derives the language preferences
    from the HTTP headers and the session information. The information
    is kept in thread local storage and can be accessed with the
    class method :meth:`preferred`.
    """
    
    channel = "web"

    _SESSION_KEY = "circuits_bricks.web.LanguagePreferences"

    _cache = dict()
    _thread_data = threading.local()

    @handler("request", filter=True, priority=9)
    # Priority must be less than Sessions' priority
    def _on_request(self, event, request, response, peer_cert=None):
        langs = None
        session = getattr(request, "session", None)
        if session:
            langs = session.get(self._SESSION_KEY, None)
        if not langs:
            langdefs = request.headers.get("Accept-Language", "en")
            if self._cache.has_key(langdefs):
                langs = self._cache[langdefs]
        if not langs:
            defs = dict()
            for langdef in langdefs.split(","):
                langparts = langdef.split(";", 1)
                lang = langparts[0].replace("-", "_")
                q = 1
                if len(langparts) > 1:
                    qparts = langparts[1].split("=")
                    q = float(qparts[1])
                defs[q] = lang
            defslist = defs.items()
            defslist.sort(reverse=True)
            langs = [value for key, value in defslist]
            self._cache[langdefs] = langs
        self._thread_data.langs = langs

    @classmethod
    def preferred(cls):
        """
        Return the language preferences as derived from the latest intercepted
        request.
        """
        return getattr(cls._thread_data, "langs", ["en"])
    
    @classmethod
    def override_accept(cls, session, languages):
        """
        Set the language preferences for the given session, thus overriding
        the preferences given in the HTTP header.
        
        :param session: the session.
        :param languages: a list of language identifiers.
        """
        if not isinstance(languages, list):
            languages = [languages]
        session[cls._SESSION_KEY] = languages
        cls._thread_data.langs = languages


class ThemeSelection(BaseComponent):
    """
    Localization may sometimes be dependent on the selected theme. In order
    to support the "_()" approach to localization
    (see :class:`circuits_bricks.web.LanguagePreferences`) the selected
    theme must therefore also be available as a global but thread local
    information.
    
    This class filters the theme setting from the session information
    associated with a request and makes it available.
    """

    channel = "web"

    _THEME_KEY = "circuits_bricks.web.ThemeSelection"
    _thread_data = threading.local()

    def __init__(self, *args, **kwargs):
        super(ThemeSelection, self).__init__(*args, **kwargs)
        self._default_theme = kwargs.get("default", "default")

    @handler("request", filter=True, priority=9)
    # Priority must be less than Sessions' priority
    def _on_request(self, event, request, response, peer_cert=None):
        session = getattr(request, "session", None)
        if session:
            self._thread_data.theme \
                = session.get(self._THEME_KEY, self._default_theme)
        else:
            self._thread_data.theme = self._default_theme

    @classmethod
    def selected(cls):
        """
        Return the selected theme.
        """
        return getattr(cls._thread_data, "theme", "default")

    @classmethod
    def select(cls, session, theme):
        """
        Select the theme for the given session.
        """
        session[cls._THEME_KEY] = theme
        cls._thread_data.theme = theme
        