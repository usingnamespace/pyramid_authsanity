==================
pyramid_authsanity
==================

An auth policy for the `Pyramid Web Framework
<https://trypyramid.com>`_ with sane defaults that works with `Michael
Merickel's <http://michael.merickel.org>`_ absolutely fantastic
`pyramid_services <https://github.com/mmerickel/pyramid_services>`_.
Provides an easy to use authorization policy that incorporates web security
best practices.

Installation
============

Install from `PyPI <https://pypi.python.org/pypi/pyramid_authsanity>`_ using
``pip`` or ``easy_install`` inside a virtual environment.

::

  $ $VENV/bin/pip install pyramid_authsanity

Or install directly from source.

::

  $ git clone https://github.com/usingnamespace/pyramid_authsanity.git
  $ cd pyramid_authsanity
  $ $VENV/bin/pip install -e .

Setup
=====

Activate ``pyramid_authsanity`` by including it into your pyramid application.

::

  config.include('pyramid_authsanity')

