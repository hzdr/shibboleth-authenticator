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

"""
Module for Invenio that provides authentication via shibboleth.

The shibboleth-authenticator module for Invenio provides web authorization via
the Shibboleth single sign-on system and allows people to sign in using just
one identity to various systems run by federations of different organizations.

This module is basing on `invenio-oauthclient
<https://github.com/inveniosoftware/invenio-oauthclient>`_ and `python3-saml
<https://github.com/onelogin/python3-saml>`_. It supports multiple
Identity-Providers (IDPs) which can easily be configured via configuration
parameters.
"""


from __future__ import absolute_import, print_function

from .ext import ShibbolethAuthenticator
from .version import __version__

__all__ = (
    '__version__',
    'ShibbolethAuthenticator',
)
