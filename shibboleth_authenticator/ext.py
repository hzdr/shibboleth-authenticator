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

"""Module that adds shibboleth authentication to Invenio platform."""


from __future__ import absolute_import, print_function

from . import config


class ShibbolethAuthenticator(object):
    """Shibboleth extension for Invenio."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.state = self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions['shibboleth-authenticator'] = self

    @staticmethod
    def init_config(app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith('SHIBBOLETH_'):
                app.config.setdefault(k, getattr(config, k))
