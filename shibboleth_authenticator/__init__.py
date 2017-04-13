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
#
# Example configuration:
# SHIBBOLETH_REMOTE_APPS = {
#   'hzdr': {
#       'saml_path': '...',
#       'mapping': {
#           'email': 'urn:oid:0.9.2342.19200300.100.1.3',
#           'fullname': 'urn:oid:2.16.840.1.113730.3.1.241',
#           'username': 'urn:oid:1.3.6.1.4.1.5923.1.1.1.6',
#       }
#       'id': '12345'
#   }
# }

"""
The shibbolet-authenticator module for Invenio offers Shibboleth/SAML support.

It uses the Python-SAML-Toolkit (https://github.com/onelogin/python3-saml).

"""


from __future__ import absolute_import, print_function

from .ext import ShibbolethAuthenticator
from .version import __version__

__all__ = (
    '__version__',
    'ShibbolethAuthenticator',
)
