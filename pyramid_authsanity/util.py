
def add_vary_callback(vary_by):
    def vary_add(request, response):
        vary = set(response.vary if response.vary is not None else [])
        vary |= set(vary_by)
        response.vary = list(vary)
    return vary_add

def InnerFactory(cls):
    def inner(context, request):
        return cls(context, request)
    return inner
