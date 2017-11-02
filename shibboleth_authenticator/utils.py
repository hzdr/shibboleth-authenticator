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

from flask import current_app
from werkzeug.local import LocalProxy
from wtforms.fields.core import FormField

_security = LocalProxy(lambda: current_app.extensions['security'])

_datastore = LocalProxy(lambda: _security.datastore)


def get_account_info(attributes, remote_app):
    """Return account info for remote user."""
    mappings = current_app.config['SHIBBOLETH_REMOTE_APPS'][
        remote_app]['mappings']
    email = attributes[mappings['email']][0]
    external_id = attributes[mappings['user_unique_id']][0]
    full_name = attributes[mappings['full_name']][0]

    return dict(
        user=dict(
            email=email,
            profile=dict(
                full_name=full_name,
                username=external_id.split('@')[0],
            ),
        ),
        external_id=external_id,
        external_method=remote_app,
    )
