#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: constants.py
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

from collections import namedtuple
from urllib.parse import urlparse

User = namedtuple('User', ['client_id',
                           'client_secret',
                           'email',
                           'password'])

Token = namedtuple('Token', ['access_token',
                             'token_type',
                             'expires_at',
                             'expires_in',
                             'refresh_token'])

SITE = 'https://www.strava.com'
HEADERS = {'DNT': '1', 'Host': urlparse(SITE).netloc}

INVALID_TOKEN_MSG = {"message": "Authorization Error",
                     "errors": [{"resource": "Athlete",
                                 "field":"access_token",
                                 "code":"invalid"}]}
