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

"""Configuration variables for service provider.

========================== ===================================================
`SHIBBOLETH_REMOTE_APPS`   Dictionary of remote applications.
                           See example below. **Default:** ``{}``

`SHIBBOLETH_STATE_EXPIRES` Number of seconds after which the state token
                           expires. **Default:** ``OAUTHCLIENT_STATE_EXPIRES``.
========================== ===================================================

Each remote application must be defined in the ``SHIBBOLETH_REMOTE_APPS``
dictionary, where the keys are the application names and the values the
configuration parameters for the application.

.. code-block:: python

    SHIBBOLETH_REMOTE_APPS = dict(
        idp1=dict(
            # Configuration values for idp1
        ),
        idp2=dict(
            # Configuration values for idp2
        )
    )

The given application name (e.g. `idp1` or `idp2`) is used in the login
authorized and metadata endpoints:

- Login endpoint: ``/shibboleth/login/<remote_app>``
- Authorized endpoint: ``/shibboleth/authorized/<remote_app>``
- Metadata endpoint: ``/shibboleth/metadata/<remote_app>``

Remote application
^^^^^^^^^^^^^^^^^^
Configuration of a single remote application is a dictionary with the
following keys:

- ``title`` - Title of the remote application. Not in use so far.
- ``description`` - Short description of the remote application. Not in use so
  far.
- ``saml_path`` - This is the path, that will target the specific 'saml' folder
  of the remote application. Python3-saml requires it to load the settings
  files.
- ``mappings`` - This is a dictionary, that contains key-value pairs to map
  the response of the IDP to the keys required by shibboleth-authenticator.
  The required keys are: ``email``, ``fullname``, ``username``

Example:

.. code-block:: python

    SHIBBOLETH_REMOTE_APPS = dict(
        idp1=dict(
            title: '',
            description: '',
            saml_path='',
            mappings=dict(
                email='',
                full_name='',
                user_unique_id='',
            )
        )
    )

Configure python3-saml
^^^^^^^^^^^^^^^^^^^^^^

For using python3-saml you need to configure the Service Provider's (SP) and
the Identity Provider's (IDP) info. Futhermore, you can configure advanced
security issues like signatures and encryption.

To provide the settings information create a ``settings.json`` and an
``advanced_settings.json`` file and locate it in a folder. The path to this
folder needs to be passed via the ``saml_path`` parameter.

This is the ``settings.json`` file:

.. include:: json/settings.txt
    :literal:

Extra or additional settings can be defined in ``advanced_settings.json``:

.. include:: json/advanced_settings.txt
    :literal:

In the security section you can specify, how the SP will handle the messages
and assertions. Talk to the admin of the IdP and ask them what the IdP expects.

If your environment requires support for signing or encryption, add a ``certs``
folder to your ``saml_path``. This folder my contain the x509 certificate and
the private key that the SP will use.

- ``sp.crt`` - The public certificate of the SP
- ``sp.key`` - The private key of the SP.

For further information about the configuration of python3-saml have a look
into their `Documentation
<https://github.com/onelogin/python3-saml/blob/master/README.md>`_.
"""

SHIBBOLETH_REMOTE_APPS = {}
"""Configuration of remote applications."""

SHIBBOLETH_STATE_EXPIRES = 300
"""Number of seconds after which the state token expires."""
