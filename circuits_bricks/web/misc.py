"""
..
   This file is part of the circuits bricks component library.
   Copyright (C) 2012-2015 Michael N. Lipp

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

    @handler("request", priority=9)
    # Priority must be less than Sessions' priority
    def _on_request(self, event, request, response, peer_cert=None):
        self.update(request)
        
    @classmethod
    def update(cls, request):
        """
        Return the language preferences as derived from the request
        and (possibly) a cookie and the preference stored in the session.
        """
        session = getattr(request, "session")
        # Highest priority: override setting from session
        if not session is None:
            langs = session.get(cls._SESSION_KEY + ".overridden")
            if not langs is None:
                return langs
        # Next try cookie
        from_cookie =  None # [when #135 is fixed:] request.cookie.get(cls._SESSION_KEY)
        if from_cookie:
            langs = from_cookie.value.split(":")
        else:
            # Next, try accept header
            langdefs = request.headers.get("Accept-Language", "en")
            if cls._cache.has_key(langdefs):
                langs = cls._cache[langdefs]
            else:
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
                langs = [value for _, value in defslist]
                cls._cache[langdefs] = langs
        if not session is None:
            session[cls._SESSION_KEY + ".cached"] = langs
        return langs
    
    @classmethod
    def override_accept(cls, session, languages, response=None):
        """
        Set the language preferences for the given session, thus overriding
        the preferences given in the HTTP header.
        
        :param session: the session. 
        :param languages: a list of language identifiers.
        :param response: if not None, the preference will also be
                saved as a cookie.
        """
        if not isinstance(languages, list):
            languages = [languages]
        session[cls._SESSION_KEY + ".overridden"] = languages
        if not response is None:
            pass # [when #135 is fixed:] response.cookie[cls._SESSION_KEY] = ":".join(languages)
 
    @classmethod
    def preferred(cls, session):
        return session.get(cls._SESSION_KEY + ".overridden") \
            or session.get(cls._SESSION_KEY + ".cached")


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
