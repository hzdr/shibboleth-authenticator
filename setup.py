# -*- coding: utf-8 -*-
#
# This file is part of the shibboleth-authenticator module for Invenio.
# Copyright (C) 2017  Helmholtz-Zentrum Dresden-Rossendorf
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Module for Invenio that provides authentication via Shibboleth."""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()
history = open('CHANGES.md').read()

tests_require = [
    'check-manifest>=0.35',
    'coverage>=4.0',
    'invenio-accounts>=1.0.0b12',
    'invenio-userprofiles>=1.0.0b2',
    'isort>=4.3.3',
    'mock>=1.3.0',
    'pydocstyle>=1.1.1',
    'pytest-cache>=1.0',
    'pytest-cov>=1.8.0',
    'pytest-pep8>=1.0.6',
    'pytest>=2.8.3',
    'sphinx_rtd_theme>=0.2.4',
]

setup_requires = [
    'pytest-runner>=2.6.2',
]

install_requires = [
    'Flask>=0.11.1',
    'Flask-Login>=0.3.2',
    'Flask-WTF>=0.13.1',
    'python3-saml>=1.4.0',
    'uritools>=1.0.1',
]

extras_require = {
    'docs': [
        'recommonmark>=0.4.0',
        'Sphinx>=1.5.1',
    ],
    'mysql': [
        'invenio-oauthclient[mysql]>=1.0.0b5',
    ],
    'postgresql': [
        'invenio-oauthclient[postgresql]>=1.0.0b5',
    ],
    'sqlite': [
        'invenio-oauthclient[sqlite]>=1.0.0b5',
    ],
    'tests': tests_require,
}
extras_require['all'] = []
for name, reqs in extras_require.items():
    if name in ('mysql', 'postgresql', 'sqlite'):
        continue
    extras_require['all'].extend(reqs)

packages = find_packages()

# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('shibboleth_authenticator', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='shibboleth-authenticator',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='invenio shibboleth authentication',
    license='GPLv3',
    author='HZDR',
    author_email='t.frust@hzdr.de',
    url='https://github.com/tobiasfrust/shibboleth-authenticator',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'invenio_base.apps': [
            'shibboleth_authenticator = '
            'shibboleth_authenticator.ext:ShibbolethAuthenticator',
        ],
        'invenio_base.blueprints': [
            'shibboleth_authenticator = '
            'shibboleth_authenticator.views:blueprint',
        ]
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Development Status :: 5 - Production/Stable',
    ]
)
