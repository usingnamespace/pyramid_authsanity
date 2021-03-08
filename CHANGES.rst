2.0.0 (2021-03-07)
==================

- Remove support for Python 2, 3.4, and 3.5

- Updated to use new Pyramid 2.0 import locations, please use 1.1.0 if you want
  compatibility with lower versions of Pyramid.

1.1.0 (2017-11-29)
==================

- Add new Authorization header based authentication source

  This provides out of the box support for "Bearer" like tokens.

1.0.0 (2017-05-19)
==================

- Remove Python 2.6 support

- Fix a bug whereby the policy was storing a dict instead of a list in the
  source, which of course broke things subtly when actually using the policy.

- Send empty cookie when forgetting the authentication for the cookie source
