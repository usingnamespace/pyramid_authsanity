pyramid_authsanity
==================

pyramid_authsanity is an authentication policy for the `Pyramid Web Framework
<https://docs.pylonsproject.org/projects/pyramid>`__ that strives to make it
easier to write a secure authentication policy that follows web best practices.

- Uses tickets to allow sessions to be prematurely ended. Don't depend on the
  expiration of a cookie for example, instead have the ability to terminate
  sessions server side.
- Stops session fixation by automatically clearing the session upon
  login/logout. Sessions are also cleared if the new session is for a different
  userid than before.
- Automatically adds the Vary HTTP header if the authentication policy is used.

pyramid_authsanity uses `Michael Merickel's <http://michael.merickel.org>`__
absolutely fantastic `pyramid_services
<https://github.com/mmerickel/pyramid_services>`__ to allow an application
developer to easily plug in their own sources, and interact with their user
database.

API Documentation
=================

Reference material for every public API exposed by pyramid_authsanity:

.. toctree::
   :maxdepth: 1
   :glob:

   api/*

Narrative Documentation
=======================

Narrative documentation that describes how to use this library, with some
examples.

.. toctree::
   :maxdepth: 1

   narr/policy

Other Matters
=============

.. toctree::
   :maxdepth: 2

   faq
   license

.. toctree::
   :maxdepth: 2

