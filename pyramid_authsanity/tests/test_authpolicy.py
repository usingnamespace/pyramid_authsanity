import pytest

import pyramid.testing
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.interfaces import IAuthenticationPolicy

from zope.interface import implementer

from zope.interface.verify import (
    verifyClass,
    verifyObject
    )

from pyramid_authsanity.interfaces import (
    IAuthSourceService,
    IAuthService,
    )

def test_clean_principal_invalid():
    from pyramid_authsanity.policy import _clean_principal
    from pyramid.security import Everyone

    ret = _clean_principal(Everyone)

    assert ret is None

def test_clean_principal_valid():
    from pyramid_authsanity.policy import _clean_principal

    ret = _clean_principal('root')

    assert ret == 'root'

class TestAuthServicePolicyInterface(object):
    def test_verify(self):
        from pyramid_authsanity.policy import AuthServicePolicy
        assert verifyClass(IAuthenticationPolicy, AuthServicePolicy)
        assert verifyObject(IAuthenticationPolicy, AuthServicePolicy())

class TestAuthServicePolicy(object):
    @pytest.fixture(autouse=True)
    def pyramid_config(self, request):
        from pyramid.interfaces import IDebugLogger
        self.config = pyramid.testing.setUp()
        self.config.set_authorization_policy(ACLAuthorizationPolicy())
        self.logger = DummyLogger()
        self.config.registry.registerUtility(self.logger, IDebugLogger)

        def finish():
            del self.config
            pyramid.testing.tearDown()
        request.addfinalizer(finish)

    def _makeOne(self, debug=False, source=None, auth=None):
        from pyramid_authsanity import AuthServicePolicy
        def find_services(request):
            return (source, auth)

        def session_registered(request):
            return False

        policy = AuthServicePolicy(debug=debug)
        policy._find_services = find_services
        policy._session_registered = session_registered
        return policy

    def _makeOneRequest(self):
        request = DummyRequest()
        request.registry = self.config.registry
        return request

    def test_find_services(self):
        policy = self._makeOne()
        request = self._makeOneRequest()

        (source, auth) = policy._find_services(request)

        assert source is None
        assert auth is None

    def test_fake_source_ticket(self):
        context = None
        request = self._makeOneRequest()
        source = fake_source_init(None)(context, request)
        auth = fake_auth_init()(context, request)

        assert verifyObject(IAuthService, auth)
        assert verifyObject(IAuthSourceService, source)

    def test_valid_source_ticket(self):
        context = None
        request = self._makeOneRequest()
        source = fake_source_init(['test', 'valid'])(context, request)
        auth = fake_auth_init(fake_userid='test', valid_tickets=['valid'])(context, request)

        policy = self._makeOne(debug=True, source=source, auth=auth)

        authuserid = policy.authenticated_userid(request)
        assert authuserid == 'test'

    def test_invalid_source_ticket(self):
        context = None
        request = self._makeOneRequest()
        source = fake_source_init(['test', 'invalid'])(context, request)
        auth = fake_auth_init(fake_userid='test', valid_tickets=['valid'])(context, request)

        policy = self._makeOne(source=source, auth=auth)

        authuserid = policy.authenticated_userid(request)
        assert authuserid is None

    def test_bad_auth_service(self):
        context = None
        request = self._makeOneRequest()
        source = fake_source_init([None, None])(context, request)

        class BadAuth(object):
            def userid(self):
                raise ValueError('No ticket verified')

            def verify_ticket(self, principal, ticket):
                pass

        auth = BadAuth()

        policy = self._makeOne(source=source, auth=auth)

        authuserid = policy.authenticated_userid(request)
        assert authuserid is None

    def test_no_user_effective_principals(self):
        from pyramid.security import Everyone
        context = None
        request = self._makeOneRequest()
        source = fake_source_init([None, None])(context, request)
        auth = fake_auth_init()(context, request)

        policy = self._makeOne(source=source, auth=auth)

        groups = policy.effective_principals(request)

        assert [Everyone] == groups

    def test_user_bad_principal_effective_principals(self):
        from pyramid.security import Everyone
        context = None
        request = self._makeOneRequest()
        source = fake_source_init([Everyone, 'valid'])(context, request)
        auth = fake_auth_init(fake_userid=Everyone, valid_tickets=['valid'])(context, request)

        policy = self._makeOne(source=source, auth=auth)

        groups = policy.effective_principals(request)

        assert [Everyone] == groups

    def test_effective_principals(self):
        from pyramid.security import Everyone, Authenticated
        context = None
        request = self._makeOneRequest()
        source = fake_source_init(['test', 'valid'])(context, request)
        auth = fake_auth_init(fake_userid='test', valid_tickets=['valid'])(context, request)

        policy = self._makeOne(source=source, auth=auth)

        groups = policy.effective_principals(request)

        assert [Everyone, Authenticated, 'test'] == groups

    def test_remember(self):
        context = None
        request = self._makeOneRequest()
        source = fake_source_init([None, None])(context, request)
        auth = fake_auth_init(fake_userid='test')(context, request)

        policy = self._makeOne(source=source, auth=auth)

        headers = policy.remember(request, 'test')

        assert len(headers) == 0
        assert len(auth.valid_tickets) >= 1
        assert isinstance(source.value, list)
        assert len(source.value) == 2

    def test_forget(self):
        context = None
        request = self._makeOneRequest()
        source = fake_source_init(['test', 'valid'])(context, request)
        auth = fake_auth_init(fake_userid='test', valid_tickets=['valid'])(context, request)

        policy = self._makeOne(source=source, auth=auth)

        assert 'valid' in auth.valid_tickets

        headers = policy.forget(request)

        assert len(headers) == 0
        assert 'valid' not in auth.valid_tickets


