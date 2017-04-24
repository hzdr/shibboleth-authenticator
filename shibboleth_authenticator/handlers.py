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

"""Handlers for shibboleth endpoints."""

from __future__ import absolute_import, print_function

from flask import (current_app, redirect, render_template, request, session,
                   url_for)
from flask_login import current_user
from invenio_db import db
from invenio_oauthclient.errors import OAuthError
from invenio_oauthclient.handlers import (get_session_next_url,
                                          oauth_error_handler, token_getter,
                                          token_session_key, token_setter)
from invenio_oauthclient.proxies import current_oauthclient
from invenio_oauthclient.signals import (account_setup_committed,
                                         account_setup_received)
from invenio_oauthclient.utils import (disable_csrf, fill_form,
                                       oauth_authenticate, oauth_get_user,
                                       oauth_register, registrationform_cls)
from werkzeug.local import LocalProxy

from .utils import get_account_info

_security = LocalProxy(lambda: current_app.extensions['security'])

_datastore = LocalProxy(lambda: _security.datastore)


#
# Handlers
#
@oauth_error_handler
def authorized_signup_handler(auth, remote=None, *args, **kwargs):
    """Handle sign-in/up functionality.

    :param remote: The remote application.
    :param resp: The response.
    :returns: Redirect response.
    """
    # Remove any previously stored auto register session key
    session.pop(token_session_key(auth.get_nameid()) + '_autoregister', None)

    # Sign-in/up user
    # ---------------
    if not current_user.is_authenticated:
        account_info = get_account_info(auth.get_attributes(), remote)

        user = oauth_get_user(
            'hzdr_shibboleth',
            account_info=account_info
        )
        if user is None:
            # Auto sign-up if user not found
            form_cls = registrationform_cls()
            form = fill_form(
                disable_csrf(form_cls()),
                account_info['user']
            )

            user = oauth_register(form)

            # if registration fails ...
            if user is None:
                return current_app.login_manager.unauthorized()

        # Authenticate user
        if not oauth_authenticate('hzdr_shibboleth', user,
                                  require_existing_link=False):
            return current_app.login_manager.unauthorized()

    db.session.commit()

    return redirect(url_for('zenodo_frontpage.index'))


def signup_handler(remote, *args, **kwargs):
    """Handle extra signup information.

    :param remote: The remote application.
    :returns: Redirect response or the template rendered.
    """
    # User already authenticated so move on
    if current_user.is_authenticated:
        return redirect('/')

    # Retrieve token from session
    oauth_token = token_getter(remote)
    if not oauth_token:
        return redirect('/')

    session_prefix = token_session_key(remote.name)

    # Test to see if this is coming from on authorized request
    if not session.get(session_prefix + '_autoregister', False):
        return redirect(url_for('.login', remote_app=remote.name))

    form = registrationform_cls()(request.form)

    if form.validate_on_submit():
        account_info = session.get(session_prefix + '_account_info')
        response = session.get(session_prefix + '_response')

        # Register user
        user = oauth_register(form)

        if user is None:
            raise OAuthError('Could not create user.', remote)

        # Remove session key
        session.pop(session_prefix + '_autoregister', None)

        # Link account and set session data
        token = token_setter(remote, oauth_token[0], secret=oauth_token[1],
                             user=user)
        handlers = current_oauthclient.signup_handlers[remote.name]

        if token is None:
            raise OAuthError('Could not create token for user.', remote)

        if not token.remote_account.extra_data:
            account_setup = handlers['setup'](token, response)
            account_setup_received.send(
                remote, token=token, response=response,
                account_setup=account_setup
            )
            # Registration has been finished
            db.session.commit()
            account_setup_committed.send(remote, token=token)
        else:
            # Registration has been finished
            db.session.commit()

        # Authenticate the user
        if not oauth_authenticate(remote.consumer_key, user,
                                  require_existing_link=False,
                                  remember=current_app.config[
                                      'OAUTHCLIENT_REMOTE_APPS']
                                  [remote.name].get('remember', False)):
            # Redirect the user after registration (which doesn't include the
            # activation), waiting for user to confirm his email.
            return redirect(url_for('security.login'))

        # Remove account info from session
        session.pop(session_prefix + '_account_info', None)
        session.pop(session_prefix + '_response', None)

        # Redirect to next
        next_url = get_session_next_url(remote.name)
        if next_url:
            return redirect(next_url)
        else:
            return redirect('/')

    # Pre-fill form
    account_info = session.get(session_prefix + '_account_info')
    if not form.is_submitted():
        form = fill_form(form, account_info['user'])

    return render_template(
        current_app.config['OAUTHCLIENT_SIGNUP_TEMPLATE'],
        form=form,
        remote=remote,
        app_title=current_app.config['OAUTHCLIENT_REMOTE_APPS'][
            remote.name].get('title', ''),
        app_description=current_app.config['OAUTHCLIENT_REMOTE_APPS'][
            remote.name].get('description', ''),
        app_icon=current_app.config['OAUTHCLIENT_REMOTE_APPS'][
            remote.name].get('icon', None),
    )
