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

"""Test cases for views."""

import os

import mock
from flask import url_for
from flask_login import current_user
from onelogin.saml2.auth import OneLogin_Saml2_Error

from helpers import check_redirect_location
from shibboleth_authenticator._compat import _create_identifier


def _invalid_configuration(app):
    app.config['SHIBBOLETH_REMOTE_APPS'].update(
        dict(
            idp=dict(
                title='Test identity provider'
            )
        )
    )


def _invalid__saml_configuration(app):
    app.config['SHIBBOLETH_REMOTE_APPS'].update(
        dict(
            idp=dict(
                title='Test identity provider',
                saml_path=os.path.join(os.path.dirname(__file__),
                                       'data', 'invalid')
            )
        )
    )


def _valid_configuration(app):
    app.config['SHIBBOLETH_REMOTE_APPS'].update(
        dict(
            idp=dict(
                title='Test identity provider',
                saml_path=os.path.join(os.path.dirname(__file__),
                                       'data', 'valid')
            )
        )
    )


def _authorized_valid_config(app):
    app.config['SHIBBOLETH_REMOTE_APPS'].update(
        dict(
            idp=dict(
                title='Test identity provider',
                saml_path=os.path.join(os.path.dirname(__file__),
                                       'data', 'settings'),
                mappings=dict(
                    email='mail',
                    full_name='sn',
                    user_unique_id='uid',
                )
            )
        )
    )
    app.config['OAUTHCLIENT_SESSION_KEY_PREFIX'] = 'prefix'


def patch_auth(request, path):
    """Patch init saml function."""
    raise OneLogin_Saml2_Error('Failed')


def _load_file(filename):
    """Load content of file."""
    filename = os.path.join(os.path.dirname(__file__), 'data', filename)
    if(os.path.exists(filename)):
        f = open(filename, 'r')
        content = f.read()
        f.close()
        return content


def test_login(views_fixture):
    """Test login view."""
    app = views_fixture
    with app.test_client() as client:
        # Invalid remote
        resp = client.get(
            url_for('shibboleth_authenticator.login', remote_app='invalid')
        )
        assert resp.status_code == 404

        # Invalid configuration
        _invalid_configuration(app)
        resp = client.get(
            url_for('shibboleth_authenticator.login', remote_app='idp')
        )
        assert resp.status_code == 500

        # Invalid configuration of python3-saml
        _invalid__saml_configuration(app)
        resp = client.get(
            url_for('shibboleth_authenticator.metadata', remote_app='idp')
        )
        assert resp.status_code == 500


@mock.patch(
    'shibboleth_authenticator.views.init_saml_auth',
    side_effect=patch_auth
)
def test_login_fail(mock_auth, views_fixture):
    """Test failing login view."""
    app = views_fixture
    with app.test_client() as client:
        _valid_configuration(app)
        resp = client.get(
            url_for('shibboleth_authenticator.login', remote_app='idp')
        )
        assert resp.status_code == 500


def test_redirect_uri(views_fixture):
    """Test redirect uri."""
    app = views_fixture
    with app.test_client() as client:
        # Test redirect
        _valid_configuration(app)
        resp = client.get(
            url_for('shibboleth_authenticator.login', remote_app='idp')
        )
        assert resp.status_code == 302


def test_authorized(views_fixture):
    """Test authorized view."""
    app = views_fixture

    with app.test_client() as client:
        # Invalid remote
        resp = client.get(
            url_for('shibboleth_authenticator.authorized',
                    remote_app='invalid')
        )
        assert resp.status_code == 404

        # Invalid configuration
        _invalid_configuration(app)
        resp = client.get(
            url_for('shibboleth_authenticator.authorized', remote_app='idp')
        )
        assert resp.status_code == 500

        # Invalid configuration of python3-saml
        _invalid__saml_configuration(app)
        resp = client.get(
            url_for('shibboleth_authenticator.authorized', remote_app='idp')
        )
        assert resp.status_code == 500

        # Valid configuration, no authorization response
        _valid_configuration(app)
        resp = client.get(
            url_for('shibboleth_authenticator.authorized', remote_app='idp')
        )
        assert resp.status_code == 400


@mock.patch('shibboleth_authenticator.handlers.oauth_register')
@mock.patch('shibboleth_authenticator.handlers.oauth_authenticate')
def test_failing_authorized1(mock_authenticate, mock_register, views_fixture):
    """Test authorized signup handler."""
    app = views_fixture
    with app.test_client() as client:
        _authorized_valid_config(app)
        mock_register.return_value = None
        resp = client.post(
            url_for('shibboleth_authenticator.authorized', remote_app='idp'),
            data=dict(SAMLResponse=_load_file('valid.xml.base64'))
        )
        assert resp.status_code == 302
        assert not current_user.is_authenticated


@mock.patch('shibboleth_authenticator.handlers.oauth_authenticate')
def test_failing_authorized2(mock_authenticate, views_fixture):
    """Test authorized signup handler."""
    app = views_fixture
    with app.test_client() as client:
        _authorized_valid_config(app)
        mock_authenticate.return_value = False
        resp = client.post(
            url_for('shibboleth_authenticator.authorized', remote_app='idp'),
            data=dict(SAMLResponse=_load_file('valid.xml.base64'))
        )
        assert resp.status_code == 302
        assert not current_user.is_authenticated


