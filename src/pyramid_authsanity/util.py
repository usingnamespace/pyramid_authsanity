from pyramid.interfaces import (
    ISessionFactory,
    )

from .interfaces import (
    IAuthService,
    IAuthSourceService,
    )


def int_or_none(x):
    return int(x) if x is not None else x


def kw_from_settings(settings, from_prefix='authsanity.'):
    return {
        k.replace(from_prefix, ''): v
        for k, v in settings.items()
        if k.startswith(from_prefix)
    }


def add_vary_callback(vary_by):
    def vary_add(request, response):
        vary = set(response.vary if response.vary is not None else [])
        vary |= set(vary_by)
        response.vary = list(vary)
    return vary_add


def _find_services(request):
    sourcesvc = request.find_service(IAuthSourceService)
    authsvc = request.find_service(IAuthService)

    return (sourcesvc, authsvc)


def _session_registered(request):
    registry = request.registry
    factory = registry.queryUtility(ISessionFactory)

    return (False if factory is None else True)
