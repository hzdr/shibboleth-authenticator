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

.. code-block:: python

    {
        // If strict is True, then the Python Toolkit will reject unsigned
        // or unencrypted messages if it expects them to be signed or encrypted.
        // Also it will reject the messages if the SAML standard is not strictly
        // followed. Destination, NameId, Conditions ... are validated too.
        "strict": true,

        // Enable debug mode (outputs errors).
        "debug": true,

        // Service Provider Data that we are deploying.
        "sp": {
            // Identifier of the SP entity  (must be a URI)
            "entityId": "https://<sp_domain>/metadata/",
            // Specifies info about where and how the <AuthnResponse> message MUST be
            // returned to the requester, in this case our SP.
            "assertionConsumerService": {
                // URL Location where the <Response> from the IdP will be returned
                "url": "https://<sp_domain>/?acs",
                // SAML protocol binding to be used when returning the <Response>
                // message. OneLogin Toolkit supports this endpoint for the
                // HTTP-POST binding only.
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            },
            // Specifies info about where and how the <Logout Response> message MUST be
            // returned to the requester, in this case our SP.
            "singleLogoutService": {
                // URL Location where the <Response> from the IdP will be returned
                "url": "https://<sp_domain>/?sls",
                // SAML protocol binding to be used when returning the <Response>
                // message. OneLogin Toolkit supports the HTTP-Redirect binding
                // only for this endpoint.
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
            },
            // If you need to specify requested attributes, set a
            // attributeConsumingService. nameFormat, attributeValue and
            // friendlyName can be ommited
            "attributeConsumingService": {
                    "serviceName": "SP test",
                    "serviceDescription": "Test Service",
                    "requestedAttributes": [
                        {
                            "name": "",
                            "isRequired": false,
                            "nameFormat": "",
                            "friendlyName": "",
                            "attributeValue": []
                        }
                    ]
            },
            // Specifies the constraints on the name identifier to be used to
            // represent the requested subject.
            // Take a look on src/onelogin/saml2/constants.py to see the NameIdFormat that are supported.
            "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified",
            // Usually x509cert and privateKey of the SP are provided by files placed at
            // the certs folder. But we can also provide them with the following parameters
            "x509cert": "",
            "privateKey": ""
        },

        // Identity Provider Data that we want connected with our SP.
        "idp": {
            // Identifier of the IdP entity  (must be a URI)
            "entityId": "https://app.onelogin.com/saml/metadata/<onelogin_connector_id>",
            // SSO endpoint info of the IdP. (Authentication Request protocol)
            "singleSignOnService": {
                // URL Target of the IdP where the Authentication Request Message
                // will be sent.
                "url": "https://app.onelogin.com/trust/saml2/http-post/sso/<onelogin_connector_id>",
                // SAML protocol binding to be used when returning the <Response>
                // message. OneLogin Toolkit supports the HTTP-Redirect binding
                // only for this endpoint.
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
            },
            // SLO endpoint info of the IdP.
            "singleLogoutService": {
                // URL Location of the IdP where SLO Request will be sent.
                "url": "https://app.onelogin.com/trust/saml2/http-redirect/slo/<onelogin_connector_id>",
                // SAML protocol binding to be used when returning the <Response>
                // message. OneLogin Toolkit supports the HTTP-Redirect binding
                // only for this endpoint.
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
            },
            // Public x509 certificate of the IdP
            "x509cert": "<onelogin_connector_cert>"
            /*
             *  Instead of using the whole x509cert you can use a fingerprint in
             *  order to validate a SAMLResponse.
             *  (openssl x509 -noout -fingerprint -in "idp.crt" to generate it,
             *  or add for example the -sha256 , -sha384 or -sha512 parameter)
             *
             *  If a fingerprint is provided, then the certFingerprintAlgorithm is required in order to
             *  let the toolkit know which algorithm was used.
             Possible values: sha1, sha256, sha384 or sha512
             *  'sha1' is the default value.
             *
             *  Notice that if you want to validate any SAML Message sent by the HTTP-Redirect binding, you
             *  will need to provide the whole x509cert.
             */
            // "certFingerprint": "",
            // "certFingerprintAlgorithm": "sha1",
        }
    }

Extra or additional settings can be defined in ``advanced_settings.json``:

