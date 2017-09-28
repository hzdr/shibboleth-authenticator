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

"""Pytest configuration."""

from __future__ import absolute_import, print_function

import os
import shutil
import tempfile

import pytest
from flask import Flask
from flask_mail import Mail
from flask_menu import Menu as FlaskMenu
from invenio_accounts import InvenioAccounts
from invenio_db import InvenioDB, db
from invenio_userprofiles import InvenioUserProfiles, UserProfile
from invenio_userprofiles.views import blueprint_ui_init
from sqlalchemy_utils.functions import (create_database, database_exists,
                                        drop_database)

from shibboleth_authenticator import ShibbolethAuthenticator
from shibboleth_authenticator.views import blueprint


@pytest.fixture
def base_app(request):
    """Flask application fixture without ShibbolethAuthenticator init."""
    instance_path = tempfile.mkdtemp()
    base_app = Flask('testapp')
    base_app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        LOGIN_DISABLED=False,
        CACHE_TYPE='simple',
        SHIBBOLETH_REMOTE_APPS=dict(
            hzdr=dict(
                title='HZDR Shibboleth Authentication',
                saml_path='data/',
                mappings=dict(
                    email='email_mapping',
                    user_unique_id='id_mapping',
                    full_name='full_name_mapping',
                )
            )
        ),
        DEBUG=False,
        EMAIL_BACKEND='flask_email.backends.locmem.Mail',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_DATABASE_URI=os.getenv('SQLALCHEMY_DATABASE_URI',
                                          'sqlite://'),
        SERVER_NAME='localhost',
        SECRET_KEY='TEST',
        SECURITY_DEPRECATED_PASSWORD_SCHEMES=[],
        SECURITY_PASSWORD_HASH='plaintext',
        SECURITY_PASSWORD_SCHEMES=['plaintext'],
    )
    FlaskMenu(base_app)
    InvenioDB(base_app)
    InvenioAccounts(base_app)
    Mail(base_app)

    with base_app.app_context():
        if str(db.engine.url) != 'sqlite://' and \
           not database_exists(str(db.engine.url)):
                create_database(str(db.engine.url))
        db.create_all()

    def teardown():
        with base_app.app_context():
            db.session.close()
            if str(db.engine.url) != 'sqlite://':
                drop_database(str(db.engine.url))
                print('Path: ' + instance_path)
            shutil.rmtree(instance_path)

    request.addfinalizer(teardown)

    base_app.test_request_context().push()

    return base_app


@pytest.fixture
def app(base_app):
    """Flask application fixture."""
    ShibbolethAuthenticator(base_app)
    base_app.register_blueprint(blueprint)
    return base_app


@pytest.fixture
def userprofiles_app(app):
    """Configure userprofiles module."""
    app.config.update(
        USERPROFILES_EXTEND_SECURITY_FORMS=True,
        WTF_CSRF_ENABLED=True,
    )
    InvenioUserProfiles(app)
    app.register_blueprint(blueprint_ui_init)
    return app


@pytest.fixture
def models_fixture(app):
    """Flask app with example data used to test models."""
    with app.app_context():
        datastore = app.extensions['security'].datastore
        datastore.create_user(
            email='existing@hzdr.de',
            password='tester',
            active=True
        )
        datastore.create_user(
            email='test1@hzdr.de',
            password='tester',
            active=True
        )
        datastore.create_user(
            email='test2@hzdr.de',
            password='tester',
            active=True
        )
        datastore.commit()
    return app


@pytest.fixture
def views_fixture(base_app):
    """Flask application with example data used to test views."""
    with base_app.app_context():
        datastore = base_app.extensions['security'].datastore
        datastore.create_user(
            email='existing@hzdr.de',
            password='tester',
            active=True
        )
        datastore.create_user(
            email='test2@hzdr.de',
            password='tester',
            active=True
        )
        datastore.create_user(
            email='test3@hzdr.de',
            password='tester',
            active=True
        )
        datastore.commit()

    ShibbolethAuthenticator(base_app)
    base_app.register_blueprint(blueprint)
    return base_app


@pytest.fixture
def userprofiles_fixture(views_fixture):
    """Fixture with userprofiles module."""
    views_fixture.config.update(
        USERPROFILES_EXTEND_SECURITY_FORMS=True,
    )
    InvenioUserProfiles(views_fixture)
    views_fixture.register_blueprint(blueprint_ui_init)
    return views_fixture


@pytest.fixture
def user(userprofiles_app):
    """Create users."""
    with db.session.begin_nested():
        datastore = userprofiles_app.extensions['security'].datastore
        user1 = datastore.create_user(email='info@hzdr.de',
                                      password='tester', active=True)
        profile = UserProfile(username='nick', user=user1)
        db.session.add(profile)
    db.session.commit()
    return user1


@pytest.fixture
def valid_user_dict():
    """Fixture for remote app."""
    return dict(
        user=dict(
            email='test@hzdr.de',
            profile=dict(
                full_name='Test Tester',
                username='test123',
            ),
        ),
        external_id='test123',
        external_method='hzdr',
    )


@pytest.fixture
def valid_attributes():
    """Fixture for valid attributes."""
    return dict(
        email_mapping=['test@hzdr.de'],
        id_mapping=['test123'],
        full_name_mapping=['Test Tester'],
    )
