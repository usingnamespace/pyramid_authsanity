import pytest

import pyramid.testing
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.interfaces import IAuthenticationPolicy

from zope.interface import Interface
from zope.interface.verify import (
        verifyClass,
        verifyObject
        )

def test_clean_principal_invalid():
    from pyramid_authsanity import _clean_principal
    from pyramid.security import Everyone

    ret = _clean_principal(Everyone)

    assert ret == None

def test_clean_principal_valid():
    from pyramid_authsanity import _clean_principal
    
    ret = _clean_principal('root')

    assert ret == 'root'

class TestAuthServicePolicyInterface(object):
    def test_verify(self):
        from pyramid_authsanity import AuthServicePolicy
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

        policy = AuthServicePolicy(debug=debug)
        policy._find_services = find_services
        return policy

    def _makeOneRequest(self):
        request = DummyRequest()
        request.registry = self.config.registry
        return request

    def test_find_services(self):
        policy = self._makeOne()
        request = self._makeOneRequest()
        
        (source, auth) = policy._find_services(request)

        assert source == None
        assert auth == None

class TestAuthServicePolicyIntegration(object):
    @pytest.fixture(autouse=True)
    def pyramid_config(self, request):
        from pyramid.interfaces import IDebugLogger
        self.config = pyramid.testing.setUp()
        self.config.include('pyramid_services')
        self.config.set_authorization_policy(ACLAuthorizationPolicy())
        self.logger = DummyLogger()
        self.config.registry.registerUtility(self.logger, IDebugLogger)

        def finish():
            del self.config
            pyramid.testing.tearDown()
        request.addfinalizer(finish)

    def _makeOne(self, debug=False, userid=None, ticket=None):
        from pyramid_authsanity import AuthServicePolicy
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
        from pyramid_authsanity import AuthServicePolicy
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
        self.config.register_service_factory(lambda x,y: 'Source', iface=IAuthSourceService)
        self.config.register_service_factory(lambda x,y: 'Auth', iface=IAuthService)

        policy = self._makeOne()
        request = self._makeOneRequest()

        (sourcesvc, authsvc) = policy._find_services(request)

        assert sourcesvc == 'Source'
        assert authsvc == 'Auth'

class DummyLogger(object):
    def debug(self, log):
        self.logentries.append(log)
    
    def __init__(self):
        self.logentries = []

class DummyRequest(object):
    domain = 'example.net'

    def __init__(self, environ=None, session=None, registry=None, cookie=None):
        self.environ = environ or {}
        self.session = session or {}
        self.registry = registry
        self.callbacks = []
        self.cookies = cookie or []
        self.context = None

    def add_response_callback(self, callback):
        self.callbacks.append(callback)


