import sys

import pytest

from collections import Iterable

from pyramid_authsanity.interfaces import IAuthSourceService
from pyramid_authsanity import sources

from zope.interface.verify import verifyObject

class _TestAuthSource(object):
    def test_verify_object(self):
        assert verifyObject(IAuthSourceService, self._makeOne())

    def test_get_value(self):
        source = self._makeOne()
        val = source.get_value()

        assert val == [None, None]

    def test_headers_remember(self):
        source = self._makeOne()
        headers = source.headers_remember("test")

        assert isinstance(headers, Iterable)

    def test_headers_forget(self):
        source = self._makeOne()
        headers = source.headers_forget()

        assert isinstance(headers, Iterable)


class TestSessionAuthSource(_TestAuthSource):
    def _makeOne(self, request=None):
        obj = sources.SessionAuthSourceInitializer()

        if request is None:
            request = DummyRequest()

        return obj(None, request)

    def test_remember(self):
        request = DummyRequest()
        source = self._makeOne(request=request)
        source.headers_remember("test")

        assert request.session['sanity.value'] == "test"

    def test_forget(self):
        request = DummyRequest()
        request.session['sanity.value'] = "test"
        source = self._makeOne(request=request)
        source.headers_forget()

        assert 'sanity.value' not in request.session

    def test_get_value_from_session(self):
        request = DummyRequest()
        request.session['sanity.value'] = "test"
        source = self._makeOne(request=request)
        val = source.get_value()

        assert val == "test"

    def test_get_previous_value_after_remember(self):
        request = DummyRequest()
        source = self._makeOne(request=request)
        val = source.get_value()

        assert val == [None, None]

        source.headers_remember("test")

        val2 = source.get_value()

        assert val2 == [None, None]
        assert request.session['sanity.value'] == "test"

class TestCookieAuthSource(_TestAuthSource):
    def _makeOne(self, request=None):
        obj = sources.CookieAuthSourceInitializer('seekrit')

        if request is None:
            request = DummyRequest()

        return obj(None, request)

    def test_get_header_remember(self):
        source = self._makeOne()
        headers = source.headers_remember("test")

        assert isinstance(headers, Iterable)

        for h in headers:
            assert 'auth' in h[1]

    @pytest.mark.skipif(
        sys.version_info < (3, 0),
        reason="json.dumps() doesn't like binary data on Python 3.x"
    )
    def test_get_header_remember_binary(self):
        source = self._makeOne()
        with pytest.raises(TypeError):
            source.headers_remember(b"test")

    def test_get_header_forget(self):
        source = self._makeOne()
        headers = source.headers_forget()

        assert isinstance(headers, Iterable)

        # Should set an empty cookie
        for h in headers:
            assert h[1].startswith("auth=;")

    def test_get_value_cookie(self):
        request = DummyRequest()
        request.cookies['auth'] = "JgEICiZyfFFc3Qcx5O84h4u8NSZIi51xVMYs_HyP94BO1aXGZpME_LJ1UZgfdAMJDoaGaLCt_y-x6FSBh3ZKDyJ0ZXN0Ig"
        source = self._makeOne(request=request)
        val = source.get_value()

        assert val == "test"

    def test_get_value_bad_cookie(self):
        request = DummyRequest()
        request.cookies['auth'] = "jxxxxxxxfFFc3Qcx5O84h4u8NSZIi51xVMYs_HyP94BO1aXGZpME_LJ1UZgfdAMJDoaGaLCt_y-x6FSBh3ZKDyJ0ZXN0Ig"
        source = self._makeOne(request=request)
        val = source.get_value()

        assert val == [None, None]

    def test_get_value_empty_cookie(self):
        request = DummyRequest()
        request.cookies['auth'] = ""
        source = self._makeOne(request=request)
        val = source.get_value()

        assert val == [None, None]

    def test_round_trip_cookie(self):
        source1 = self._makeOne()
        headers1 = source1.headers_remember(['user1', 'ticket1'])

        assert isinstance(headers1, Iterable)
        assert len(headers1) == 1

        set_cookie = headers1[0][1]
        authpart = set_cookie.split(' ')[0]
        (name, cookie) = authpart.split('=')

        assert name == "auth"

        request = DummyRequest()
        request.cookies[name] = cookie[:-1]

        source2 = self._makeOne(request=request)
        val = source2.get_value()

        assert val == ['user1', 'ticket1']

class TestHeaderAuthSource(_TestAuthSource):
    def _makeOne(self, request=None):
        obj = sources.HeaderAuthSourceInitializer('seekrit')

        if request is None:
            request = DummyRequest()

        return obj(None, request)

    def test_get_header_remember(self):
        source = self._makeOne()
        headers = source.headers_remember("test")

        assert isinstance(headers, Iterable)
        assert len(headers) >= 1

        for h in headers:
            assert 'Authorization' in h[0]

    @pytest.mark.skipif(
        sys.version_info < (3, 0),
        reason="json.dumps() doesn't like binary data on Python 3.x"
    )
    def test_get_header_remember_binary(self):
        source = self._makeOne()
        with pytest.raises(TypeError):
            source.headers_remember(b"test")

    def test_get_header_forget(self):
        source = self._makeOne()
        headers = source.headers_forget()

        assert isinstance(headers, Iterable)
        assert len(headers) == 0

    def test_get_value_bad_authorization(self):
        request = DummyRequest()
        request.authorization = ('Bearer', 'thisisinvalid')
        source = self._makeOne(request=request)
        val = source.get_value()

        assert val == [None, None]

    def test_get_value_authorization(self):
        request = DummyRequest()
        request.authorization = ('Bearer', 'zASow9lpNp6cr7FirG4kV6vQym8i75kLPZ7orcPMaemV4iaf92P-DTR0om_h0trImTEOXyv514obhbcB-3fvKyJ0ZXN0Ig')
        source = self._makeOne(request=request)
        val = source.get_value()

        assert val == "test"


class DummyRequest(object):
    def __init__(self):
        self.session = dict()
        self.domain = 'example.net'
        self.cookies = dict()
        self.authorization = None
