The authentication policy
=========================

This authentication policy has two moving pieces, they work together to provide
an easy to use authenitcation policy that provides more security by allowing
the server to terminate an active authentication session.

Source Service
~~~~~~~~~~~~~~

The first piece is called the authentication source service, this stores the
principal and a ticket. There are two provided source services:

cookie
------

This is the default source and stores the information in a JSON encoded cookie
that is signed using HMAC. This secures the information so long as the secret
key for the HMAC is not made public.

session
-------

This source stores the information required for the authentiation in the
Pyramid session, this requires that a session is available in the application
as `request.session`. Since there is no requirement for a Pyramid application
to have a registered session, pyramid_authsanity decided to not make this the
default.

Authentication Service
~~~~~~~~~~~~~~~~~~~~~~

The authentication service is defined by the user, the primary goal is to
verify that the principal and ticket are both still valid.
