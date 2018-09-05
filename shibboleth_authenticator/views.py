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

"""Blueprint for handling Shibboleth callbacks."""

from __future__ import absolute_import, print_function

from flask import (Blueprint, abort, current_app, make_response, redirect,
                   request)
from flask_login import current_user, logout_user
from invenio_oauthclient.handlers import set_session_next_url
from itsdangerous import BadData, TimedJSONWebSignatureSerializer
from onelogin.saml2.auth import OneLogin_Saml2_Auth, OneLogin_Saml2_Error
from werkzeug.local import LocalProxy

from ._compat import _create_identifier, urlparse
from .handlers import authorized_signup_handler
from .utils import get_safe_redirect_target

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
    """
    Init SAML authentication for remote application.

    Args:
        req(dict):
        saml_path(str): The path to the configuration files for python3-saml.

    Returns:

    """
    auth = OneLogin_Saml2_Auth(
        req,
        custom_base_path=saml_path
    )
    return auth


def prepare_flask_request(request):
    """
    Prepare flask request.

    Args:
        request(flask.Request): The Flask request.
    Returns:
        dict: Returns dictionary used in :func:`init_saml_auth`.

    """
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


@blueprint.route('/login/<remote_app>/', methods=['GET', 'POST'])
def login(remote_app):
    """
    Redirect user to remote application for authentication.

    This function redirects the user to the IdP for authorization. After having
    authorized the IdP redirects the user back to this web application as
    configured in your ``saml_path``.

    Args:
        remote_app (str): The remote application key name.

    Returns:
        flask.Response: Return redirect response to IdP or abort in case
                        of failure.

    """
    if remote_app not in current_app.config['SHIBBOLETH_REMOTE_APPS']:
        return abort(404)
    conf = current_app.config['SHIBBOLETH_REMOTE_APPS'][remote_app]
    if 'saml_path' not in conf:
        return abort(500, 'Bad server configuration.')

    # Store next parameter in state token
    next_param = get_safe_redirect_target(arg='next')
    if not next_param:
        next_param = '/'
    state_token = serializer.dumps({
        'app': remote_app,
        'next': next_param,
        'sid': _create_identifier(),
    })

    saml_path = conf['saml_path']
    req = prepare_flask_request(request)
    try:
        auth = init_saml_auth(req, saml_path)
    except OneLogin_Saml2_Error:
        return abort(500)

    return redirect(auth.login(state_token))


@blueprint.route('/authorized/<remote_app>', methods=['GET', 'POST'])
def authorized(remote_app=None):
    """
    Authorize handler callback.

    This function is called when the user is redirected from the IdP to the
    web application. It handles the authorization.

    Args:
        remote_app (str): The remote application key name.

    Returns:
        flask.Response: Return redirect response or abort in case of failure.

    """
    if current_user.is_authenticated:
        logout_user()
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
    try:
        auth.process_response()
    except OneLogin_Saml2_Error:
        return abort(400)
    errors = auth.get_errors()
    if len(errors) == 0 and auth.is_authenticated():
        if 'RelayState' in request.form:
            # Get state token stored in RelayState
            state_token = request.form['RelayState']
            try:
                if not state_token:
                    raise ValueError
                # Check authenticity and integrity of state and decode the
                # values.
                state = serializer.loads(state_token)
                # Verify that state is for this session, app and that next
                # parameter have not been modified.
                if (state['sid'] != _create_identifier() or
                        state['app'] != remote_app):
                    raise ValueError
                # Store next url
                set_session_next_url(remote_app, state['next'])
            except (ValueError, BadData):
                if current_app.config.get('OAUTHCLIENT_STATE_ENABLED', True) \
                   or (not(current_app.debug or current_app.testing)):
                    return abort(400)
        return authorized_signup_handler(auth, remote_app)
    return abort(403)


@blueprint.route('/metadata/<remote_app>')
def metadata(remote_app):
    """
    Create remote application specific metadata xml for ServiceProvider.

    The metadata-XML response is created using the settings provided in the
    remote app's specific ``saml_path``.

    Args:
        remote_app (str): The remote application key name.
    Returns:
        flask.Response: The SP's metadata xml.

    """
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
