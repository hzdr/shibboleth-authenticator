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

from flask import (Blueprint, abort, current_app, make_response, redirect,
                   request)
from itsdangerous import TimedJSONWebSignatureSerializer
from onelogin.saml2.auth import OneLogin_Saml2_Auth, OneLogin_Saml2_Error
from werkzeug.local import LocalProxy

from .handlers import authorized_signup_handler

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


blueprint = Blueprint(
    'shibboleth_authenticator',
    __name__,
    url_prefix='/shibboleth',
)


serializer = LocalProxy(
    lambda: TimedJSONWebSignatureSerializer(
        current_app.config['SECRET_KEY'],
        expires_in=current_app.config['SHIBBOLETH_STATE_EXPIRES'],
    )
)


def init_saml_auth(req, saml_path):
    """Init SAML authentication for remote application."""
    auth = OneLogin_Saml2_Auth(
        req,
        custom_base_path=saml_path
    )
    return auth


def prepare_flask_request(request):
    """Prepare flask request."""
    url_data = urlparse(request.url)
    # If server is behind proxys or balancers use the HTTP_X_FORWARDED fields.
    return {
        'https': 'on' if request.scheme == 'https' else 'off',
        'http_host': request.host,
        'server_port': url_data.port,
        'script_name': request.path,
        'get_data': request.args.copy(),
        'X-Forwarded-for': '',
        'post_data': request.form.copy()
    }


@blueprint.route('/login/<remote_app>/')
def login(remote_app):
    """Send user to remote application for authentication."""
    if remote_app not in current_app.config['SHIBBOLETH_REMOTE_APPS']:
        return abort(404)
    conf = current_app.config['SHIBBOLETH_REMOTE_APPS'][remote_app]
    if 'saml_path' not in conf:
        return abort(500, 'Bad server configuration.')
    saml_path = conf['saml_path']
    req = prepare_flask_request(request)
    try:
        auth = init_saml_auth(req, saml_path)
    except OneLogin_Saml2_Error:
        return abort(500)

    return redirect(auth.login())


@blueprint.route('/authorized/<remote_app>')
def authorized(remote_app=None):
    """Authorize handler callback."""
    if remote_app not in current_app.config['SHIBBOLETH_REMOTE_APPS']:
        return abort(404)
    conf = current_app.config['SHIBBOLETH_REMOTE_APPS'][remote_app]
    if 'saml_path' not in conf:
        return abort(500, 'Bad server configuration.')
    req = prepare_flask_request(request)
    try:
        auth = init_saml_auth(req, conf['saml_path'])
    except OneLogin_Saml2_Error:
        return abort(500)
    errors = []
    auth.process_response()
    errors = auth.get_errors()
    if len(errors) == 0 and auth.is_authenticated():
        authorized_signup_handler(auth)
        return redirect('/')
    return redirect('/')


@blueprint.route('/metadata/<remote_app>')
def metadata(remote_app):
    """Create remote application specific metadata xml for ServiceProvider."""
    if remote_app not in current_app.config['SHIBBOLETH_REMOTE_APPS']:
        return abort(404)
    conf = current_app.config['SHIBBOLETH_REMOTE_APPS'][remote_app]
    if 'saml_path' not in conf:
        return abort(500, 'Bad server configuration.')
    req = prepare_flask_request(request)
    try:
        auth = init_saml_auth(req, conf['saml_path'])
    except OneLogin_Saml2_Error:
        return abort(500)

    settings = auth.get_settings()
    metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(metadata)

    if len(errors) == 0:
        resp = make_response(metadata, 200)
        resp.headers['Content-Type'] = 'text/xml'
    else:
        resp = make_response(', '.join(errors), 500)
    return resp
