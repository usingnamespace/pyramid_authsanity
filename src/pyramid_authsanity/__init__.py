from pyramid.settings import (
    asbool,
    aslist,
    )

from .interfaces import (
    IAuthSourceService,
    )

from .policy import (
    AuthServicePolicy,
    )

from .sources import (
    CookieAuthSourceInitializer,
    HeaderAuthSourceInitializer,
    SessionAuthSourceInitializer,
    )

from .util import (
    int_or_none,
    kw_from_settings,
    )

default_settings = (
    ('source', str, ''),
    ('debug', asbool, False),
    ('cookie.cookie_name', str, 'auth'),
    ('cookie.max_age', int_or_none, None),
    ('cookie.httponly', asbool, True),
    ('cookie.path', str, '/'),
    ('cookie.domains', aslist, []),
    ('cookie.debug', asbool, False),
    ('session.value_key', str, 'sanity.'),
)


def init_cookie_source(config, settings):
    if 'authsanity.secret' not in settings:
        raise RuntimeError('authsanity.secret is required for cookie based storage')

    kw = kw_from_settings(settings, 'authsanity.cookie.')

    config.register_service_factory(
        CookieAuthSourceInitializer(
            settings['authsanity.secret'],
            **kw
        ),
        iface=IAuthSourceService
    )


def init_session_source(config, settings):
    kw = kw_from_settings(settings, 'authsanity.session.')

    config.register_service_factory(
        SessionAuthSourceInitializer(**kw),
        iface=IAuthSourceService
    )


def init_authorization_header_source(config, settings):
    if 'authsanity.secret' not in settings:
        raise RuntimeError(
            'authsanity.secret is required for Authorization header source'
        )

    kw = kw_from_settings(settings, 'authsanity.header.')

    config.register_service_factory(
        HeaderAuthSourceInitializer(
            settings['authsanity.secret'],
            **kw
        ),
        iface=IAuthSourceService
    )


default_sources = {
    'cookie': init_cookie_source,
    'session': init_session_source,
    'header': init_authorization_header_source,
}


# Stolen from pyramid_debugtoolbar
def parse_settings(settings):
    parsed = {}

    def populate(name, convert, default):
        name = '%s%s' % ('authsanity.', name)
        value = convert(settings.get(name, default))
        parsed[name] = value
    for name, convert, default in default_settings:
        populate(name, convert, default)
    return parsed


def includeme(config):
    # Go parse the settings
    settings = parse_settings(config.registry.settings)

    # Update the config
    config.registry.settings.update(settings)

    # include pyramid_services
    config.include('pyramid_services')

    if settings['authsanity.source'] in default_sources:
        default_sources[settings['authsanity.source']](config, config.registry.settings)

    config.set_authentication_policy(
        AuthServicePolicy(
            debug=settings['authsanity.debug']
        )
    )
