from .interfaces import (
        IAuthService,
        IAuthSourceService,
        )

def int_or_none(x):
    return int(x) if x != None else x

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
