import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()
except IOError:
    README = CHANGES = ''

requires = [
    'pyramid',
    'zope.interface',
    'pyramid_services>=0.3'
]

tests_require = requires + [
    'pytest',
    'coverage',
    'pytest-cov',
    ]

docs_require = requires + [
    'sphinx',
    'repoze.sphinx.autointerface',
    ]

setup(
    name='pyramid_authsanity',
    version='1.1.0',
    description='An auth policy for the Pyramid Web Framework with sane defaults.',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Pyramid',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    keywords='pyramid authorization policy',
    author='Bert JW Regeer',
    author_email='bertjw@regeer.org',
    url='https://github.com/usingnamespace/pyramid_authsanity',
    packages=find_packages('src', exclude=['tests']),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    extras_require={
        'testing': tests_require,
        'docs': docs_require,
    },
    entry_points={
    },
)
