"""
..
   This file is part of the circuits bricks component library.
   Copyright (C) 2012 Michael N. Lipp

.. moduleauthor:: mnl
"""
from circuits.core.components import BaseComponent
from circuits.core.handlers import handler

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
    """
    
    channel = "web"

    _SESSION_KEY = "circuits_bricks.web.LanguagePreferences"

    _cache = dict()

    @classmethod
    def preferred(cls, request):
        """
        Return the language preferences as derived from the request
        and the preference stored in the session.
        """
        langs = None
        session = getattr(request, "session", None)
        if session:
            langs = session.get(cls._SESSION_KEY, None)
        if not langs:
            langdefs = request.headers.get("Accept-Language", "en")
            if cls._cache.has_key(langdefs):
                langs = cls._cache[langdefs]
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
            cls._cache[langdefs] = langs
        return langs
    
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


class ThemeSelection(BaseComponent):
    """
    This is just a small wrapper for handling the theme selection
    in the session.
    """

    channel = "web"

    _THEME_KEY = "circuits_bricks.web.ThemeSelection"
    _default_theme = "default"

    @classmethod
    def set_default(cls, theme):
        cls._default_theme = theme

    @classmethod
    def selected(cls, session):
        """
        Return the selected theme.
        """
        return session.get(cls._THEME_KEY, cls._default_theme)

    @classmethod
    def select(cls, session, theme):
        """
        Select the theme for the given session.
        """
        session[cls._THEME_KEY] = theme
        cls._thread_data.theme = theme
