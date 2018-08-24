#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
#
# Copyright 2018 Costas Tyfoxylos
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
import logging
import os
import shutil

from bootstrap import bootstrap
from configuration import BUILD_REQUIRED_FILES
from library import execute_command, clean_up, save_requirements

# This is the main prefix used for logging
LOGGER_BASENAME = '''_CI.build'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


def build():
    emojize = bootstrap()
    clean_up(('build', 'dist'))
    exit_code = execute_command('pipenv lock')
    success = not exit_code
    if success:
        LOGGER.info('Successfully created lock file %s %s',
                     emojize(':white_heavy_check_mark:'),
                     emojize(':thumbs_up:'))
    else:
        LOGGER.error('%s Errors creating lock file! %s',
                      emojize(':cross_mark:'),
                      emojize(':crying_face:'))
        raise SystemExit(1)
    save_requirements()
    for file in BUILD_REQUIRED_FILES:
        shutil.copy(file, os.path.join('pystrava', file))
    exit_code = execute_command('python setup.py sdist bdist_egg')
    success = not exit_code
    if success:
        LOGGER.info('%s Successfully built artifact %s',
                    emojize(':white_heavy_check_mark:'),
                    emojize(':thumbs_up:'))
    else:
        LOGGER.error('%s Errors building artifact! %s',
                     emojize(':cross_mark:'),
                     emojize(':crying_face:'))
    clean_up([os.path.join('pystrava', file)
              for file in BUILD_REQUIRED_FILES])
    return emojize if success else None


if __name__ == '__main__':
    raise SystemExit(not build())