class TestAuthServicePolicyIntegration(object):
    @pytest.fixture(autouse=True)
    def pyramid_config(self, request):
        from pyramid.interfaces import IDebugLogger, ISessionFactory
        self.config = pyramid.testing.setUp()
        self.config.registry.registerUtility(lambda: None, ISessionFactory)
        self.config.include('pyramid_services')
        self.config.set_authorization_policy(ACLAuthorizationPolicy())
        self.logger = DummyLogger()
        self.config.registry.registerUtility(self.logger, IDebugLogger)

        def finish():
            del self.config
            pyramid.testing.tearDown()
        request.addfinalizer(finish)

    def _makeOne(self, debug=False, source=None, auth=None):
        from pyramid_authsanity import AuthServicePolicy

        if source:
            self.config.register_service_factory(source, iface=IAuthSourceService)

        if auth:
            self.config.register_service_factory(auth, iface=IAuthService)

        return AuthServicePolicy(debug=debug)

    def _makeOneRequest(self):
        from pyramid_services import find_service
        from zope.interface.adapter import AdapterRegistry
        import types

        request = DummyRequest()
        request.find_service = types.MethodType(find_service, request)
        request.registry = self.config.registry
        request.service_cache = AdapterRegistry()

        return request

    def test_include_me(self):
        from pyramid_authsanity.policy import AuthServicePolicy
        self.config.include('pyramid_authsanity')
        self.config.commit()
        introspector = self.config.registry.introspector
        auth_policy = introspector.get('authentication policy', None)

        assert isinstance(auth_policy['policy'], AuthServicePolicy)

    def test_logging(self):
        policy = self._makeOne(debug=True)
        request = DummyRequest(registry=self.config.registry)
        policy._log('this message', 'test_logging', request)

        assert len(self.logger.logentries) >= 1

    def test_find_services(self):
        from pyramid_authsanity.interfaces import (IAuthSourceService, IAuthService)
        self.config.register_service_factory(lambda x, y: 'Source', iface=IAuthSourceService)
        self.config.register_service_factory(lambda x, y: 'Auth', iface=IAuthService)

        policy = self._makeOne()
        request = self._makeOneRequest()

        (sourcesvc, authsvc) = policy._find_services(request)

        assert sourcesvc == 'Source'
        assert authsvc == 'Auth'

    def test_valid_source_ticket(self):
        request = self._makeOneRequest()
        source = fake_source_init(['test', 'valid'])
        auth = fake_auth_init(fake_userid='test', valid_tickets=['valid'])

        policy = self._makeOne(debug=True, source=source, auth=auth)

        authuserid = policy.authenticated_userid(request)
        assert authuserid == 'test'

    def test_invalid_source_ticket(self):
        request = self._makeOneRequest()
        source = fake_source_init(['test', 'invalid'])
        auth = fake_auth_init(fake_userid='test', valid_tickets=['valid'])

        policy = self._makeOne(source=source, auth=auth)

        authuserid = policy.authenticated_userid(request)
        assert authuserid is None

    def test_bad_auth_service(self):
        request = self._makeOneRequest()
        source = fake_source_init([None, None])

        class BadAuth(object):
            def __init__(self, context, request):
                pass

            def userid(self):
                raise ValueError('No ticket verification')

            def verify_ticket(self, principal, ticket):
                pass

        policy = self._makeOne(source=source, auth=BadAuth)

        authuserid = policy.authenticated_userid(request)
        assert authuserid is None

    def test_no_user_effective_principals(self):
        from pyramid.security import Everyone
        request = self._makeOneRequest()
        source = fake_source_init([None, None])
        auth = fake_auth_init()

        policy = self._makeOne(source=source, auth=auth)

        groups = policy.effective_principals(request)

        assert [Everyone] == groups

    def test_user_bad_principal_effective_principals(self):
        from pyramid.security import Everyone
        request = self._makeOneRequest()
        source = fake_source_init([Everyone, 'valid'])
        auth = fake_auth_init(fake_userid=Everyone, valid_tickets=['valid'])

        policy = self._makeOne(source=source, auth=auth)

        groups = policy.effective_principals(request)

        assert [Everyone] == groups

    def test_effective_principals(self):
        from pyramid.security import Everyone, Authenticated
        request = self._makeOneRequest()
        source = fake_source_init(['test', 'valid'])
        auth = fake_auth_init(fake_userid='test', valid_tickets=['valid'])

        policy = self._makeOne(source=source, auth=auth)

        groups = policy.effective_principals(request)

        assert [Everyone, Authenticated, 'test'] == groups

    def test_remember(self):
        request = self._makeOneRequest()
        source = fake_source_init([None, None])
        auth = fake_auth_init(fake_userid='test')

        policy = self._makeOne(source=source, auth=auth)

        headers = policy.remember(request, 'test')

        authreq = request.find_service(IAuthService)

        assert len(headers) == 0
        assert len(authreq.valid_tickets) >= 1

    def test_remember_value_json_serializable(self):
        request = self._makeOneRequest()
        source = fake_source_init([None, None])
        auth = fake_auth_init(fake_userid='test')

        policy = self._makeOne(source=source, auth=auth)

        headers = policy.remember(request, 'test')

        authreq = request.find_service(IAuthService)
        sourcereq = request.find_service(IAuthSourceService)

        assert len(headers) == 0
        assert len(authreq.valid_tickets) >= 1
        import json

        assert json.dumps(sourcereq.value)

    def test_remember_same_user(self):
        request = self._makeOneRequest()
        source = fake_source_init(['test', 'valid_ticket'])
        auth = fake_auth_init(fake_userid='test', valid_tickets=['valid_ticket'])

        policy = self._makeOne(source=source, auth=auth)

        headers = policy.remember(request, 'test')

        authreq = request.find_service(IAuthService)

        assert len(headers) == 0
        assert len(authreq.valid_tickets) >= 1

    def test_forget(self):
        request = self._makeOneRequest()
        source = fake_source_init(['test', 'valid'])
        auth = fake_auth_init(fake_userid='test', valid_tickets=['valid'])

        policy = self._makeOne(source=source, auth=auth)

        authreq = request.find_service(IAuthService)

        assert 'valid' in authreq.valid_tickets

        headers = policy.forget(request)

        assert len(headers) == 0
        assert 'valid' not in authreq.valid_tickets

