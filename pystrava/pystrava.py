#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: pystrava.py
#
# Copyright 2018 Oriol Fabregas
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#

"""
Main code for pystrava

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import logging
from requests import Session
from bs4 import BeautifulSoup as Bfs
from urllib.parse import quote, parse_qsl, urlparse
from copy import copy
from stravalib import Client as OriginalStrava
from constants import User, Token, HEADERS, SITE, INVALID_TOKEN_MSG


__author__ = '''Oriol Fabregas <fabregas.oriol@gmail.com>'''
__docformat__ = '''google'''
__date__ = '''2018-08-22'''
__copyright__ = '''Copyright 2018, Oriol Fabregas'''
__credits__ = ["Oriol Fabregas"]
__license__ = '''MIT'''
__maintainer__ = '''Oriol Fabregas'''
__email__ = '''<fabregas.oriol@gmail.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".


# This is the main prefix used for logging
LOGGER_BASENAME = '''pystrava'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


class StravaAuthenticator:
    def __init__(self, client_id, client_secret, callback, scope, email, password):
        self._logger = logging.getLogger('{base}.{suffix}'
                                         .format(base=LOGGER_BASENAME,
                                                 suffix=self.__class__.__name__)
                                         )
        self.user = User(client_id, client_secret, email, password)
        self._token = None
        self._scope = scope
        self._callback = callback
        self._session = Session()
        self._session.headers.update(HEADERS)
        self._login_headers = {}
        self._authenticate()

    def _authenticate(self):
        self._authorize()
        response = self._accept_application()
        self._token = self._exchange_token(response)
        self._monkey_patch_session()
        return True

    def __populate_url_params(self):
        params = {'client_id': self.user.client_id,
                  'redirect_uri': quote(self._callback, safe=''),
                  'approval_prompt': 'auto',
                  'response_type': 'code',
                  'scope': self._scope}
        return params

    def _authorize(self):
        authorize_response = self._session.get(url=f'{SITE}/oauth/authorize',
                                               params=self.__populate_url_params())
        return authorize_response

    def _get_login_details(self):
        login_url = f'{SITE}/login'
        login_response = self._session.get(login_url)
        login_form = {
            'authenticity_token': self._get_csrf_token(login_response.text),
            'email': self.user.email,
            'password': self.user.password,
            'utf8': '✓'}
        self._login_headers = copy(self._session.headers)
        self._login_headers.update({'Referer': login_url})
        return login_form

    def _login_session(self):
        login_form = self._get_login_details()
        session_response = self._session.post(url=f'{SITE}/session',
                                              data=login_form,
                                              headers=self._login_headers)
        return session_response

    @staticmethod
    def _generate_auth_scope(scopes):
        scope = {scope: 'on' for scope in scopes.split(',')}
        return scope

    def _accept_application(self):
        headers = self._login_headers
        login_session = self._login_session()
        auth_form = {'authenticity_token': self._get_csrf_token(login_session.text)}
        auth_form.update(self._generate_auth_scope(self._scope))
        params = self.__populate_url_params()
        params.update({'redirect_uri': self._callback})
        auth_response = self._session.post(url=f'{SITE}/oauth/accept_application',
                                           params=params,
                                           data=auth_form,
                                           headers=headers.update(
                                               {'Referer': self._authorize().url}),
                                           allow_redirects=False)
        return auth_response

    def _exchange_token(self, response):
        location_url = response.headers.get('location')
        code = dict(parse_qsl(urlparse(location_url).query)).get('code')
        payload = {'code': code,
                   'grant_type': 'authorization_code',
                   'client_id': self.user.client_id,
                   'client_secret': self.user.client_secret}
        return self._retrieve_token(self._session, payload)

    @staticmethod
    def _retrieve_token(session, payload):
        response = session.post(url=f'{SITE}/oauth/token',
                                data=payload)
        tokens = response.json()
        if not tokens.get('refresh_token'):
            tokens.update({'refresh_token': session.token.refresh_token})
        token_values = [tokens.get(key) for key in Token._fields]
        if not all(token_values):
            LOGGER.exception(response.content)
            raise ValueError('Incomplete token response received. '
                             'Got: {}'.format(response.json()))
        return Token(*token_values)

    @staticmethod
    def _renew_token(session, user, token):
        payload = {'grant_type': 'refresh_token',
                   'client_id': user.client_id,
                   'client_secret': user.client_secret,
                   'refresh_token': token.refresh_token}
        LOGGER.info(f"Refreshing token with {token.refresh_token}")
        return StravaAuthenticator._retrieve_token(session, payload)

    def _monkey_patch_session(self):
        """
        Gets original request method and overrides it with the patched one
        It also sets Token and User namedtuples as well as the renew token
        method as session attributes.
        :return: Response instance
        """
        self._session.original_request = self._session.request
        self._session.token = self.token
        self._session.user = self.user
        self._session.renew_token = self._renew_token
        self._session.request = self._patched_request

    def _patched_request(self, method, url, **kwargs):
        self._logger.info(('Using patched request for method {method}, '
                            'url {url}').format(method=method, url=url))
        response = self._session.original_request(method, url, **kwargs)
        if response.status_code == 401 and response.json() == INVALID_TOKEN_MSG:
            self._logger.warning('Expired token detected, trying to refresh!')
            self._session.token = self._session.renew_token(self._session,
                                                            self.user,
                                                            self.token)
            kwargs.update({'params':
                          {'access_token': self._session.token.access_token}})
            response = self._session.original_request(method, url, **kwargs)
        return response

    @property
    def token(self):
        return self._token

    @staticmethod
    def _get_csrf_token(html_page):
        soup = Bfs(html_page, 'html.parser')
        csrf_token = soup.find('meta',
                               {'name': 'csrf-token'}).attrs.get('content')
        return csrf_token


class Strava:
    def __new__(cls, client_id, client_secret, callback, scope, email, password):
        authenticated = StravaAuthenticator(client_id, client_secret, callback, scope, email, password)
        strava_client = OriginalStrava(access_token=authenticated.token.access_token,
                                       requests_session=authenticated._session)
        return strava_client
