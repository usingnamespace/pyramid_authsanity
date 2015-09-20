from zope.interface import implementer

from .interfaces (
        IAuthSourceService,
        )

@implementer(IAuthSourceService)
class SessionAuthSource(object):
    """ An authentication source that uses the current session """

    vary = ()
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
