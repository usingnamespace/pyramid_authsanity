import base64
import os

from pyramid.interfaces import (
    IAuthenticationPolicy,
    IDebugLogger,
    )

from pyramid.security import (
    Authenticated,
    Everyone,
    )

from .interfaces import (
        IAuthSourceService,
        IAuthService,
        )

from .util import (
        add_vary_callback,
        _find_services,
        )

from zope.interface import implementer

NoAuthCompleted = object()

def _clean_principal(princid):
    """ Utility function that cleans up the passed in principal
    This can easily also be extended for example to make sure that certain
    usernames are automatically off-limits.
    """
    if princid in (Authenticated, Everyone):
        princid = None
    return princid

@implementer(IAuthenticationPolicy)
class AuthServicePolicy(object):
    def _log(self, msg, methodname, request):
        logger = request.registry.queryUtility(IDebugLogger)
        if logger:
            cls = self.__class__
            classname = cls.__module__ + '.' + cls.__name__
            methodname = classname + '.' + methodname
            logger.debug(methodname + ': ' + msg)

    _find_services = staticmethod(_find_services) # Testing

    def __init__(self, debug=False):
        self.debug = debug

    def unauthenticated_userid(self, request):
        """ We do not allow the unauthenticated userid to be used. """

    def authenticated_userid(self, request):
        """ Returns the authenticated userid for this request. """
        debug = self.debug

        (sourcesvc, authsvc) = self._find_services(request)
        request.add_response_callback(add_vary_callback(sourcesvc.vary))

        userid = authsvc.userid()

        if userid is NoAuthCompleted:
            debug and self._log('authentication has not yet been completed',
                    'authenticated_userid', request)
            (principal, ticket) = sourcesvc.get_value()

            debug and self._log(
                'source service provided information: (principal: %r, ticket: %r)'
                % (principal, ticket), 'authenticated_userid', request)

            # Verify the principal and the ticket, even if None
            authsvc.verify_ticket(principal, ticket)
            # This should now return None
            userid = authsvc.userid()

            if userid is NoAuthCompleted:
                userid = None

        debug and self._log('authenticated_userid returning: %r' % (userid,),
                'authenticated_userid', request)

        return userid

    def effective_principals(self, request):
        """ A list of effective principals derived from request. """
        debug = self.debug
        effective_principals = [Everyone]

        userid = self.authenticated_userid(request)
        (_, authsvc) = self._find_services(request)

        if userid is None:
            debug and self._log(
                'authenticated_userid returned %r; returning %r' % (
                    userid, effective_principals),
                'effective_principals',
                request
                )
            return effective_principals

        if _clean_principal(userid) is None:
            debug and self._log(
                ('authenticated_userid returned disallowed %r; returning %r '
                 'as if it was None' % (userid, effective_principals)),
                'effective_principals',
                request
                )
            return effective_principals

        effective_principals.append(Authenticated)
        effective_principals.append(userid)
        effective_principals.extend(authsvc.groups())

        debug and self._log(
            'returning effective principals: %r' % (
                effective_principals,),
            'effective_principals',
            request
        )
        return effective_principals

    def remember(self, request, principal, **kw):
        """ Returns a list of headers that are to be set from the source service. """
        debug = self.debug

        (sourcesvc, authsvc) = self._find_services(request)

        request.add_response_callback(add_vary_callback(sourcesvc.vary))

        value = {}
        value['principal'] = principal
        value['ticket'] = ticket = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b"=")

        debug and self._log('Remember principal: %r, ticket: %r' % (principal, ticket), 'remember', request)

        authsvc.add_ticket(principal, ticket)

        return sourcesvc.headers_remember(value)

    def forget(self, request):
        """ A list of headers which will delete appropriate cookies."""
        debug = self.debug

        (sourcesvc, authsvc) = self._find_services(request)

        request.add_response_callback(add_vary_callback(sourcesvc.vary))

        (_, ticket) = sourcesvc.get_value()
        authsvc.remove_ticket(ticket)

        return sourcesvc.headers_forget()

