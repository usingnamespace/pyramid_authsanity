==================
pyramid_authsanity
==================

An sane defaults auth policy for the `Pyramid Web Framework
<https://docs.pylonsproject.org/projects/pyramid>`__. that works with `Michael
Merickel's <http://michael.merickel.org>`__ absolutely fantastic
`pyramid_services <https://github.com/mmerickel/pyramid_services>`__ to provide
an easy to use authorization policy that incorporates web security best
practices.

Installation
============

Install from `PyPI <https://pypi.python.org/pyramid_authsanity>`__ using
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