class DummyLogger(object):
    def debug(self, log):
        self.logentries.append(log)

    def __init__(self):
        self.logentries = []

class DummyRequest(object):
    domain = 'example.net'

    def __init__(self, environ=None, session=None, registry=None, cookie=None):
        class Session(dict):
            def invalidate(self):
                self.clear()
            
            def new_csrf_token(self):
                pass

        self.environ = environ or {}
        self.session = Session()
        self.session.update(session or {})
        self.registry = registry
        self.callbacks = []
        self.cookies = cookie or []
        self.context = None


    def add_response_callback(self, callback):
        self.callbacks.append(callback)

def fake_source_init(fake_value):
    @implementer(IAuthSourceService)
    class fake_source(object):
        vary = ['Cookie']
        def __init__(self, context, request):
            self.value = fake_value

        def get_value(self):
            return self.value if self.value else [None, None]

        def headers_remember(self, value):
            self.value = value
            return []

        def headers_forget(self):
            self.value = [None, None]
            return []

    return fake_source


def fake_auth_init(fake_userid=None, fake_groups=list(), valid_tickets=list()):
    @implementer(IAuthService)
    class fake_auth(object):

        def __init__(self, context, request):
            self.authcomplete = False
            self.ticketvalid = False
            self._userid = fake_userid
            self._groups = fake_groups
            self.valid_tickets = valid_tickets

        def userid(self):
            if not self.authcomplete:
                raise ValueError('No ticket verified.')

            if not self.ticketvalid:
                return None

            return self._userid

        def groups(self):
            return self._groups

        def verify_ticket(self, principal, ticket):
            self.authcomplete = True
            if principal == self._userid and ticket in self.valid_tickets:
                self.ticketvalid = True

        def add_ticket(self, principal, ticket):
            if ticket not in self.valid_tickets:
                self.valid_tickets.append(ticket)

        def remove_ticket(self, ticket):
            if ticket in self.valid_tickets:
                self.valid_tickets.remove(ticket)

    return fake_auth
