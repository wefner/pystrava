#!/usr/bin/env python
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
from stravalib import Client
from .constants import User, HEADERS, SITE


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
        self._scope = scope
        self._callback = callback
        self._session = Session()
        self._session.headers.update(HEADERS)
        self._login_headers = {}

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

    def _post_session(self):
        login_form = self._get_login_details()
        session_response = self._session.post(url=f'{SITE}/session',
                                              data=login_form,
                                              headers=self._login_headers)
        return session_response

    def _accept_application(self):
        headers = self._login_headers
        post_session = self._post_session()
        auth_form = {'authenticity_token': self._get_csrf_token(post_session.text),
                     'write': 'on'}
        params = self.__populate_url_params()
        params.update({'redirect_uri': self._callback})
        auth_response = self._session.post(url=f'{SITE}/oauth/accept_application',
                                           params=params,
                                           data=auth_form,
                                           headers=headers.update({'Referer': self._authorize().url}),
                                           allow_redirects=False)
        return auth_response

    def _get_code(self):
        auth_response = self._accept_application()
        location_url = auth_response.headers.get('location')
        code = dict(parse_qsl(urlparse(location_url).query)).get('code')
        exchange_post = self._session.post(url=f'{SITE}/oauth/token',
                                           data={'code': code,
                                                 'client_id': self.user.client_id,
                                                 'client_secret': self.user.client_secret})
        return exchange_post

    @property
    def access_token(self):
        code_response = self._get_code().json()
        return code_response.get('access_token')

    @staticmethod
    def _get_csrf_token(html_page):
        soup = Bfs(html_page, 'html.parser')
        csrf_token = soup.find('meta',
                               {'name': 'csrf-token'}).attrs.get('content')
        return csrf_token


class Strava:
    def __new__(cls, client_id, client_secret, callback, scope, email, password):
        authenticated = StravaAuthenticator(client_id, client_secret, callback, scope, email, password)
        strava = Client(access_token=authenticated.access_token)
        return strava
