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

from .util import (
    add_vary_callback,
    _find_services,
    _session_registered,
    )

from zope.interface import implementer


def _clean_principal(princid):
    """ Utility function that cleans up the passed in principal
    This can easily also be extended for example to make sure that certain
    usernames are automatically off-limits.
    """
    if princid in (Authenticated, Everyone):
        princid = None
    return princid


_marker = object()


@implementer(IAuthenticationPolicy)
class AuthServicePolicy(object):
    def _log(self, msg, methodname, request):
        logger = request.registry.queryUtility(IDebugLogger)
        if logger:
            cls = self.__class__
            classname = cls.__module__ + '.' + cls.__name__
            methodname = classname + '.' + methodname
            logger.debug(methodname + ': ' + msg)

    _find_services = staticmethod(_find_services)  # Testing
    _session_registered = staticmethod(_session_registered)  # Testing
    _have_session = _marker

    def __init__(self, debug=False):
        self.debug = debug

    def unauthenticated_userid(self, request):
        """ We do not allow the unauthenticated userid to be used. """

    def authenticated_userid(self, request):
        """ Returns the authenticated userid for this request. """
        debug = self.debug

        (sourcesvc, authsvc) = self._find_services(request)
        request.add_response_callback(add_vary_callback(sourcesvc.vary))

        try:
            userid = authsvc.userid()
        except Exception:
            debug and self._log(
                'authentication has not yet been completed',
                'authenticated_userid',
                request
            )
            (principal, ticket) = sourcesvc.get_value()

            debug and self._log(
                'source service provided information: (principal: %r, ticket: %r)'
                % (principal, ticket), 'authenticated_userid', request)

            # Verify the principal and the ticket, even if None
            authsvc.verify_ticket(principal, ticket)

            try:
                # This should now return None or the userid
                userid = authsvc.userid()
            except Exception:
                userid = None

        debug and self._log(
            'authenticated_userid returning: %r' % (userid,),
            'authenticated_userid',
            request
        )

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

        if self._have_session is _marker:
            self._have_session = self._session_registered(request)

        prev_userid = self.authenticated_userid(request)

        (sourcesvc, authsvc) = self._find_services(request)

        request.add_response_callback(add_vary_callback(sourcesvc.vary))

        value = {}
        value['principal'] = principal
        value['ticket'] = ticket = (
            base64.urlsafe_b64encode(
                os.urandom(32)
            ).
            rstrip(b"=").
            decode('ascii')
        )

        debug and self._log(
            'Remember principal: %r, ticket: %r' % (principal, ticket),
            'remember',
            request
        )

        authsvc.add_ticket(principal, ticket)

        # Clear the previous session
        if self._have_session:
            if prev_userid != principal:
                request.session.invalidate()
            else:
                # We are logging in the same user that is already logged in, we
                # still want to generate a new session, but we can keep the
                # existing data
                data = dict(request.session.items())
                request.session.invalidate()
                request.session.update(data)
                request.session.new_csrf_token()

        return sourcesvc.headers_remember([principal, ticket])

    def forget(self, request):
        """ A list of headers which will delete appropriate cookies."""
        debug = self.debug

        if self._have_session is _marker:
            self._have_session = self._session_registered(request)

        (sourcesvc, authsvc) = self._find_services(request)

        request.add_response_callback(add_vary_callback(sourcesvc.vary))

        (_, ticket) = sourcesvc.get_value()

        debug and self._log('Forgetting ticket: %r' % (ticket,), 'forget', request)
        authsvc.remove_ticket(ticket)

        # Clear the session by invalidating it
        if self._have_session:
            request.session.invalidate()

        return sourcesvc.headers_forget()
