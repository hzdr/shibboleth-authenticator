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
"""Test utils."""

from __future__ import absolute_import, print_function

import pytest
from invenio_oauthclient.utils import fill_form
from wtforms.fields.core import FormField

from shibboleth_authenticator.utils import (create_csrf_free_registrationform,
                                            get_account_info)


def _attributes():
    return dict(
        email_mapping=['test@hzdr.de'],
        id_mapping=['123456'],
        full_name_mapping=['Test Tester'],
    )


def test_accountinfo(valid_user_dict, valid_attributes, models_fixture):
    """Test get_account_info."""
    # Test valid result.
    res = get_account_info(valid_attributes, 'hzdr')
    assert res == valid_user_dict

    # Test invalid remote app.
    with pytest.raises(KeyError):
        res = get_account_info(valid_attributes, 'invalid')


def test_csrf_disable(userprofiles_app, valid_user_dict):
    """Test disabling of CSRF-Token."""
    app = userprofiles_app
    with app.test_request_context():
        form = create_csrf_free_registrationform()

        form = fill_form(
            form,
            valid_user_dict['user'],
        )

        import flask_wtf
        from pkg_resources import parse_version
        if parse_version(flask_wtf.__version__) >= parse_version("0.14.0"):
            assert form.meta.csrf is False
            assert 'csrf_token' not in form
            for f in form:
                if isinstance(f, FormField):
                    assert f.meta.csrf is False
                    assert 'csrf_token' not in f
        else:
            assert form.csrf_enabled is False
            for f in form:
                if isinstance(f, FormField):
                    assert f.csrf_enabled is False
        assert form.validate() is True
