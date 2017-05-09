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

Authorization Flow Overview
---------------------------

There generally exist two different roles. The Identity-Provider (IdP) and the
Service-Provider (SP). The IdPs supply user information, while SPs consume this
information and give access to secure content. The ShibbolethAuthenticator
module acts as a SP.

First of all, the client (SP) must be properly configured and registered in
your IdP. Once, the SP is successfully registered the autorization flow is
following:

.. figure:: img/sequence_saml.svg

   Sequence diagram of a successful authorization flow.

1. The user clicks "Sign in with IdP-Name (idp1)":

    .. code-block:: http

        GET /shibboleth/login/idp1 HTTP/1.1

    The *client* redirects the user to the IdP's *authorize URL*.

    .. code-block:: http

        HTTP/1.1 302 FOUND
        Location: https://app.onelogin.com/trust/saml2/http-post/
            sso/<onelogin_connector_id>?...

2. The IdP asks the user to sign in (if not already signed in).
3. The IdP aks the user to authorize or reject the SP's request for access.
4. If the user authorizes the request, the IdP redirects the user back to
   the client web application using the configured URL.

    .. code-block:: http

        HTTP/1.1 302 FOUND
        Location: https://localhost/shibboleth/authorized/idp1?...

5. If the user was authorized successfully the user can now access restricted
   ressources.

Usage
-----

1. Edit your configuration. Add ``shibboleth_authenticator`` to your packages.

2. Define your remote applications according to the configuration guide below.

"""


from __future__ import absolute_import, print_function

from .ext import ShibbolethAuthenticator
from .version import __version__

__all__ = (
    '__version__',
    'ShibbolethAuthenticator',
)
