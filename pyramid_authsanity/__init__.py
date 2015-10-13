from .interfaces import (
    IAuthSourceService,
    IAuthService,
    )

from .policy import (
    AuthServicePolicy,
    NoAuthCompleted,
    )

def includeme(config):
    config.set_authentication_policy(AuthServicePolicy())