.. code-block:: python

    {
        // Security settings
        "security": {

            /** signatures and encryptions offered **/

            // Indicates that the nameID of the <samlp:logoutRequest> sent by this SP
            // will be encrypted.
            "nameIdEncrypted": false,

            // Indicates whether the <samlp:AuthnRequest> messages sent by this SP
            // will be signed.  [Metadata of the SP will offer this info]
            "authnRequestsSigned": false,

            // Indicates whether the <samlp:logoutRequest> messages sent by this SP
            // will be signed.
            "logoutRequestSigned": false,

            // Indicates whether the <samlp:logoutResponse> messages sent by this SP
            // will be signed.
            "logoutResponseSigned": false,

            /* Sign the Metadata
             false || true (use sp certs) || {
                                                "keyFileName": "metadata.key",
                                                "certFileName": "metadata.crt"
                                             }
            */
            "signMetadata": false,

            /** signatures and encryptions required **/

            // Indicates a requirement for the <samlp:Response>, <samlp:LogoutRequest>
            // and <samlp:LogoutResponse> elements received by this SP to be signed.
            "wantMessagesSigned": false,

            // Indicates a requirement for the <saml:Assertion> elements received by
            // this SP to be signed. [Metadata of the SP will offer this info]
            "wantAssertionsSigned": false,

            // Indicates a requirement for the <saml:Assertion>
            // elements received by this SP to be encrypted.
            "wantAssertionsEncrypted": false,

            // Indicates a requirement for the NameID element on the SAMLResponse
            // received by this SP to be present.
            "wantNameId": true,

            // Indicates a requirement for the NameID received by
            // this SP to be encrypted.
            "wantNameIdEncrypted": false,

            // Indicates a requirement for the AttributeStatement element
            "wantAttributeStatement": true,

            // Authentication context.
            // Set to false and no AuthContext will be sent in the AuthNRequest,
            // Set true or don't present thi parameter and you will get an AuthContext 'exact' 'urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport'
            // Set an array with the possible auth context values: array ('urn:oasis:names:tc:SAML:2.0:ac:classes:Password', 'urn:oasis:names:tc:SAML:2.0:ac:classes:X509'),
            "requestedAuthnContext": true,
            // Allows the authn comparison parameter to be set, defaults to 'exact' if the setting is not present.
            "requestedAuthnContextComparison": "exact",

            // In some environment you will need to set how long the published metadata of the Service Provider gonna be valid.
            // is possible to not set the 2 following parameters (or set to null) and default values will be set (2 days, 1 week)
            // Provide the desire TimeStamp, for example 2015-06-26T20:00:00Z
            "metadataValidUntil": null,
            // Provide the desire Duration, for example PT518400S (6 days)
            "metadataCacheDuration": null,

            // Algorithm that the toolkit will use on signing process. Options:
            //    'http://www.w3.org/2000/09/xmldsig#rsa-sha1'
            //    'http://www.w3.org/2000/09/xmldsig#dsa-sha1'
            //    'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256'
            //    'http://www.w3.org/2001/04/xmldsig-more#rsa-sha384'
            //    'http://www.w3.org/2001/04/xmldsig-more#rsa-sha512'
            "signatureAlgorithm": "http://www.w3.org/2000/09/xmldsig#rsa-sha1",

            // Algorithm that the toolkit will use on digest process. Options:
            //    'http://www.w3.org/2000/09/xmldsig#sha1'
            //    'http://www.w3.org/2001/04/xmlenc#sha256'
            //    'http://www.w3.org/2001/04/xmldsig-more#sha384'
            //    'http://www.w3.org/2001/04/xmlenc#sha512'
            'digestAlgorithm': "http://www.w3.org/2000/09/xmldsig#sha1"
        },

        // Contact information template, it is recommended to suply a
        // technical and support contacts.
        "contactPerson": {
            "technical": {
                "givenName": "technical_name",
                "emailAddress": "technical@example.com"
            },
            "support": {
                "givenName": "support_name",
                "emailAddress": "support@example.com"
            }
        },

        // Organization information template, the info in en_US lang is
        // recomended, add more if required.
        "organization": {
            "en-US": {
                "name": "sp_test",
                "displayname": "SP test",
                "url": "http://sp.example.com"
            }
        }
    }

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
