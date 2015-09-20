import logging
log = logging.getLogger(__name__)

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

from webob.cookies (
        SignedCookieProfile,
        SignedSerializer,
        )

from zope.interface import implementer

@implementer(IAuthenticationPolicy)
class AuthServicePolicy(object):
    debug = False

    def _log(self, msg, methodname, request):
        logger = request.registry.queryUtility(IDebugLogger)
        if logger:
            cls = self.__class__
            classname = cls.__module__ + '.' + cls.__name__
            methodname = classname + '.' + methodname
            logger.debug(methodname + ': ' + msg)

    def __init__(debug=False):
        self.debug = debug

    def unauthenticated_userid(self, request):
        """ We do not allow the unauthenticated userid to be used. """

    def authenticated_userid(self, request):









    def effective_principals(self, request):
        """ A list of effective principals derived from request.

        This will return a list of principals including, at least,
        :data:`pyramid.security.Everyone`. If there is no authenticated
        userid, or the ``callback`` returns ``None``, this will be the
        only principal:

        .. code-block:: python

            return [Everyone]

        """
        debug = self.debug
        effective_principals = [Everyone]
        userid = self.authenticated_userid(request)

        if userid is None:
            debug and self._log(
                'authenticated_userid returned %r; returning %r' % (
                    userid, effective_principals),
                'effective_principals',
                request
                )
            return effective_principals

        groups = []

        # Get the groups here ...

        effective_principals.append(Authenticated)
        effective_principals.append(userid)
        effective_principals.extend(groups)

        debug and self._log(
            'returning effective principals: %r' % (
                effective_principals,),
            'effective_principals',
            request
             )
        return effective_principals

    def remember(self, request, principal, **kw):
        debug = self.debug


        value = {}
        value['principal'] = principal
        value['ticket'] = ticket = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b"=")

        debug and self._log('Remember principal: %r, ticket: %r' % (principal, ticket), 'remember', request)


        if self.domains is None:
            self.domains = []
            self.domains.append(request.domain)

        return self.cookie.get_headers(value, domains=self.domains)

    def forget(self, request):
        """ A list of headers which will delete appropriate cookies."""

        debug = self.debug
        user = request.user

        if user.ticket:
            debug and self._log('forgetting user: %s, removing ticket: %s' % (user.id, user.ticket.ticket), 'forget', request)
            request.dbsession.delete(user.ticket)

        return self.cookie.get_headers('', max_age=0)

