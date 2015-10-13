from pytest import raises

from pyramid_authsanity.util import add_vary_callback

class TestAddVaryCallback(object):
    def _makeOne(self, *varies):
        return add_vary_callback(varies)

    def test_add_single_vary(self):
        cb = self._makeOne('cookie')
        response = DummyResponse()
        cb(None, response)

        assert len(response.vary) == 1
        assert 'cookie' in response.vary

    def test_add_multiple_vary(self):
        cb = self._makeOne('cookie', 'authorization')
        response = DummyResponse()
        cb(None, response)

        assert len(response.vary) == 2
        assert 'cookie' in response.vary
        assert 'authorization' in response.vary

    def test_add_multiple_existing(self):
        cb = self._makeOne('cookie')
        response = DummyResponse()
        response.vary = ['cookie']
        cb(None, response)

        assert len(response.vary) == 1
        assert 'cookie' in response.vary

def test_int_or_none_none():
    from pyramid_authsanity.util import int_or_none

    assert None == int_or_none(None)

def test_int_or_none_int():
    from pyramid_authsanity.util import int_or_none

    assert 1 == int_or_none(1)

def test_int_or_none_fail():
    from pyramid_authsanity.util import int_or_none

    with raises(ValueError):
        int_or_none('test')



class DummyResponse(object):
    vary = None