def test_valid_authorized(views_fixture):
    """Test authorized signup handler."""
    app = views_fixture
    with app.test_client() as client:
        _authorized_valid_config(app)
        resp = client.post(
            url_for('shibboleth_authenticator.authorized', remote_app='idp'),
            data=dict(SAMLResponse=_load_file('valid.xml.base64'))
        )
        assert resp.status_code == 302
        assert current_user.email == 'smartin@yaco.es'
        assert current_user.is_authenticated

        _authorized_valid_config(app)
        resp = client.post(
            url_for('shibboleth_authenticator.authorized', remote_app='idp'),
            data=dict(SAMLResponse=_load_file('expired.xml.base64'))
        )
        assert resp.status_code == 403
        assert not current_user.is_authenticated

        from shibboleth_authenticator.views import serializer

        # test valid request with next parameter
        next_url = '/test/redirect'
        state = serializer.dumps({
            'app': 'idp',
            'sid': _create_identifier(),
            'next': next_url,
        })
        resp = client.post(
            url_for('shibboleth_authenticator.authorized', remote_app='idp'),
            data=dict(
                SAMLResponse=_load_file('valid.xml.base64'),
                RelayState=state,
            )
        )
        check_redirect_location(resp, lambda x: x.endswith(next_url))
        assert current_user.email == 'smartin@yaco.es'
        assert current_user.is_authenticated

        # test invalid state token
        state = serializer.dumps({
            'app': 'idp',
            'sid': 'invalid',
            'next': next_url,
        })
        resp = client.post(
            url_for('shibboleth_authenticator.authorized', remote_app='idp'),
            data=dict(
                SAMLResponse=_load_file('valid.xml.base64'),
                RelayState=state,
            )
        )
        assert resp.status_code == 400

        resp = client.post(
            url_for('shibboleth_authenticator.authorized', remote_app='idp'),
            data=dict(
                SAMLResponse=_load_file('valid.xml.base64'),
                RelayState='',
            )
        )
        assert resp.status_code == 400


def test_valid_authorized_userprofiles(userprofiles_fixture):
    """Test authorized signup handler with userprofiles enabled."""
    app = userprofiles_fixture
    with app.test_client() as client:
        _authorized_valid_config(app)
        resp = client.post(
            url_for('shibboleth_authenticator.authorized', remote_app='idp'),
            data=dict(SAMLResponse=_load_file('valid.xml.base64'))
        )
        assert resp.status_code == 302
        assert current_user.email == 'smartin@yaco.es'
        assert current_user.is_authenticated

        _authorized_valid_config(app)
        resp = client.post(
            url_for('shibboleth_authenticator.authorized', remote_app='idp'),
            data=dict(SAMLResponse=_load_file('expired.xml.base64'))
        )
        assert resp.status_code == 403
        assert not current_user.is_authenticated

        from shibboleth_authenticator.views import serializer

        # test valid request with next parameter
        next_url = '/test/redirect'
        state = serializer.dumps({
            'app': 'idp',
            'sid': _create_identifier(),
            'next': next_url,
        })
        resp = client.post(
            url_for('shibboleth_authenticator.authorized', remote_app='idp'),
            data=dict(
                SAMLResponse=_load_file('valid.xml.base64'),
                RelayState=state,
            )
        )
        check_redirect_location(resp, lambda x: x.endswith(next_url))
        assert current_user.email == 'smartin@yaco.es'
        assert current_user.is_authenticated

        # test invalid state token
        state = serializer.dumps({
            'app': 'idp',
            'sid': 'invalid',
            'next': next_url,
        })
        resp = client.post(
            url_for('shibboleth_authenticator.authorized', remote_app='idp'),
            data=dict(
                SAMLResponse=_load_file('valid.xml.base64'),
                RelayState=state,
            )
        )
        assert resp.status_code == 400

        resp = client.post(
            url_for('shibboleth_authenticator.authorized', remote_app='idp'),
            data=dict(
                SAMLResponse=_load_file('valid.xml.base64'),
                RelayState='',
            )
        )
        assert resp.status_code == 400


@mock.patch('shibboleth_authenticator.views.len')
def test_metadata_fail(mock_len, views_fixture):
    """Test failing metadata view."""
    app = views_fixture
    mock_len.return_value = 1
    with app.test_client() as client:
        # Valid configuration
        _valid_configuration(app)
        resp = client.get(
            url_for('shibboleth_authenticator.metadata', remote_app='idp')
        )
        assert resp.status_code == 500


def test_metadata(views_fixture):
    """Test metadata view."""
    app = views_fixture
    with app.test_client() as client:
        # Invalid remote application
        resp = client.get(
            url_for('shibboleth_authenticator.metadata', remote_app='invalid')
        )
        assert resp.status_code == 404

        # Invalid configuration
        _invalid_configuration(app)
        resp = client.get(
            url_for('shibboleth_authenticator.metadata', remote_app='idp')
        )
        assert resp.status_code == 500

        # Valid configuration
        _valid_configuration(app)
        resp = client.get(
            url_for('shibboleth_authenticator.metadata', remote_app='idp')
        )
        assert resp.status_code == 200
        assert resp.headers['Content-Type'] in ['text/xml', 'application/xml']

        # Invalid configuration of python3-saml
        _invalid__saml_configuration(app)
        resp = client.get(
            url_for('shibboleth_authenticator.metadata', remote_app='idp')
        )
        assert resp.status_code == 500
