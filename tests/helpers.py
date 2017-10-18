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

"""Test helpers."""

from inspect import isfunction

import six
from wtforms.fields.core import FormField


def check_redirect_location(resp, loc):
    """Check response redirect location."""
    assert resp._status_code == 302
    if isinstance(loc, six.string_types):
        assert resp.headers['Location'] == loc
    elif isfunction(loc):
        assert loc(resp.headers['Location'])


def check_csrf_disabled(form):
    """Check if csrf is disabled in form."""
    import flask_wtf
    from pkg_resources import parse_version
    if parse_version(flask_wtf.__version__) >= parse_version("0.14.0"):
        assert form.meta.csrf is False
        if hasattr(form, 'csrf_token'):
            assert not form.csrf_token
        for f in form:
            if isinstance(f, FormField):
                check_csrf_disabled(f)
    else:
        assert form.csrf_enabled is False
        for f in form:
            if isinstance(f, FormField):
                check_csrf_disabled(f)
