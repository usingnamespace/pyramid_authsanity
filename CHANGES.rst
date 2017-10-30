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
