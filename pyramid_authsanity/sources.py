from webob.cookies import (
        SignedCookieProfile,
        SignedSerializer,
        )

from zope.interface import implementer

from .interfaces import (
        IAuthSourceService,
        )

def SessionAuthSourceFactory():
    """ An authentication source that uses the current session """
    return SessionAuthSource

@implementer(IAuthSourceService)
class SessionAuthSource(object):
    """ An authentication source that uses the current session """

    vary = []
    value_key = 'sanity.value'

    def __init__(self, context, request):
        self.request = request
        self.session = request.session

        return self

    def get_value(self):
        return self.session.get(value_key, [None, None])

    def headers_remember(self, value):
        self.session[value_key] = value
        return []

    def headers_forget(self):
        if value_key in self.session:
            del self.session[value_key]
        return []


def CookieAuthSourceFactory(
         secret,
         cookie_name='auth',
         secure=False,
         max_age=None,
         httponly=False,
         path="/",
         domains=None,
         timeout=None,
         reissue_time=None,
         debug=False,
         hashalg='sha512',
        ):
    """ An authentication source that uses a unique cookie """

    @implementer(IAuthSourceService)
    class CookieAuthSource(object):

        vary = ['Cookie']

        def __init__(self, context, request):
            self.domains = domains

            if self.domains is None:
                self.domains = []
                self.domains.append(request.domain)

            self.cookie = SignedCookieProfile(
                            secret,
                            'authsanity',
                            cookie_name,
                            secure=secure,
                            max_age=max_age,
                            httponly=httponly,
                            path=path,
                            domains=domains,
                            hashalg=hashalg,
                            )
            # Bind the cookie to the current request
            self.cookie = self.cookie.bind(request)

            return self

        def get_value(self):
            return self.cookie.get_value()

        def headers_remember(self, value):
            return self.cookie.get_headers(value, domains=self.domains)

        def headers_forget(self):
            return self.cookie.get_headers('', max_age=0)

    return CookieAuthSource

