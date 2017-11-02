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

from helpers import check_csrf_disabled
from shibboleth_authenticator.utils import get_account_info


def test_accountinfo(valid_user_dict, valid_attributes, models_fixture):
    """Test get_account_info."""
    # Test valid result.
    res = get_account_info(valid_attributes, 'hzdr')
    assert res == valid_user_dict

    # Test invalid remote app.
    with pytest.raises(KeyError):
        res = get_account_info(valid_attributes, 'invalid')
