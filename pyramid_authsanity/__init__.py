import logging
log = logging.getLogger(__name__)

import string
import hashlib

from os import urandom

from zope.interface import implementer

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

    def __init__(self,
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

        self.domains = domains

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
        self.debug = debug

    def unauthenticated_userid(self, request):
        """ No support for the unauthenticated userid """
        return None

    def authenticated_userid(self, request):
        """ Return the authenticated userid or ``None``."""

        try:
            return request.state['auth']['userinfo'].id
        except:
            pass

        result = self.cookie.bind(request).get_value()

        if result:
            principal = result['principal']
            ticket = result['ticket']
            tokens = result['tokens']

            valid_ticket = find_user_ticket(request, principal, ticket, tokens)

        self.debug and self._log('Got result from cookie: %s' % (result,), 'authenticated_userid', request)
        return None

    def find_user_ticket(self, request, principal, ticket, tokens):
        """ Update the user service to a valid user id if the users ticket matches """

        if not ticket or not principal:
            return False

        ticket = UserTickets.find_ticket_userid(request.dbsession, ticket, principal)

        if ticket is None:
            self.debug and self._log('No ticket found', 'find_user_ticket', request)
            self.cookie.set_cookies(request.response, '', max_age=0)

        return ticket

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


    def remember(self, request, principal, tokens=None, **kw):
        """ Accepts the following kw args: ``max_age=<int-seconds>``

        Return a list of headers which will set appropriate cookies on
        the response.

        """

        debug = self.debug

        hashalg = 'sha256'
        digestmethod = lambda string=b'': hashlib.new(hashalg, string)

        value = {}
        value['principal'] = principal
        value['ticket'] = ticket = digestmethod(urandom(32)).hexdigest()
        value['tokens'] = tokens if tokens is not None else []

        user = request.dbsession.query(User).filter(User.email == principal).first()

        if user is None:
            raise ValueError('Invalid principal provided')

        debug and self._log('Remember user: %s, ticket: %s' % (user.email, value['ticket']), 'remember', request)

        user.tickets.append(UserTickets(ticket=ticket, remote_addr=remote_addr))

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

