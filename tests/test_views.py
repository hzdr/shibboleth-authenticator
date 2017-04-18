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

from flask import url_for


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
                                       'data/invalid/')
            )
        )
    )


def _valid_configuration(app):
    app.config['SHIBBOLETH_REMOTE_APPS'].update(
        dict(
            idp=dict(
                title='Test identity provider',
                saml_path=os.path.join(os.path.dirname(__file__),
                                       'data/valid/')
            )
        )
    )


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
