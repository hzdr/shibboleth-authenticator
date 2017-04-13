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

"""Utility methods to help find, authenticate or register a remote user."""

from __future__ import absolute_import, print_function

import json

from flask import current_app
from invenio_accounts.models import User
from invenio_oauthclient.models import UserIdentity
from invenio_oauthclient.utils import _get_external_id
from werkzeug.local import LocalProxy

_security = LocalProxy(lambda: current_app.extensions['security'])

_datastore = LocalProxy(lambda: _security.datastore)


def get_account_info(attributes):
    """Return account info for remote user."""
    return dict(
        user=dict(
            email=attributes[current_app.config['HZDR_EMAIL_ID']][0],
            profile=dict(
                full_name=attributes[current_app.config[
                    'HZDR_FULLNAME_ID']][0],
                username=attributes[
                    current_app.config[
                        'HZDR_USER_UNIQUE_ID']][0].split('@')[0],
            ),
        ),
        external_id=attributes[current_app.config['HZDR_USER_UNIQUE_ID']][0],
        external_method=current_app.config['HZDR_EXTERNAL_METHOD'],
    )


def _get_email(account_info):
    email = account_info[current_app.config['HZDR_EMAIL_ID']][0]
    return email


def oauth_get_user(client_id, account_info):
    """Retrieve user object for the given request."""
    if account_info:
        external_id = _get_external_id(account_info)
        current_app.logger.exception(json.dumps(external_id, indent=3))
        if external_id:
            user_identity = UserIdentity.query.filter_by(
                id=external_id['id'], method=external_id['method']).first()
            if user_identity:
                return user_identity.user
            email = _get_email(account_info)
            if email:
                return User.query.filter_by(email=email).one_or_none()
    return None
